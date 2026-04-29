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

    # 키워드 매칭 규칙: (카테고리, 키워드목록, 우선순위_가중치)
    # 가중치가 높은 카테고리가 우선 매칭됩니다. 이를 통해 "부산 코딩 캠프" 같은
    # 다중 매칭 시에도 dict 순서가 아닌 명시적 가중치로 우선순위가 결정됩니다.
    KEYWORD_RULES: list[tuple[str, list[str], int]] = [
        ("코딩", ["코딩", "코드", "프로그래밍", "python", "Python", "개발", "알고리즘", "데코레이터"], 3),
        ("맛집", ["맛집", "음식", "파스타", "추천", "레스토랑"], 2),
        ("여행", ["여행", "부산", "계획", "일정", "관광"], 2),
    ]

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "demo-model",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        # 최근 사용자 메시지들을 수집하여 맥락 기반 응답 선택
        # (마지막 메시지뿐 아니라 이전 대화 맥락도 함께 고려)
        user_messages = [m["content"] for m in messages if m.get("role") == "user"]
        combined_input = " ".join(user_messages[-3:]) if user_messages else ""
        response_parts = self._select_response(combined_input)

        for token in response_parts:
            await asyncio.sleep(0.08)  # 실제 타이핑 속도 시뮬레이션 (80ms)
            yield token

    def _select_response(self, user_input: str) -> List[str]:
        """가중치 기반 키워드 매칭으로 응답 템플릿 선택.

        KEYWORD_RULES의 각 규칙을 순회하며 매칭되는 카테고리 중
        가장 높은 가중치를 가진 카테고리를 선택합니다.
        가중치가 같으면 먼저 정의된 규칙이 우선합니다.
        """
        best_category: str | None = None
        best_weight = 0
        for category, keywords, weight in self.KEYWORD_RULES:
            if any(kw in user_input for kw in keywords) and weight > best_weight:
                best_category = category
                best_weight = weight
        if best_category is not None:
            return self.DEMO_RESPONSES[best_category]
        return self.DEMO_RESPONSES["default"]

    async def get_models(self) -> List[Dict[str, str]]:
        # NOTE: 데모 Provider는 항상 단일 모델만 제공합니다.
        # 실제 Provider로 전환 시 해당 Provider의 get_models()가 사용됩니다.
        return [
            {"id": "demo-model", "name": "Demo Model", "description": "데모 모드 (API 키 불필요)"},
        ]

    def get_provider_name(self) -> str:
        return "demo"
