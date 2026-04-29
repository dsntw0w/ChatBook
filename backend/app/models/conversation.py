# backend/app/models/conversation.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def now_utc():
    """UTC 현재 시간을 datetime 객체로 반환 (DateTime 컬럼용)."""
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False, default="새 대화")
    provider = Column(
        String,
        nullable=False,
        default="openai"
    )
    model = Column(String, nullable=False, default="gpt-5-nano")
    # RP 캐릭터봇 연동: 일반 대화(NULL) vs 캐릭터 세션 대화(캐릭터 ID)
    character_id = Column(
        Integer,
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 관계
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    order = relationship("Order", back_populates="conversation", uselist=False)
    character = relationship("Character", backref="conversations")

    __table_args__ = (
        CheckConstraint(
            "provider IN ('openai', 'gemini', 'deepseek', 'demo')",
            name="ck_conversation_provider"
        ),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(
        String,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    # RP 캐릭터봇 시스템 연동을 위한 session_id (nullable, 추후 마이그레이션용)
    session_id = Column(
        Integer,
        ForeignKey("chatsessions.id", ondelete="SET NULL"),
        nullable=True
    )
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # 관계
    conversation = relationship("Conversation", back_populates="messages")
    session = relationship("ChatSession", back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="ck_message_role"
        ),
    )
