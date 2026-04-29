# backend/app/services/gemini_service.py
from google import genai
from typing import AsyncIterator, Dict, List, Any
from app.services.base import AIProvider


class GeminiService(AIProvider):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-2.5-flash-lite",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        # Gemini API는 system role을 직접 지원하지 않으므로,
        # system 메시지를 첫 번째 user 메시지 앞에 병합하여 전달
        #
        # NOTE: 이 우회 방식은 OpenAI/DeepSeek의 네이티브 system role 대비 의미적 차이가 있습니다.
        # system prompt가 user 메시지의 일부로 전달되므로, 모델에 따라 system 지시사항
        # 준수도에 미묘한 차이가 발생할 수 있습니다. Gemini API가 추후 system role을
        # 네이티브 지원하게 되면 이 우회 로직을 제거하고 직접 system 메시지를 전달하는
        # 방식으로 전환하는 것이 바람직합니다.
        system_messages = [m for m in messages if m["role"] == "system"]
        chat_messages = [m for m in messages if m["role"] != "system"]

        if system_messages:
            system_content = "\n".join([m["content"] for m in system_messages])
            if chat_messages:
                chat_messages[0]["content"] = (
                    f"[System Instructions]\n{system_content}\n\n{chat_messages[0]['content']}"
                )
            else:
                # user 메시지가 없는 경우 system 메시지를 user로 변환
                chat_messages.insert(0, {"role": "user", "content": system_content})

        # Gemini는 messages 형식을 자체 Contents 포맷으로 변환 필요
        contents = self._convert_messages(chat_messages)
        response = await self.client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
            **kwargs,  # temperature, max_tokens 등 추가 파라미터를 Gemini API로 전달
        )
        async for chunk in response:
            # 방어 코드: chunk.text가 None이거나 빈 문자열인 경우 대비
            if chunk.text is not None and chunk.text:
                yield chunk.text

    def _convert_messages(self, messages: List[Dict[str, str]]) -> list:
        """
        OpenAI 형식의 messages를 Gemini Contents 형식으로 변환합니다.
        system role은 stream_chat()에서 사전 처리되므로 여기서는 user/assistant만 처리.

        OpenAI: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        Gemini: [{"role": "user", "parts": [{"text": "..."}]}, {"role": "model", "parts": [{"text": "..."}]}]
        """
        contents = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                # NOTE: system role은 stream_chat()에서 이미 user 메시지에 병합되므로
                #       이 분기는 정상 흐름에서는 도달하지 않음 (방어적 안전장치)
                gemini_role = "user"
            elif role == "assistant":
                # Gemini는 'assistant' 대신 'model' 사용
                gemini_role = "model"
            else:
                gemini_role = role
            contents.append({
                "role": gemini_role,
                "parts": [{"text": msg["content"]}]
            })
        return contents

    async def get_models(self) -> List[Dict[str, str]]:
        # NOTE: 정적 폴백 모델 목록입니다. Gemini API의 models.list 엔드포인트를
        # 통해 동적으로 조회하는 방식으로 전환하면 최신 모델을 자동 반영할 수 있습니다.
        # 현재는 데모/시연 목적으로 대표 모델만 하드코딩되어 있습니다.
        return [
            {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite", "description": "경량 고속 모델"},
            {"id": "gemini-3.1-flash-lite-preview", "name": "Gemini 3.1 Flash Lite Preview", "description": "초경량 미리보기 모델"},
        ]

    def get_provider_name(self) -> str:
        return "gemini"
