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
        return [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "범용 대화 모델"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "description": "추론 특화 모델"},
        ]

    def get_provider_name(self) -> str:
        return "deepseek"
