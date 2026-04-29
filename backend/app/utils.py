# backend/app/utils.py
"""공통 유틸리티 함수"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Order, Character, ChatSession, Message


def now_utc() -> datetime:
    """UTC 현재 시간을 datetime 객체로 반환."""
    return datetime.now(timezone.utc)


def get_character_name_for_order(order: Order, db: Session) -> Optional[str]:
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
