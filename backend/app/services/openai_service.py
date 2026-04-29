# backend/app/services/openai_service.py
from openai import AsyncOpenAI
from typing import Dict, List
from app.services.base_ai_service import OpenAICompatibleService


class OpenAIService(OpenAICompatibleService):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def get_models(self) -> List[Dict[str, str]]:
        # NOTE: 정적 폴백 모델 목록입니다. OpenAI API의 /v1/models 엔드포인트를
        # 통해 동적으로 조회하는 방식으로 전환하면 최신 모델을 자동 반영할 수 있습니다.
        # 현재는 데모/시연 목적으로 대표 모델만 하드코딩되어 있습니다.
        return [
            {"id": "gpt-5-nano", "name": "GPT-5 Nano", "description": "초경량 최신 모델"},
            {"id": "gpt-4.1-nano", "name": "GPT-4.1 Nano", "description": "경량 고성능 모델"},
        ]

    def get_provider_name(self) -> str:
        return "openai"
