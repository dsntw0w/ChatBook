# backend/app/services/deepseek_service.py
from openai import AsyncOpenAI
from typing import Dict, List
from app.services.base_ai_service import OpenAICompatibleService


class DeepSeekService(OpenAICompatibleService):
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def get_models(self) -> List[Dict[str, str]]:
        # NOTE: 정적 폴백 모델 목록입니다. DeepSeek API의 /v1/models 엔드포인트를
        # 통해 동적으로 조회하는 방식으로 전환하면 최신 모델을 자동 반영할 수 있습니다.
        # 현재는 데모/시연 목적으로 대표 모델만 하드코딩되어 있습니다.
        return [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "범용 대화 모델"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "description": "추론 특화 모델"},
        ]

    def get_provider_name(self) -> str:
        return "deepseek"
