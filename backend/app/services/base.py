# backend/app/services/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Any


class AIProvider(ABC):
    """AI Provider 추상 베이스 클래스"""

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        채팅 메시지를 스트리밍 방식으로 생성합니다.

        Args:
            messages: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
            model: 사용할 모델 ID (예: "gpt-5-nano", "gemini-2.5-flash-lite")
            **kwargs: 추가 파라미터 (temperature, max_tokens 등)

        Yields:
            str: 토큰 단위로 스트리밍되는 텍스트 청크
        """
        ...

    @abstractmethod
    async def get_models(self) -> List[Dict[str, str]]:
        """
        사용 가능한 모델 목록을 반환합니다.

        Returns:
            [
              {"id": "model-id", "name": "표시명", "description": "설명"},
              ...
            ]
        """
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Provider 이름 반환 ('openai', 'gemini', 'deepseek', 'demo')"""
        ...
