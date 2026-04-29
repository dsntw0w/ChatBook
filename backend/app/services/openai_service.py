# backend/app/services/openai_service.py
from openai import AsyncOpenAI
from typing import Dict, List
from app.services.base_ai_service import OpenAICompatibleService


class OpenAIService(OpenAICompatibleService):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def get_models(self) -> List[Dict[str, str]]:
        return [
            {"id": "gpt-5-nano", "name": "GPT-5 Nano", "description": "초경량 최신 모델"},
            {"id": "gpt-4.1-nano", "name": "GPT-4.1 Nano", "description": "경량 고성능 모델"},
        ]

    def get_provider_name(self) -> str:
        return "openai"
