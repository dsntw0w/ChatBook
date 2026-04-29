# backend/app/seed.py
"""더미 데이터 시드 스크립트 - 컨테이너 시작 시 자동 실행"""
from app.database import SessionLocal, init_db
from app.models import Conversation, Message, Order, Character, CharacterSettings
from app.config import settings
from app.utils import now_utc
import uuid
from datetime import datetime


def add_seconds(dt: datetime, seconds: int) -> datetime:
    """주어진 datetime에 초를 더한 새 datetime 반환"""
    from datetime import timedelta
    return dt + timedelta(seconds=seconds)


def generate_id():
    return str(uuid.uuid4())


def seed_demo_conversations():
    """더미 대화방 3개 + 메시지 시드"""
    db = SessionLocal()

    # 중복 실행 방지: 대화방이 이미 있으면 스킵
    if db.query(Conversation).count() > 0:
        db.close()
        return

    # --- 대화방 1: 오늘의 코딩 공부 (OpenAI) ---
    conv1_id = generate_id()
    conv1 = Conversation(
        id=conv1_id,
        title="오늘의 코딩 공부",
        provider="openai",
        model="gpt-5-nano",
        created_at=now_utc(),
        updated_at=now_utc()
    )
    db.add(conv1)

    t0 = now_utc()
    messages1 = [
        Message(id=generate_id(), conversation_id=conv1_id, role="user",
                content="Python에서 데코레이터가 뭐야?", created_at=t0),
        Message(id=generate_id(), conversation_id=conv1_id, role="assistant",
                content="데코레이터는 함수나 클래스를 래핑하여 추가 기능을 부여하는 Python의 강력한 기능입니다. @ 기호를 사용하며, 함수를 인자로 받아 새로운 함수를 반환합니다.", created_at=add_seconds(t0, 5)),
        Message(id=generate_id(), conversation_id=conv1_id, role="user",
                content="예제 코드를 보여줘", created_at=add_seconds(t0, 15)),
        Message(id=generate_id(), conversation_id=conv1_id, role="assistant",
                content='```python\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print("Before function call")\n        result = func(*args, **kwargs)\n        print("After function call")\n        return result\n    return wrapper\n\n@my_decorator\ndef say_hello(name):\n    print(f"Hello, {name}!")\n```', created_at=add_seconds(t0, 20)),
        Message(id=generate_id(), conversation_id=conv1_id, role="user",
                content="비동기 함수에도 사용할 수 있어?", created_at=add_seconds(t0, 30)),
        Message(id=generate_id(), conversation_id=conv1_id, role="assistant",
                content="네! 비동기 함수에도 데코레이터를 사용할 수 있습니다. 다만 데코레이터 내부에서 `await`를 사용하려면 데코레이터 자체도 비동기로 작성해야 합니다. `asyncio.coroutine`이나 `async def`로 래퍼를 정의하면 됩니다.", created_at=add_seconds(t0, 35)),
    ]
    for msg in messages1:
        db.add(msg)

    # --- 대화방 2: 맛집 추천 받기 (Gemini) ---
    conv2_id = generate_id()
    conv2 = Conversation(
        id=conv2_id,
        title="맛집 추천 받기",
        provider="gemini",
        model="gemini-2.5-flash-lite",
        created_at=now_utc(),
        updated_at=now_utc()
    )
    db.add(conv2)

    t0 = now_utc()
    messages2 = [
        Message(id=generate_id(), conversation_id=conv2_id, role="user",
                content="서울에서 분위기 좋은 파스타 맛집 추천해줘", created_at=t0),
        Message(id=generate_id(), conversation_id=conv2_id, role="assistant",
                content="서울에는 정말 맛있는 파스타 맛집이 많죠! 분위기 좋은 곳으로 몇 군데 추천해드릴게요:\n\n1. **오스테리아 코** (이태원) - 분위기 좋은 와인바 같은 느낌의 이탈리안\n2. **피오니** (한남동) - 감각적인 인테리어와 수제 파스타\n3. **보나베띠** (청담동) - 고급스러운 분위기의 파인다이닝", created_at=add_seconds(t0, 5)),
        Message(id=generate_id(), conversation_id=conv2_id, role="user",
                content="가격대는 어때?", created_at=add_seconds(t0, 15)),
        Message(id=generate_id(), conversation_id=conv2_id, role="assistant",
                content="가격대를 간략히 요약하면:\n\n- 오스테리아 코: 1인 3~5만원대\n- 피오니: 1인 2~4만원대\n- 보나베띠: 1인 5~8만원대\n\n합리적인 가격을 원하신다면 피오니를 추천드려요!", created_at=add_seconds(t0, 20)),
        Message(id=generate_id(), conversation_id=conv2_id, role="user",
                content="고마워! 예약은 어떻게 해?", created_at=add_seconds(t0, 30)),
    ]
    for msg in messages2:
        db.add(msg)

    # --- 대화방 3: 여행 계획 세우기 (DeepSeek) ---
    conv3_id = generate_id()
    conv3 = Conversation(
        id=conv3_id,
        title="여행 계획 세우기",
        provider="deepseek",
        model="deepseek-chat",
        created_at=now_utc(),
        updated_at=now_utc()
    )
    db.add(conv3)

    t0 = now_utc()
    messages3 = [
        Message(id=generate_id(), conversation_id=conv3_id, role="user",
                content="부산으로 2박 3일 여행 계획 짜줘", created_at=t0),
        Message(id=generate_id(), conversation_id=conv3_id, role="assistant",
                content="부산 2박 3일 여행 계획을 다음과 같이 제안드립니다!\n\n**Day 1:** 해운대 도착 → 해운대 해수욕장 산책 → 더베이101 저녁식사 → 광안대교 야경\n**Day 2:** 감천문화마을 → 자갈치시장 점심 → 태종대 유람선 → 남포동 저녁\n**Day 3:** 해동용궁사 → 기장 해녀촌 점심 → 귀가", created_at=add_seconds(t0, 5)),
        Message(id=generate_id(), conversation_id=conv3_id, role="user",
                content="교통편은 어떻게 되는 게 좋을까?", created_at=add_seconds(t0, 15)),
        Message(id=generate_id(), conversation_id=conv3_id, role="assistant",
                content="부산 내 이동은 지하철 + 버스 + 택시 조합이 가장 효율적입니다. KTX로 부산역 도착 후 지하철 2호선으로 해운대까지 40분 정도 소요됩니다. 감천문화마을은 버스가 편리하고, 태종대는 택시 이용을 추천드려요.", created_at=add_seconds(t0, 20)),
    ]
    for msg in messages3:
        db.add(msg)

    # --- 더미 주문 2개 ---
    order1 = Order(
        id=generate_id(),
        conversation_id=conv1_id,
        status="접수",
        quantity=1,
        cover_style="basic",
        memo="코딩 공부 내용을 책으로 보관하고 싶어요",
        created_at=now_utc(),
        updated_at=now_utc()
    )
    db.add(order1)

    order2 = Order(
        id=generate_id(),
        conversation_id=conv2_id,
        status="제작중",
        quantity=2,
        cover_style="premium",
        memo="선물용으로 2권 부탁드립니다",
        created_at=now_utc(),
        updated_at=now_utc()
    )
    db.add(order2)

    db.commit()
    db.close()
    print("[OK] 더미 데이터 시드 완료: 대화방 3개, 주문 2개")


def seed_demo_provider_data():
    """데모 모드 전용 추가 시드 데이터

    DemoProvider는 demo_service.py에서 하드코딩된 응답 템플릿을 사용하므로
    DB 시드가 필요하지 않습니다. 이 함수는 데모 모드 활성화 확인 및
    향후 데모 전용 시드 데이터(예: 샘플 응답 템플릿, 추가 캐릭터)를
    추가할 수 있는 확장점으로 유지합니다.
    """
    if not settings.USE_DEMO_MODE:
        return

    db = SessionLocal()
    try:
        # 데모 모드 활성화 로그
        print("[DEMO] 데모 모드 활성화: DemoProvider가 응답을 처리합니다.")
        # 향후 데모 전용 데이터 추가 시 이곳에 구현
    finally:
        db.close()


def seed_character_bots():
    """기본 캐릭터봇 시드 - 할머니 동화책 리더"""
    db = SessionLocal()

    # 멱등성: 이미 "할머니" 캐릭터가 있으면 스킵
    existing = db.query(Character).filter(Character.name == "할머니").first()
    if existing:
        db.close()
        return

    # --- 할머니 캐릭터 생성 ---
    character = Character(name="할머니")
    db.add(character)
    db.flush()  # ID 확보

    # --- 캐릭터 설정 ---
    settings_data = CharacterSettings(
        character_id=character.id,
        description=(
            "당신은 70대의 따뜻한 할머니입니다. 손자/손녀를 무척 사랑하며, 어릴 적부터 동화책을 읽어주던 추억이 많습니다. "
            "목소리는 부드럽고 차분하며, 이야기 중간중간 손주를 '우리 아가', '우리 강아지' 같은 애정 어린 호칭으로 부릅니다. "
            "조금은 옛날 말투를 사용하고, 이야기하다가 가끔 추억에 잠기기도 합니다. "
            "모든 이야기에서 교훈을 찾아 손주에게 전달하려 합니다."
        ),
        persona=(
            "당신은 할머니의 사랑스러운 손주입니다. "
            "할머니가 읽어주는 동화책을 무척 좋아하며, 이야기를 들을 때면 호기심이 가득해 중간중간 질문을 하곤 합니다. "
            "할머니를 '할머니~' 하고 애교 있게 부르며, 할머니가 들려주시는 옛날이야기와 추억담을 즐겨 듣습니다. "
            "때로는 재미있었던 이야기를 또 해달라고 조르기도 하고, 동화 속 등장인물에 대해 궁금한 점을 물어보기도 합니다."
        ),
        prompt=(
            "# 역할\n"
            "{{description}}\n\n"
            "# 상대방\n"
            "당신이 대화를 나누는 상대방은 다음과 같습니다:\n"
            "{{persona}}\n\n"
            "위 설명에 따라 당신은 손주에게 동화책을 읽어주는 따뜻한 할머니 역할을 완벽하게 수행해야 합니다.\n\n"

            "## 말투와 표현\n"
            "- 부드럽고 다정한 어투를 사용하며, 문장 끝을 '~하렴', '~한단다', '~그랬단다', "
            "'~하겠니' 같은 옛날식 정겨운 표현으로 끝내세요.\n"
            "- 손주를 부를 때는 '우리 아가', '우리 강아지', '우리 예쁜이' 같은 "
            "애정 어린 호칭을 자주 사용하세요.\n"
            "- 중간중간 '어머나', '아이고', '그래...', '참...' 같은 감탄사를 "
            "자연스럽게 섞어주세요.\n"
            "- 서두를 때는 '얼른', '냉큼', '어서' 같은 표현을 쓰고, "
            "이야기를 시작할 때는 '옛날 옛날 아주 먼 옛날에...' 같은 "
            "전통적인 동화 구연 방식을 사용하세요.\n\n"

            "## 동화 읽기 방식\n"
            "- 손주가 특정 동화를 요청하면 그 동화를 들려주세요. "
            "요청이 없으면 스스로 재미있는 동화 하나를 골라 들려주세요.\n"
            "- 이야기를 들려줄 때는 장면을 생생하게 묘사하고, "
            "등장인물마다 목소리 톤을 살짝 바꾸며 읽어주는 느낌을 주세요.\n"
            "- 이야기 중간중간 '우리 아가는 이 주인공이 어떻게 했으면 좋겠니?' "
            "같은 질문을 건네며 손주를 이야기에 참여시키세요.\n"
            "- 이야기가 끝나면 반드시 손주에게 "
            "'또 다른 이야기를 들려줄까, 아니면 이 이야기에 대해 얘기해볼까?' "
            "라고 물어봐 주세요.\n\n"

            "## 추억 회상\n"
            "- 가끔 동화 내용과 관련된 자신의 어린 시절 추억을 자연스럽게 꺼내세요. "
            "예: '할머니가 어릴 때는 말이야...', "
            "'옛날에 우리 할머니가 해주셨던 이야기인데...'\n"
            "- 추억 이야기는 너무 길게 하지 말고, 동화의 흐름을 끊지 않도록 "
            "짧게 한두 문장 정도만 하세요.\n\n"

            "## 교훈\n"
            "- 모든 동화가 끝난 후에는 그 이야기에서 배울 수 있는 교훈을 "
            "손주에게 자연스럽게 전달하세요. "
            "예: '이 이야기는 우리 아가에게 말이야, 친구를 소중히 여기라는 뜻이란다.'\n"
            "- 교훈은 훈계조가 아니라 부드러운 권유나 다정한 설명으로 전달하세요.\n\n"

            "## 주의사항\n"
            "- 무섭거나 잔인한 내용의 동화는 피하고, "
            "항상 따뜻하고 희망적인 이야기를 들려주세요.\n"
            "- 손주의 나이를 알 수 없으니, 너무 유치하거나 너무 어려운 표현은 피하고 "
            "누구나 이해할 수 있는 쉬운 우리말을 사용하세요.\n"
            "- 절대 손주에게 화내거나 짜증 내지 말고, "
            "항상 무한한 인내심과 사랑으로 대해주세요."
        ),
    )
    db.add(settings_data)

    db.commit()
    db.close()
    print("[OK] 캐릭터봇 시드 완료: 할머니 (동화책 읽어주는 할머니)")


if __name__ == "__main__":
    init_db()
    seed_demo_conversations()
    seed_demo_provider_data()
    seed_character_bots()
