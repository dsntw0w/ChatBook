# backend/app/models/character.py
"""Role Playing 캐릭터봇 시스템을 위한 DB 모델"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Character(Base):
    """캐릭터봇 모델"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 관계
    sessions = relationship(
        "ChatSession",
        back_populates="character",
        cascade="all, delete-orphan",
    )
    settings = relationship(
        "CharacterSettings",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan",
    )
    conversations = relationship(
        "Conversation",
        back_populates="character",
    )


class ChatSession(Base):
    """캐릭터별 대화 세션 모델"""
    __tablename__ = "chatsessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(
        Integer,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False, default="New Chat")
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 관계
    character = relationship("Character", back_populates="sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="save-update, merge, delete, delete-orphan",
        order_by="Message.created_at",
    )


class CharacterSettings(Base):
    """캐릭터별 설정 모델 (persona, lorebook, prompt 등)"""
    __tablename__ = "charactersettings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(
        Integer,
        ForeignKey("characters.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=True)
    persona = Column(Text, nullable=True)
    lorebook = Column(Text, nullable=True)
    prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 관계
    character = relationship("Character", back_populates="settings")
