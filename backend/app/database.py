# backend/app/database.py
# 참고: 프로덕션 배포 시 SQLite의 동시성 제한(WAL 모드 미사용 시 단일 쓰기 잠금)을
#       고려하여 PostgreSQL 또는 MySQL로 마이그레이션을 검토할 수 있습니다.
#       SQLAlchemy ORM을 사용하므로 dialect 변경만으로 전환 가능합니다.
#       (참조: code-review-debug-prep.md §2.3, 제안 이슈 #20)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import os

# data 디렉토리 생성 (SQLite 파일 저장 경로)
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용: 멀티스레드 허용
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI 의존성 주입용 DB 세션 제너레이터"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """모든 테이블 생성 (main.py startup에서 호출)"""
    Base.metadata.create_all(bind=engine)
