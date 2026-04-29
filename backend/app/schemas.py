# backend/app/schemas.py
"""Pydantic 요청/응답 스키마 - 모든 API 엔드포인트용"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== 대화방 (Conversation) ====================

class ConversationCreate(BaseModel):
    """대화방 생성 요청"""
    title: str = Field(default="새 대화", max_length=200)
    provider: str = Field(default="openai", pattern=r"^(openai|gemini|deepseek|demo)$")
    model: str = Field(default="gpt-5-nano", max_length=100)
    character_id: Optional[int] = Field(default=None, description="연결할 캐릭터 ID (일반 대화일 경우 생략)")


class ConversationUpdate(BaseModel):
    """대화방 수정 요청"""
    title: Optional[str] = Field(default=None, max_length=200)


class ConversationResponse(BaseModel):
    """대화방 응답"""
    id: str
    title: str
    provider: str
    model: str
    character_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(BaseModel):
    """대화방 상세 응답 (메시지 포함)"""
    id: str
    title: str
    provider: str
    model: str
    character_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    messages: List["MessageResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== 메시지 (Message) ====================

class ChatSendRequest(BaseModel):
    """채팅 메시지 전송 요청"""
    conversation_id: str = Field(..., description="대화방 ID")
    message: str = Field(..., min_length=1, max_length=10000)
    provider: str = Field(default="openai", pattern=r"^(openai|gemini|deepseek|demo)$")
    model: str = Field(default="gpt-5-nano")
    character_id: Optional[int] = Field(default=None, description="캐릭터 ID (선택)")
    session_id: Optional[int] = Field(default=None, description="세션 ID (선택, RP 캐릭터봇 연동용)")
    api_key: Optional[str] = Field(default=None, description="사용자 제공 API 키 (선택)")


class MessageResponse(BaseModel):
    """메시지 응답"""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 주문 (Order) ====================

class OrderCreate(BaseModel):
    """주문 생성 요청"""
    conversation_id: str
    quantity: int = Field(default=1, ge=1, le=100)
    cover_style: str = Field(default="basic")
    memo: str = Field(default="", max_length=500)


class OrderStatusUpdate(BaseModel):
    """주문 상태 변경 요청"""
    status: str = Field(..., pattern=r"^(접수|제작중|완료|취소)$")


class OrderResponse(BaseModel):
    """주문 응답"""
    id: str
    conversation_id: str
    conversation_title: str = ""
    character_name: Optional[str] = None
    status: str
    quantity: int
    cover_style: str
    memo: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    """주문 상세 응답 (대화 내용 포함)"""
    conversation: Optional[ConversationDetailResponse] = None


# ==================== AI 모델 ====================

class ModelInfo(BaseModel):
    """개별 모델 정보"""
    id: str
    name: str
    description: str


class ProviderModelsResponse(BaseModel):
    """Provider별 모델 목록 응답"""
    provider: str
    models: List[ModelInfo]


# ==================== 헬스체크 ====================

class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    service: str
    demo_mode: bool = False


# ==================== 캐릭터 (Character) ====================

class CharacterCreate(BaseModel):
    """캐릭터 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100)


class CharacterUpdate(BaseModel):
    """캐릭터 수정 요청"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    avatar: Optional[str] = None


class CharacterResponse(BaseModel):
    """캐릭터 응답"""
    id: int
    name: str
    avatar: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 캐릭터 세션 (ChatSession) ====================

class ChatSessionCreate(BaseModel):
    """캐릭터 세션 생성 요청"""
    title: Optional[str] = Field(default="New Chat", max_length=200)
    provider: Optional[str] = None
    model: Optional[str] = None


class ChatSessionResponse(BaseModel):
    """캐릭터 세션 응답"""
    id: int
    character_id: int
    title: str
    provider: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 캐릭터 설정 (CharacterSettings) ====================

class CharacterSettingsUpdate(BaseModel):
    """캐릭터 설정 수정 요청"""
    description: Optional[str] = None
    persona: Optional[str] = None
    lorebook: Optional[str] = None
    prompt: Optional[str] = None


class CharacterSettingsResponse(BaseModel):
    """캐릭터 설정 응답"""
    id: int
    character_id: int
    description: Optional[str]
    persona: Optional[str]
    lorebook: Optional[str]
    prompt: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 공통 에러 ====================

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    message: str
