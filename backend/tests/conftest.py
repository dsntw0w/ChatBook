# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db

# 모델을 명시적으로 import하여 Base.metadata에 등록
import app.models  # noqa: F401

from app.main import app
from app.config import settings

# 테스트용 인메모리 SQLite
# StaticPool 사용: :memory: DB에서 모든 연결이 동일한 DB를 공유하도록 함
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """각 테스트 전에 테이블 생성, 후에 삭제"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """테스트용 DB 세션"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """FastAPI TestClient

    참고: app은 모듈 레벨 싱글톤이므로 병렬 테스트(xdist) 실행 시
    dependency_overrides 충돌 가능성이 있습니다. 순차 실행(--numprocesses=0) 권장.
    """
    from fastapi.testclient import TestClient

    # 의존성 오버라이드: 테스트 DB 사용
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        # 함수 레벨 fixture 종료 시 오버라이드 정리
        app.dependency_overrides.clear()
