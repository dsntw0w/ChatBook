# backend/app/services/demo_service.py
import asyncio
from typing import AsyncIterator, Dict, List, Any
from app.services.base import AIProvider


class DemoProvider(AIProvider):
    """API 키 없이 미리 정의된 응답으로 SSE 스트리밍을 흉내내는 데모 Provider"""

    DEMO_RESPONSES = {
        "default": [
            "안녕하세요! 저는 ChatBook 데모 모드입니다. ",
            "이 응답은 API 키 없이도 ",
            "SSE 스트리밍이 어떻게 동작하는지 ",
            "보여주기 위한 예시입니다. ",
            "실제 API 키를 설정하시면 OpenAI, Gemini, DeepSeek와 ",
            "실제로 대화하실 수 있습니다!",
        ],
        "코딩": [
            "코딩 관련 질문을 주셨네요! ",
            "데모 모드에서는 실제 코드 실행이 불가능하지만, ",
            "실제 Provider를 연결하면 정확한 코드 예제와 ",
            "설명을 받아보실 수 있습니다. ",
            "`.env` 파일에 API 키를 설정하고 `USE_DEMO_MODE=false`로 변경해보세요.",
        ],
        "맛집": [
            "맛집을 찾고 계시군요! ",
            "데모 모드이지만 몇 가지 팁을 드릴게요. ",
            "지역 기반 검색은 Google Gemini가, ",
            "상세한 리뷰 분석은 GPT-4o가 강점을 보입니다. ",
            "실제 Provider로 전환하시면 더 정확한 추천을 받으실 수 있어요!",
        ],
        "여행": [
            "여행 계획을 세우는 중이시군요! ",
            "DeepSeek은 한국어 여행 정보에 특히 강합니다. ",
            "실제 API를 연결하시면 일정별 상세 추천과 ",
            "교통편, 숙소 정보까지 한 번에 받아보실 수 있습니다.",
        ],
    }

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "demo-model",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        # 사용자 마지막 메시지 내용에 따라 응답 템플릿 선택
        last_user_msg = messages[-1]["content"] if messages else ""
        response_parts = self._select_response(last_user_msg)

        for token in response_parts:
            await asyncio.sleep(0.08)  # 실제 타이핑 속도 시뮬레이션 (80ms)
            yield token

    def _select_response(self, user_input: str) -> List[str]:
        """키워드 기반 응답 템플릿 선택"""
        keywords_map = {
            "코딩": ["코딩", "코드", "프로그래밍", "python", "Python", "개발", "알고리즘", "데코레이터"],
            "맛집": ["맛집", "음식", "파스타", "추천", "레스토랑"],
            "여행": ["여행", "부산", "계획", "일정", "관광"],
        }
        for category, keywords in keywords_map.items():
            if any(kw in user_input for kw in keywords):
                return self.DEMO_RESPONSES[category]
        return self.DEMO_RESPONSES["default"]

    async def get_models(self) -> List[Dict[str, str]]:
        return [
            {"id": "demo-model", "name": "Demo Model", "description": "데모 모드 (API 키 불필요)"},
        ]

    def get_provider_name(self) -> str:
        return "demo"
