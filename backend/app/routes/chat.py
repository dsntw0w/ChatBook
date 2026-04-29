# backend/app/routes/chat.py
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db, SessionLocal
from app.models import Conversation, Message
from app.models.character import CharacterSettings
from app.schemas import (
    ConversationCreate, ConversationUpdate,
    ConversationResponse, ConversationDetailResponse,
    ChatSendRequest, MessageResponse,
    ProviderModelsResponse, ModelInfo,
)
from app.services import ProviderRegistry
from app.models.conversation import generate_uuid, now_utc

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


# ==================== AI 모델 목록 ====================

@router.get("/models", response_model=list[ProviderModelsResponse])
async def get_models():
    """사용 가능한 모든 AI Provider의 모델 목록 조회"""
    providers = []
    for provider_name in ProviderRegistry.list_providers():
        try:
            provider = ProviderRegistry.get(provider_name)
            models = await provider.get_models()
            providers.append(ProviderModelsResponse(
                provider=provider_name,
                models=[ModelInfo(**m) for m in models]
            ))
        except Exception as e:
            logger.error(f"Failed to get models from {provider_name}: {e}")
    return providers


# ==================== 헬퍼 함수 ====================

def build_system_prompt(settings: CharacterSettings) -> str:
    """CharacterSettings → LLM 시스템 프롬프트 문자열 생성"""
    if settings.prompt:
        # 사용자 정의 프롬프트: 변수 치환
        prompt = settings.prompt
        prompt = prompt.replace("{{description}}", settings.description or "")
        prompt = prompt.replace("{{persona}}", settings.persona or "")
        prompt = prompt.replace("{{lorebook}}", settings.lorebook or "")
        return prompt
    else:
        # 기본 템플릿
        parts = []
        if settings.description:
            parts.append(f"[캐릭터 설정]\n{settings.description}")
        if settings.persona:
            parts.append(f"[사용자 설정]\n{settings.persona}")
        if settings.lorebook:
            parts.append(f"[세계관]\n{settings.lorebook}")
        if parts:
            parts.append("위 설정에 맞게 캐릭터로서 자연스럽게 롤플레잉 대화를 진행하세요.")
            return "\n\n".join(parts)
        return ""


def _build_conversation_response(conv: Conversation, msg_count: int = 0) -> ConversationResponse:
    """Conversation ORM 객체 → ConversationResponse 변환 헬퍼 (중복 제거)"""
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        provider=conv.provider,
        model=conv.model,
        character_id=conv.character_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=msg_count,
    )


# ==================== SSE 채팅 ====================


@router.post("/chat/send",
    responses={
        200: {
            "description": "SSE 이벤트 스트림 (text/event-stream)",
            "content": {"text/event-stream": {}},
        },
        404: {"description": "대화방을 찾을 수 없음"},
        400: {"description": "Provider 선택 오류"},
    },
)
async def chat_send(
    request: ChatSendRequest,
    db: Session = Depends(get_db),
):
    """
    채팅 메시지 전송 + AI 응답 (SSE 스트리밍)

    SSE 이벤트 형식:
      data: {"type":"token","content":"텍스트"}

      data: {"type":"done","message_id":"...","provider":"...","model":"..."}

      data: {"type":"error","message":"에러 메시지"}
    """
    # 1. 대화방 존재 확인
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")

    # 2. 사용자 메시지 저장 (session_id 포함)
    user_msg_id = generate_uuid()
    user_msg = Message(
        id=user_msg_id,
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        created_at=now_utc(),
        session_id=request.session_id,
    )
    db.add(user_msg)
    db.commit()

    # 3. 이전 메시지 히스토리 조회 (컨텍스트용)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == request.conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    messages = [{"role": msg.role, "content": msg.content} for msg in history]

    # 3.5 캐릭터 설정 기반 시스템 프롬프트 생성
    # 대화의 character_id와 요청의 character_id가 일치할 때만 RP 적용
    effective_character_id = request.character_id
    if effective_character_id and conversation.character_id and effective_character_id != conversation.character_id:
        logger.warning(f"[RP] character_id mismatch: request={effective_character_id}, conversation={conversation.character_id}. Ignoring RP.")
        effective_character_id = None
    if not effective_character_id and conversation.character_id:
        # 대화 자체가 캐릭터 세션용이면 conversation의 character_id 사용
        effective_character_id = conversation.character_id

    if effective_character_id:
        settings = db.query(CharacterSettings).filter(
            CharacterSettings.character_id == effective_character_id
        ).first()
        if settings and any([settings.description, settings.persona, settings.lorebook, settings.prompt]):
            system_content = build_system_prompt(settings)
            if system_content:
                logger.debug(f"Applying RP system prompt for character_id={effective_character_id}")
                messages.insert(0, {"role": "system", "content": system_content})

    # 4. Provider 선택
    if request.api_key and request.provider != "demo":
        # 사용자 제공 API 키로 동적 provider 인스턴스 생성
        from app.services import create_provider_instance
        try:
            provider = create_provider_instance(request.provider, request.api_key)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # 기존: ProviderRegistry에서 등록된 provider 사용
        try:
            provider = ProviderRegistry.get(request.provider)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 5. SSE 스트리밍 응답 생성
    #    DB 세션을 제너레이터 밖에서 분리: ai_msg_id 미리 생성, 제너레이터 내에서는
    #    별도 SessionLocal()을 사용하여 요청 세션 수명과 무관하게 DB 저장
    ai_msg_id = generate_uuid()
    conv_id = request.conversation_id

    async def event_stream():
        full_content = ""
        save_db = None

        try:
            async for token in provider.stream_chat(
                messages=messages,
                model=request.model,
            ):
                full_content += token
                event_data = json.dumps({"type": "token", "content": token}, ensure_ascii=False)
                yield f"data: {event_data}\n\n"

            # 6. AI 응답 저장 (별도 DB 세션으로 격리, session_id 포함)
            save_db = SessionLocal()
            ai_msg = Message(
                id=ai_msg_id,
                conversation_id=conv_id,
                role="assistant",
                content=full_content,
                created_at=now_utc(),
                session_id=request.session_id,
            )
            save_db.add(ai_msg)

            # 대화방 updated_at 갱신
            conv = save_db.query(Conversation).filter(Conversation.id == conv_id).first()
            if conv:
                conv.updated_at = now_utc()
            save_db.commit()

            # done 이벤트
            done_data = json.dumps({
                "type": "done",
                "message_id": ai_msg_id,
                "provider": request.provider,
                "model": request.model,
            }, ensure_ascii=False)
            yield f"data: {done_data}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            error_data = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

        finally:
            # 클라이언트 연결 끊김 등 어떤 상황에서도 DB 세션 정리 보장
            if save_db is not None:
                try:
                    save_db.close()
                except Exception:
                    pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 버퍼링 방지
        },
    )


# ==================== 대화방 CRUD ====================

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    character_id: Optional[str] = Query(None, description="필터: 'null'=일반대화만, '숫자'=특정캐릭터대화만, 생략=전체"),
    db: Session = Depends(get_db),
):
    """대화방 목록 조회 (최신순) - character_id 필터링 지원"""
    # message_count를 서브쿼리로 계산하여 N+1 문제 해결
    count_subquery = (
        db.query(Message.conversation_id, func.count(Message.id).label('count'))
        .group_by(Message.conversation_id)
        .subquery()
    )

    query = (
        db.query(Conversation, func.coalesce(count_subquery.c.count, 0).label('message_count'))
        .outerjoin(count_subquery, Conversation.id == count_subquery.c.conversation_id)
    )

    # character_id 필터링
    if character_id == "null":
        # character_id가 NULL인 일반 대화만 반환
        query = query.filter(Conversation.character_id.is_(None))
    elif character_id is not None:
        try:
            cid = int(character_id)
            query = query.filter(Conversation.character_id == cid)
        except ValueError:
            raise HTTPException(status_code=400, detail="character_id must be 'null' or a valid integer")

    conversations = query.order_by(desc(Conversation.updated_at)).all()

    return [_build_conversation_response(conv, msg_count) for conv, msg_count in conversations]


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
):
    """새 대화방 생성 (일반 또는 캐릭터 세션용)"""
    conv = Conversation(
        id=generate_uuid(),
        title=request.title,
        provider=request.provider,
        model=request.model,
        character_id=request.character_id,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return _build_conversation_response(conv, 0)


@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation(conv_id: str, db: Session = Depends(get_db)):
    """대화방 + 메시지 전체 조회"""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
        .all()
    )

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        provider=conv.provider,
        model=conv.model,
        character_id=conv.character_id,
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
    )


@router.patch("/conversations/{conv_id}", response_model=ConversationResponse)
async def update_conversation(
    conv_id: str,
    request: ConversationUpdate,
    db: Session = Depends(get_db),
):
    """대화방 제목 수정"""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")

    if request.title is not None:
        conv.title = request.title
    conv.updated_at = now_utc()
    db.commit()
    db.refresh(conv)

    msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()

    return _build_conversation_response(conv, msg_count)


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(conv_id: str, db: Session = Depends(get_db)):
    """대화방 + 메시지 삭제 (CASCADE)"""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="대화방을 찾을 수 없습니다.")

    db.delete(conv)
    db.commit()
    return None
