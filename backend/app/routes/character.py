# backend/app/routes/character.py
"""캐릭터봇 API 라우트 - 캐릭터 CRUD, 세션, 설정"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.character import Character, ChatSession, CharacterSettings
from app.schemas import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    ChatSessionCreate, ChatSessionResponse,
    CharacterSettingsUpdate, CharacterSettingsResponse,
)

router = APIRouter(prefix="/api/characters", tags=["characters"])
logger = logging.getLogger(__name__)


# ==================== 캐릭터 CRUD ====================

def _generate_unique_name(db: Session, base_name: str) -> str:
    """중복된 이름이 있으면 base_name (1), base_name (2) ... 으로 고유 이름 생성"""
    existing_names = {r[0] for r in db.query(Character.name).all()}
    if base_name not in existing_names:
        return base_name
    i = 1
    while True:
        candidate = f"{base_name} ({i})"
        if candidate not in existing_names:
            return candidate
        i += 1


@router.get("", response_model=list[CharacterResponse])
async def list_characters(db: Session = Depends(get_db)):
    """모든 캐릭터 목록 조회 (이름순)"""
    characters = db.query(Character).order_by(Character.name).all()
    return characters


@router.post("", response_model=CharacterResponse, status_code=201)
async def create_character(
    data: CharacterCreate,
    db: Session = Depends(get_db),
):
    """새 캐릭터 생성 (CharacterSettings도 빈 값으로 자동 생성) - 중복 이름 자동 접미사"""
    unique_name = _generate_unique_name(db, data.name)

    new_character = Character(name=unique_name)
    db.add(new_character)
    db.flush()  # ID 확보

    settings = CharacterSettings(character_id=new_character.id)
    db.add(settings)
    db.commit()
    db.refresh(new_character)

    logger.info(f"Created character: id={new_character.id}, name={new_character.name}")
    return new_character


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """특정 캐릭터 조회"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    return character


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    db: Session = Depends(get_db),
):
    """캐릭터 이름/아바타 수정"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    if data.name is not None:
        # 중복 이름 확인 (자기 자신 제외)
        existing = (
            db.query(Character)
            .filter(Character.name == data.name, Character.id != character_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"이미 존재하는 캐릭터 이름입니다: {data.name}",
            )
        character.name = data.name

    if data.avatar is not None:
        character.avatar = data.avatar

    db.commit()
    db.refresh(character)

    logger.info(f"Updated character: id={character_id}")
    return character


@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """캐릭터 삭제 (CASCADE로 세션, 설정도 삭제됨)"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    db.delete(character)
    db.commit()

    logger.info(f"Deleted character: id={character_id}")
    return None


# ==================== 캐릭터별 세션 관리 ====================

@router.get("/{character_id}/sessions", response_model=list[ChatSessionResponse])
async def list_character_sessions(
    character_id: int,
    db: Session = Depends(get_db),
):
    """해당 캐릭터의 모든 채팅 세션 목록 (최신순)"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.character_id == character_id)
        .order_by(desc(ChatSession.updated_at))
        .all()
    )
    return sessions


@router.post("/{character_id}/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_character_session(
    character_id: int,
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
):
    """새 채팅 세션 생성"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    session = ChatSession(
        character_id=character_id,
        title=data.title if data.title else "New Chat",
        provider=data.provider,
        model=data.model,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Created session: id={session.id} for character_id={character_id}")
    return session


@router.delete("/{character_id}/sessions/{session_id}", status_code=204)
async def delete_character_session(
    character_id: int,
    session_id: int,
    db: Session = Depends(get_db),
):
    """세션 삭제"""
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.character_id == character_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    db.delete(session)
    db.commit()

    logger.info(f"Deleted session: id={session_id} from character_id={character_id}")
    return None


# ==================== 캐릭터 설정 관리 ====================

@router.get("/{character_id}/settings", response_model=CharacterSettingsResponse)
async def get_character_settings(
    character_id: int,
    db: Session = Depends(get_db),
):
    """캐릭터 설정 조회 (없으면 404)"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    settings = (
        db.query(CharacterSettings)
        .filter(CharacterSettings.character_id == character_id)
        .first()
    )
    if not settings:
        raise HTTPException(status_code=404, detail="캐릭터 설정을 찾을 수 없습니다.")

    return settings


@router.patch("/{character_id}/settings", response_model=CharacterSettingsResponse)
async def update_character_settings(
    character_id: int,
    data: CharacterSettingsUpdate,
    db: Session = Depends(get_db),
):
    """캐릭터 설정 수정"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")

    settings = (
        db.query(CharacterSettings)
        .filter(CharacterSettings.character_id == character_id)
        .first()
    )
    if not settings:
        raise HTTPException(status_code=404, detail="캐릭터 설정을 찾을 수 없습니다.")

    # 부분 업데이트: 명시적으로 전달된 필드만 수정
    if data.description is not None:
        settings.description = data.description
    if data.persona is not None:
        settings.persona = data.persona
    if data.lorebook is not None:
        settings.lorebook = data.lorebook
    if data.prompt is not None:
        settings.prompt = data.prompt

    db.commit()
    db.refresh(settings)

    logger.info(f"Updated settings for character_id={character_id}")
    return settings
