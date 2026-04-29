# backend/tests/test_providers.py
"""AI Provider 추상화 계층 단위 테스트"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.base import AIProvider
from app.services.demo_service import DemoProvider
from app.services import ProviderRegistry


class TestDemoProvider:
    """DemoProvider 단위 테스트"""

    @pytest.mark.asyncio
    async def test_stream_chat_returns_tokens(self):
        """stream_chat이 토큰을 yield하는지 검증"""
        provider = DemoProvider()
        messages = [{"role": "user", "content": "안녕하세요"}]

        tokens = []
        async for token in provider.stream_chat(messages):
            tokens.append(token)

        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)
        # 완성된 문장 확인
        full_text = "".join(tokens)
        assert len(full_text) > 0

    @pytest.mark.asyncio
    async def test_get_models_format(self):
        """get_models 응답 형식 검증"""
        provider = DemoProvider()
        models = await provider.get_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "id" in models[0]
        assert "name" in models[0]
        assert "description" in models[0]

    def test_get_provider_name(self):
        """get_provider_name 반환값 확인"""
        provider = DemoProvider()
        assert provider.get_provider_name() == "demo"

    @pytest.mark.asyncio
    async def test_keyword_based_response(self):
        """키워드 기반 응답 템플릿 선택 검증"""
        provider = DemoProvider()

        # 코딩 관련
        messages = [{"role": "user", "content": "Python 코딩 질문이 있어요"}]
        tokens = [t async for t in provider.stream_chat(messages)]
        full = "".join(tokens)
        assert "코딩" in full or "Provider" in full

        # 일반
        messages = [{"role": "user", "content": "아무말"}]
        tokens = [t async for t in provider.stream_chat(messages)]
        full = "".join(tokens)
        assert "데모 모드" in full


class TestProviderRegistry:
    """ProviderRegistry 단위 테스트"""

    def test_register_and_get(self):
        """Provider 등록 및 조회"""
        ProviderRegistry.clear()
        provider = DemoProvider()
        ProviderRegistry.register(provider)
        retrieved = ProviderRegistry.get("demo")
        assert retrieved is provider

    def test_get_unknown_provider(self):
        """등록되지 않은 Provider 조회 시 예외"""
        ProviderRegistry.clear()
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderRegistry.get("nonexistent")

    def test_list_providers(self):
        """Provider 목록 조회"""
        ProviderRegistry.clear()
        provider = DemoProvider()
        ProviderRegistry.register(provider)
        providers = ProviderRegistry.list_providers()
        assert "demo" in providers
        assert len(providers) == 1

    def test_clear_providers(self):
        """Provider 전체 제거"""
        ProviderRegistry.clear()
        ProviderRegistry.register(DemoProvider())
        assert len(ProviderRegistry.list_providers()) == 1
        ProviderRegistry.clear()
        assert len(ProviderRegistry.list_providers()) == 0
