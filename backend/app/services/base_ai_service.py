# backend/app/services/base_ai_service.py
"""OpenAI 호환 API를 위한 공통 스트리밍 로직 (OpenAI/DeepSeek 서비스 중복 제거)"""
from typing import AsyncIterator, Dict, List, Any
from app.services.base import AIProvider


class OpenAICompatibleService(AIProvider):
    """OpenAI 호환 API의 stream_chat() 공통 구현을 제공하는 추상 베이스 클래스.

    하위 클래스는 __init__에서 self.client (AsyncOpenAI 인스턴스)를 설정하고,
    get_models(), get_provider_name()을 구현해야 합니다.
    """

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            # 방어 코드: choices가 비어있거나 delta가 None인 경우 대비
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta is None:
                continue
            if delta.content:
                yield delta.content
