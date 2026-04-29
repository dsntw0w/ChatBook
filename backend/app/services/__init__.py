# backend/app/services/__init__.py
import logging
from .base import AIProvider
from .openai_service import OpenAIService
from .gemini_service import GeminiService
from .deepseek_service import DeepSeekService
from .demo_service import DemoProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Provider 관리 레지스트리 (싱글톤 패턴)"""

    _providers: dict[str, AIProvider] = {}

    @classmethod
    def register(cls, provider: AIProvider) -> None:
        name = provider.get_provider_name()
        cls._providers[name] = provider
        logger.info(f"Registered provider: {name}")

    @classmethod
    def get(cls, name: str) -> AIProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._providers.keys())}")
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def clear(cls) -> None:
        """테스트용: 모든 Provider 제거"""
        cls._providers.clear()


def init_providers(config) -> None:
    """
    환경 설정에 따라 Provider를 등록합니다.

    - USE_DEMO_MODE=true: DemoProvider만 등록 (API 키 불필요)
    - USE_DEMO_MODE=false: 유효한 API 키가 있는 Provider만 등록
    """
    ProviderRegistry.clear()

    if config.USE_DEMO_MODE:
        ProviderRegistry.register(DemoProvider())
        logger.info("🟡 Demo mode activated - using mock responses")
        # 데모 모드에서도 실제 API 키가 설정되어 있다면 함께 등록하여
        # 사용자가 데모/실제 Provider를 선택할 수 있도록 함
        _register_real_providers(config)
        return

    # 실제 Provider 등록 (API 키 검증)
    _register_real_providers(config)

    if not ProviderRegistry._providers:
        logger.warning("⚠️ No API keys configured. Falling back to DemoProvider.")
        ProviderRegistry.register(DemoProvider())


def create_provider_instance(provider_name: str, api_key: str) -> AIProvider:
    """요청별 API 키로 provider 인스턴스를 동적 생성합니다."""
    if provider_name == "openai":
        from .openai_service import OpenAIService
        return OpenAIService(api_key=api_key)
    elif provider_name == "gemini":
        from .gemini_service import GeminiService
        return GeminiService(api_key=api_key)
    elif provider_name == "deepseek":
        from .deepseek_service import DeepSeekService
        return DeepSeekService(api_key=api_key)
    else:
        raise ValueError(f"Cannot create provider instance for: {provider_name}")


def _register_real_providers(config) -> None:
    """유효한 API 키가 있는 실제 Provider들을 등록합니다."""
    if config.OPENAI_API_KEY and config.OPENAI_API_KEY not in ("sk-dummy", ""):
        ProviderRegistry.register(OpenAIService(api_key=config.OPENAI_API_KEY))

    if config.GEMINI_API_KEY and config.GEMINI_API_KEY not in ("gemini-dummy", ""):
        ProviderRegistry.register(GeminiService(api_key=config.GEMINI_API_KEY))

    if config.DEEPSEEK_API_KEY and config.DEEPSEEK_API_KEY not in ("deepseek-dummy", ""):
        ProviderRegistry.register(DeepSeekService(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        ))
