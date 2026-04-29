# backend/app/routes/orders.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Order, Conversation, Message, Character, ChatSession
from app.schemas import (
    OrderCreate, OrderStatusUpdate,
    OrderResponse, OrderDetailResponse,
    ConversationDetailResponse, MessageResponse,
)
from app.models.conversation import generate_uuid, now_utc

router = APIRouter(prefix="/api", tags=["orders"])
logger = logging.getLogger(__name__)


# ==================== 헬퍼 함수 ====================

def _get_character_name_for_order(order: Order, db: Session) -> str | None:
    """주문에 연결된 캐릭터봇 이름 조회 (Message.session_id → ChatSession → Character)"""
    result = (
        db.query(Character.name)
        .join(ChatSession, ChatSession.character_id == Character.id)
        .join(Message, Message.session_id == ChatSession.id)
        .filter(
            Message.conversation_id == order.conversation_id,
            Message.session_id.isnot(None),
        )
        .first()
    )
    return result[0] if result else None


def _build_order_response(order: Order, conversation_title: str, character_name: str | None = None) -> OrderResponse:
    """Order ORM 객체 → OrderResponse 변환 헬퍼 (중복 제거)"""
    return OrderResponse(
        id=order.id,
        conversation_id=order.conversation_id,
        conversation_title=conversation_title,
        character_name=character_name,
        status=order.status,
        quantity=order.quantity,
        cover_style=order.cover_style,
        memo=order.memo or "",
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


# ==================== 주문 CRUD ====================

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: OrderCreate,
    db: Session = Depends(get_db),
):
    """주문 생성"""
    # 대화방 존재 확인
    conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")

    # 동일 대화방에 대한 중복 주문 확인
    existing = db.query(Order).filter(
        Order.conversation_id == request.conversation_id,
        Order.status.in_(["접수", "제작중"]),
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 해당 대화방에 대한 주문이 존재합니다.")

    order = Order(
        id=generate_uuid(),
        conversation_id=request.conversation_id,
        status="접수",
        quantity=request.quantity,
        cover_style=request.cover_style,
        memo=request.memo,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return _build_order_response(order, conv.title, None)


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(db: Session = Depends(get_db)):
    """주문 목록 조회 (최신순)"""
    orders = (
        db.query(Order)
        .order_by(desc(Order.created_at))
        .all()
    )

    # 모든 관련 Conversation을 단일 쿼리로 조회하여 N+1 문제 해결
    conv_ids = [o.conversation_id for o in orders]
    conv_map = {}
    if conv_ids:
        convs = db.query(Conversation).filter(Conversation.id.in_(conv_ids)).all()
        conv_map = {c.id: c for c in convs}

    # 캐릭터 이름 한 번에 조회 (N+1 방지)
    char_map = {}
    if conv_ids:
        char_rows = (
            db.query(Message.conversation_id, Character.name)
            .join(ChatSession, ChatSession.id == Message.session_id)
            .join(Character, Character.id == ChatSession.character_id)
            .filter(
                Message.conversation_id.in_(conv_ids),
                Message.session_id.isnot(None),
            )
            .distinct()
            .all()
        )
        for conv_id, char_name in char_rows:
            if conv_id not in char_map:
                char_map[conv_id] = char_name

    result = []
    for order in orders:
        conv = conv_map.get(order.conversation_id)
        char_name = char_map.get(order.conversation_id)
        result.append(_build_order_response(order, conv.title if conv else "(삭제된 대화)", char_name))
    return result


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """주문 상세 조회 (대화 내용 포함)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    conv = db.query(Conversation).filter(Conversation.id == order.conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="연관된 대화방을 찾을 수 없습니다.")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .all()
    )

    character_name = _get_character_name_for_order(order, db)

    return OrderDetailResponse(
        id=order.id,
        conversation_id=order.conversation_id,
        conversation_title=conv.title,
        character_name=character_name,
        status=order.status,
        quantity=order.quantity,
        cover_style=order.cover_style,
        memo=order.memo or "",
        created_at=order.created_at,
        updated_at=order.updated_at,
        conversation=ConversationDetailResponse(
            id=conv.id,
            title=conv.title,
            provider="",
            model="",
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[
                MessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at,
                )
                for m in messages
            ],
        ),
    )


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    주문 상태 변경 (상태 머신 검증 포함)

    상태 전이 규칙:
      - 접수 → 제작중 (정상)
      - 접수 → 취소 (정상)
      - 제작중 → 완료 (정상)
      - 제작중 → 접수 (정상, 제작 취소)
      - 제작중 → 취소 (거부)
      - 완료 → 취소 (거부)
      - 취소 → * (거부)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    # 상태 전이 검증
    valid_transitions = {
        "접수": ["제작중", "취소"],
        "제작중": ["완료", "접수"],
        "완료": [],
        "취소": [],
    }

    if request.status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"'{order.status}' 상태에서 '{request.status}' 상태로 변경할 수 없습니다."
        )

    order.status = request.status
    order.updated_at = now_utc()
    db.commit()
    db.refresh(order)

    conv = db.query(Conversation).filter(Conversation.id == order.conversation_id).first()

    char_name = _get_character_name_for_order(order, db)
    return _build_order_response(order, conv.title if conv else "(삭제된 대화)", char_name)


@router.delete("/orders/{order_id}", status_code=204)
async def cancel_order(order_id: str, db: Session = Depends(get_db)):
    """주문 취소 (접수 상태만 가능)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    if order.status != "접수":
        raise HTTPException(
            status_code=400,
            detail=f"'{order.status}' 상태의 주문은 취소할 수 없습니다. '접수' 상태만 취소 가능합니다."
        )

    order.status = "취소"
    order.updated_at = now_utc()
    db.commit()
    return None
