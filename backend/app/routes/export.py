# backend/app/routes/export.py
import json
import zipfile
import io
import logging
from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, Conversation, Message, Character, ChatSession

router = APIRouter(prefix="/api", tags=["export"])
logger = logging.getLogger(__name__)


def _serialize_for_json(obj: object) -> object:
    """객체를 JSON 직렬화 가능한 형태로 재귀 변환 (datetime → ISO 8601 문자열)"""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    return obj


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


def _get_export_data(order: Order, conv: Conversation, messages: list[Message], db: Session) -> dict:
    """익스포트용 데이터 구성 (datetime → ISO 문자열 변환 포함)"""
    character_name = _get_character_name_for_order(order, db)

    data = {
        "order": {
            "id": order.id,
            "conversation_id": order.conversation_id,
            "status": order.status,
            "quantity": order.quantity,
            "cover_style": order.cover_style,
            "memo": order.memo,
            "character_name": character_name,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        },
        "conversation": {
            "id": conv.id,
            "title": conv.title,
            "provider": conv.provider,
            "model": conv.model,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                }
                for msg in messages
            ],
        },
    }
    return _serialize_for_json(data)


def _generate_conversation_text(conv: Conversation, messages: list[Message]) -> str:
    """대화 내용을 읽기 쉬운 텍스트로 변환"""
    lines = [
        f"대화 제목: {conv.title}",
        f"사용 AI: {conv.provider} / {conv.model}",
        f"생성일: {conv.created_at}",
        "",
        "=" * 50,
        "",
    ]
    for msg in messages:
        role_label = "사용자" if msg.role == "user" else "AI"
        lines.append(f"{role_label} [{msg.created_at}]:")
        lines.append(msg.content)
        lines.append("")
    return "\n".join(lines)


@router.get("/orders/{order_id}/export")
async def export_order(
    order_id: str,
    format: str = Query("json", pattern=r"^(json|zip)$"),
    db: Session = Depends(get_db),
):
    """
    주문 + 대화 데이터 익스포트

    - format=json: JSON 형식으로 다운로드
    - format=zip: JSON + TXT 파일을 ZIP으로 압축 다운로드
    """
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

    if format == "json":
        # JSON 응답
        data = _get_export_data(order, conv, messages, db)
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=order_{order_id}.json"
            },
        )

    elif format == "zip":
        # ZIP 응답 (JSON + TXT)
        data = _get_export_data(order, conv, messages, db)
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        text_str = _generate_conversation_text(conv, messages)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"order_{order_id}/order.json", json_str)
            zf.writestr(f"order_{order_id}/conversation.json", json.dumps(data["conversation"], ensure_ascii=False, indent=2))
            zf.writestr(f"order_{order_id}/conversation.txt", text_str)

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=order_{order_id}.zip"
            },
        )
