# 📖 ChatBook — AI 대화를 책으로

> **AI 캐릭터와 대화하며 콘텐츠를 만들고, 원하는 대화를 모아 책으로 주문할 수 있는 풀스택 웹 애플리케이션**

ChatBook은 OpenAI, Google Gemini, DeepSeek 등 다양한 AI와의 대화를 하나의 플랫폼에서 경험하고, 그 대화 콘텐츠를 책으로 주문·관리·내보낼 수 있는 서비스입니다.

---

## 📋 목차

1. [서비스 소개](#1-서비스-소개)
2. [Docker 실행 방법](#2-docker-실행-방법)
3. [완성한 레벨 및 구현 내용](#3-완성한-레벨-및-구현-내용)
4. [기술 스택 및 아키텍처](#4-기술-스택-및-아키텍처)
5. [AI 도구 사용 내역](#5-ai-도구-사용-내역)
6. [설계 의도](#6-설계-의도)
7. [API 엔드포인트](#7-api-엔드포인트)
8. [데이터베이스 모델](#8-데이터베이스-모델)
9. [테스트](#9-테스트)
10. [라이선스](#10-라이선스)
11. [PDF 제출 체크리스트](#11-pdf-제출-체크리스트)

---

## 1. 서비스 소개

### 1.1 한 줄 설명

**ChatBook**은 AI 캐릭터와 자유롭게 대화하고, 그 대화를 콘텐츠로 저장하여 책으로 주문·내보낼 수 있는 풀스택 웹 애플리케이션입니다.

### 1.2 타겟 사용자

| 사용자 유형 | 이용 시나리오 |
|-------------|---------------|
| 💻 **학습자·개발자** | AI와 코딩 공부 대화를 기록하고, 학습 노트로 책 제작 |
| 🍽️ **일반 사용자** | AI에게 맛집·여행 추천을 받고, 그 대화를 개인 가이드북으로 |
| 👵 **스토리텔링 애호가** | 캐릭터봇(할머니 동화책 리더 등)과의 롤플레잉 대화를 동화책으로 |
| 📚 **콘텐츠 큐레이터** | 다양한 주제의 AI 대화를 모아 큐레이션 북 제작 |

### 1.3 주요 기능

| 레벨 | 기능 | 설명 |
|------|------|------|
| **Lv1** | 🤖 AI 캐릭터 채팅 | 3종 AI Provider + 데모 모드, SSE 스트리밍, 다크모드 |
| **Lv1+** | 🎭 RP 캐릭터봇 | 할머니 동화책 리더 캐릭터, 설정 편집, 변수 치환 프롬프트 |
| **Lv2** | 📦 책 주문 관리 | 대화방 → 책 주문, 상태 머신(접수→제작중→완료), 중복 방지 |
| **Lv3** | 📤 데이터 익스포트 | JSON/ZIP 형식, 주문+대화+캐릭터 데이터 구조화 내보내기 |

> **핵심 차별점**: `USE_DEMO_MODE=true` 기본 활성화로 API 키 없이 `docker compose up -d` 한 줄로 모든 기능 체험 가능. DemoProvider가 키워드 기반 목업 응답을 생성하며, 멱등적 시드 데이터(대화방 3개, 주문 2개, 캐릭터봇 1개)가 자동 생성되어 실행 직후 바로 서비스를 확인할 수 있습니다.

---

## 2. Docker 실행 방법

### 2.1 사전 준비사항

- **Docker Desktop** 설치 ([docker.com](https://www.docker.com/products/docker-desktop))
- 호스트 머신에서 **8000번**(백엔드), **3000번**(프론트엔드) 포트가 사용 가능해야 함

### 2.2 빠른 실행

#### Windows
```batch
cd chatbook
start-docker.bat
```
start-docker.bat을 더블클릭하면 Docker 설치 확인 → .env 자동 준비 → 이미지 빌드 → 컨테이너 실행 → 브라우저 자동 실행이 한 번에 처리됩니다.

#### macOS / Linux
```bash
cd chatbook
cp .env.example .env      # macOS/Linux
docker compose up -d
```

#### Windows (터미널에서 수동 실행)
```batch
cd chatbook
copy .env.example .env    # Windows
docker compose up -d
```

> 💡 `.env` 파일이 없으면 데모 모드로 자동 실행됩니다. `.env.example`을 복사하면 기본 설정이 적용됩니다.

- **Frontend**: http://localhost:3000
- **Backend API 문서 (Swagger)**: http://localhost:8000/docs

### 2.3 데모 모드 vs 일반 모드

#### 🎮 데모 모드 (기본)
`.env` 파일에서 `USE_DEMO_MODE=true` (기본값)로 설정하면 **API 키 없이** AI 챗봇, 주문 관리, RP 캐릭터봇 등 모든 기능을 체험할 수 있습니다.

- DemoProvider가 키워드 기반 목업 응답을 자동 생성 (5개 응답 템플릿, 80ms 타이핑 지연 시뮬레이션)
- 시작 시 대화방 3개, 주문 2개, 캐릭터봇 1개의 멱등적 시드 데이터 자동 생성
- 외부 API 호출이 전혀 발생하지 않아 네트워크 제한 환경에서도 동작
- DemoProvider는 ProviderRegistry에 최우선 등록되며, 실제 API 키가 있으면 demo + real 병존

```bash
# .env 파일 없이 바로 실행 (기본값 USE_DEMO_MODE=true)
docker compose up -d
```

#### 🚀 일반 모드 (실제 AI 사용)
실제 AI 서비스(OpenAI, Gemini, DeepSeek)를 사용하려면 API 키를 설정하고 데모 모드를 비활성화합니다.

```bash
# .env 파일 편집
copy .env.example .env      # Windows
# 또는 cp .env.example .env  # macOS/Linux

# .env 파일에 API 키 입력 후 USE_DEMO_MODE=false 설정
# OPENAI_API_KEY=sk-your-real-key
# GEMINI_API_KEY=your-real-key
# DEEPSEEK_API_KEY=your-real-key
# USE_DEMO_MODE=false

docker compose up -d
```

> `USE_DEMO_MODE=false`로 설정하고 API 키를 하나라도 등록하면, 등록된 Provider는 실제 API를 사용하고 등록되지 않은 Provider는 DemoProvider가 자동 폴백합니다. 또한 사용자는 프론트엔드 UI에서 자신의 API 키를 직접 입력할 수 있으며, 이때 `create_provider_instance()`가 요청별 동적 Provider 인스턴스를 생성합니다. 이를 통해 **서버 관리자 키(ProviderRegistry) + 사용자 개인 키(create_provider_instance)** 의 이중 Provider 소스가 동시에 운영됩니다.

### 2.4 통합 테스트 실행

```batch
# Windows
test-docker.bat

# macOS/Linux
bash test-docker.sh
```

5단계 검증(Backend Health → Frontend 접근 → Models API → Conversations API → Orders API)을 자동으로 수행합니다.

### 2.5 환경변수 설정

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `OPENAI_API_KEY` | `sk-dummy` | OpenAI API 키 |
| `GEMINI_API_KEY` | `gemini-dummy` | Google Gemini API 키 |
| `DEEPSEEK_API_KEY` | `deepseek-dummy` | DeepSeek API 키 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek 커스텀 엔드포인트 |
| `USE_DEMO_MODE` | `true` | 데모 모드 활성화 여부 |
| `CORS_ORIGINS` | `http://localhost:3000` | CORS 허용 도메인 |
| `DATABASE_URL` | `sqlite:///app/data/chatbook.db` | SQLite DB 경로 |

> ⚠️ **Docker 배포 시**: `NEXT_PUBLIC_API_URL`은 프로젝트 루트의 `.env` 파일에 설정해야 `docker compose build` 시 반영됩니다. `frontend/.env.local`은 로컬 개발(`pnpm dev`) 전용입니다.

### 2.6 포트 변경

`.env` 파일에서 아래 변수를 설정하세요:

```bash
BACKEND_PORT=8080
FRONTEND_PORT=4000
```

### 2.7 서비스 중지

```bash
docker compose down          # 서비스 중지 (데이터 유지)
docker compose down -v       # DB 데이터까지 완전 삭제
```

### 2.8 문제해결 (Troubleshooting)

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `port is already allocated` | 포트 충돌 | `.env`에서 `BACKEND_PORT`, `FRONTEND_PORT` 변경 (섹션 2.6 참조) |
| `docker daemon is not running` | Docker Desktop 미실행 | Docker Desktop을 먼저 실행 |
| `'cp'은(는) 내부 또는 외부 명령...` | Windows에서 Unix 명령어 사용 | `copy .env.example .env` 사용 |
| `WSL 2 installation is incomplete` | WSL2 미설치 | 관리자 PowerShell에서 `wsl --update` 실행 후 재부팅 |
| `Cannot locate specified Dockerfile` | 구버전 Docker Compose | `docker compose` (v2) 사용, 또는 Docker Desktop 업데이트 |
| 빌드 중 메모리 부족 | Docker 메모리 부족 | Docker Desktop 설정 → Resources → Memory 증가 |
| 한글 깨짐 | 터미널 인코딩 | `chcp 65001` 실행 (UTF-8) |
| 프론트엔드 접속 불가 | 백엔드 미실행 | `docker compose logs backend` 로그 확인 |

---

## 3. 완성한 레벨 및 구현 내용

### Lv1 — 🤖 AI 캐릭터 채팅 (핵심 서비스)

> **평가 포인트: 서비스 플로우 완성도** — AI Provider 선택부터 SSE 스트리밍 응답, 대화 저장까지 전체 플로우가 끊김 없이 작동합니다.

| 구현 항목 | 상세 내용 |
|-----------|-----------|
| **멀티 Provider** | OpenAI(GPT-5 Nano, GPT-4.1 Nano), Google Gemini(2.5 Flash Lite, 3.1 Flash Lite Preview), DeepSeek(Chat, Reasoner) 3종 + 데모 모드 |
| **SSE 스트리밍** | Server-Sent Events로 토큰 단위 실시간 응답, `text/event-stream` 기반. FastAPI `StreamingResponse` + 제너레이터 패턴으로 구현 |
| **대화방 CRUD** | 생성·목록·상세·제목 수정·삭제, `updated_at` 기반 정렬, N+1 방지 서브쿼리 |
| **마크다운 렌더링** | `react-markdown`으로 코드 블록·리스트·강조 등 풀 마크다운 지원. 불완전한 스트리밍 마크다운 파싱 오류 시 일반 텍스트 폴백 |
| **낙관적 업데이트 (Optimistic Update)** | 사용자 메시지 전송 즉시 UI 반영, `SWR mutate(revalidate=false)`로 즉시 갱신 후 서버 응답 시 revalidate |
| **다크모드** | `next-themes` 기반, 시스템 테마 연동, CSS 변수 팔레트, Hydration mismatch 방지 (마운트 전까지 투명 처리) |
| **인라인 편집** | 대화방/캐릭터 제목 더블클릭 → 인라인 편집, Enter 저장 / Escape 취소 |
| **에러 복구** | Stale cache 404 자동 복구 (localStorage 세션-대화 매핑 재생성), Corrupted cache 감지 및 복구, ErrorBoundary 적용 |

#### Lv1+ — 🎭 RP 캐릭터봇 시스템 (추가 구현)

| 구현 항목 | 상세 내용 |
|-----------|-----------|
| **캐릭터 CRUD** | 생성·목록·상세·이름 수정·삭제, 중복 이름 자동 접미사 부여 ("이름" → "이름 (1)" → "이름 (2)") |
| **세션 관리** | 캐릭터별 대화 세션 생성·삭제, localStorage 기반 세션-대화 매핑 캐시 (페이지 새로고침 후에도 유지) |
| **설정 시스템** | Description(캐릭터 설명), Persona(사용자 역할), Lorebook(세계관), Prompt(커스텀 프롬프트) 4종 |
| **변수 치환** | `{{description}}`, `{{persona}}`, `{{lorebook}}` → 실제 설정값으로 자동 치환. 커스텀 프롬프트 없으면 기본 템플릿 자동 생성 |
| **기본 캐릭터** | "할머니" — 동화책을 읽어주는 70대 할머니 RP 봇 (말투·호칭·추억·교훈 포함) |
| **UI** | 아코디언 사이드바 (캐릭터/채팅방 탭), 설정 패널, 인라인 이름 편집 |

### Lv2 — 📦 책 주문 관리

> **평가 포인트: 비즈니스 로직** — 주문 상태 머신(서버 측 삼중 검증), 중복 주문 방지, 낙관적 업데이트+롤백 등 안정적인 비즈니스 로직이 작동합니다.

| 구현 항목 | 상세 내용 |
|-----------|-----------|
| **주문 CRUD** | 생성·목록·상세·취소, 주문 정보(수량, 표지 스타일, 메모) 저장 |
| **상태 머신** | `접수 → 제작중 → 완료`, `접수 → 취소`, `제작중 → 접수` (제작 취소). 완료·취소 상태는 불변 |
| **삼중 서버 검증** | ① DB CHECK 제약 (`status IN ('접수','제작중','완료','취소')`) ② Pydantic 정규식 검증 ③ `valid_transitions` 딕셔너리로 허용된 상태 전이만 허용, 위반 시 400 |
| **중복 방지** | 동일 대화방에 대해 접수/제작중 상태의 주문이 이미 있으면 409 Conflict. 완료·취소된 주문은 재주문 허용 |
| **N+1 방지** | 주문 목록 조회 시 Orders → Conversations → Characters 3단계 벌크 조회 (`WHERE id IN (...)`) |
| **낙관적 업데이트 + 이중 캐시 롤백** | 상태 변경/취소 시 상세 캐시와 목록 캐시를 동시에 즉시 갱신. 서버 오류 발생 시 `prevData`로 자동 롤백 |
| **캐릭터 연동** | Message.session_id → ChatSession → Character 경로로 캐릭터 이름 자동 조회 |

### Lv3 — 📤 데이터 익스포트

> **평가 포인트: 데이터 모델링과 직렬화 능력** — 주문 1건에 필요한 모든 데이터(주문+대화+캐릭터)를 구조화하여 JSON/ZIP으로 한 번에 내보냅니다.

| 구현 항목 | 상세 내용 |
|-----------|-----------|
| **JSON 익스포트** | 주문 + 대화(전체 메시지 포함) + 캐릭터 정보를 구조화된 JSON으로 내보내기 |
| **ZIP 익스포트** | `order.json` + `conversation.json` + `conversation.txt`(읽기 쉬운 텍스트) 포함. `io.BytesIO` + `zipfile.ZIP_DEFLATED`로 인메모리 처리 |
| **datetime 직렬화** | SQLAlchemy `datetime` 객체 → ISO 8601 문자열로 재귀 변환 |
| **TXT 변환** | 역할 라벨(사용자/AI), 타임스탬프, 내용을 사람이 읽기 쉬운 텍스트 형식으로 생성 |
| **파일명 체계** | `order_{order_id}.zip` / `order_{order_id}/` 디렉토리 구조 |

---

## 4. 기술 스택 및 아키텍처

### 4.1 기술 스택

| 계층 | 기술 | 버전 | 역할 |
|------|------|------|------|
| **Frontend** | Next.js (App Router) | 16.2 | 서버 컴포넌트, SSR, Rewrite 프록시 |
| | React | 19.2 | UI 라이브러리 |
| | TypeScript | 5 | 정적 타입 시스템 |
| | Tailwind CSS | v4 | 유틸리티 퍼스트 CSS |
| | SWR | 2.2 | 데이터 페칭·캐싱 |
| | react-markdown | 9 | AI 응답 마크다운 렌더링 |
| | next-themes | 0.4 | 다크모드 관리 |
| **Backend** | FastAPI | 0.115 | 비동기 REST API |
| | Python | 3.12 | 런타임 |
| | SQLAlchemy | 2.0 | ORM |
| | Pydantic | 2 | 데이터 검증·직렬화 |
| | uvicorn | - | ASGI 서버 |
| **Database** | SQLite | - | 파일 기반 관계형 DB |
| **AI** | OpenAI SDK | - | GPT 모델 연동 |
| | Google GenAI SDK | - | Gemini 모델 연동 |
| | OpenAI SDK (DeepSeek) | - | DeepSeek 호환 API 연동 |
| **Infra** | Docker | - | 컨테이너화 |
| | Docker Compose | - | 멀티 서비스 오케스트레이션 |

### 4.2 기술 선택 이유

| 기술 | 선택 이유 |
|------|-----------|
| **Next.js 16 + App Router** | 서버 컴포넌트로 초기 로딩 최적화, `rewrites`로 백엔드 프록시 → CORS 문제 근본적 해결, SSE 스트리밍은 `NEXT_PUBLIC_API_URL`로 백엔드 직접 호출(rewrites 버퍼링 우회), `output: 'standalone'`으로 Docker 배포 간소화 |
| **React 19 + TypeScript** | 생태계 성숙도·커뮤니티·자료 풍부, 엄격한 타입 시스템으로 런타임 오류 사전 방지, `strict: true`로 풀 퀄리티 보장 |
| **Tailwind CSS v4** | 유틸리티 클래스 기반 빠른 프로토타이핑, CSS 변수와 혼용해 일관된 디자인 토큰, 다크모드 `class` 전략 네이티브 지원 |
| **SWR** | stale-while-revalidate 전략으로 UX 향상, `mutate`를 통한 낙관적 업데이트, `useSWRMutation`으로 변경 액션 캐시 무효화 자동화 |
| **FastAPI** | 비동기 네이티브 지원으로 SSE 스트리밍에 최적화, Pydantic 통합으로 요청·응답 자동 검증, `/docs` 자동 생성으로 API 문서화 비용 제로 |
| **SQLAlchemy 2.0 + SQLite** | Python ORM 표준, dialect 변경만으로 PostgreSQL 등으로 전환 가능, SQLite로 별도 DB 서버 없이 파일 기반 운영 → Docker 볼륨 마운트로 영속화 |
| **Provider 추상화 패턴** | AIProvider ABC → OpenAICompatibleService → 구현체 구조로 신규 Provider 추가 비용 최소화, DemoProvider로 API 키 없이도 전체 플로우 테스트 가능 |
| **Docker + Docker Compose** | 멀티스테이지 빌드로 이미지 최적화, `docker compose up -d` 한 줄로 전체 스택 구동, 환경변수 기반 설정으로 이식성 극대화 |

### 4.3 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (:3000)                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Next.js Frontend (React 19 + TypeScript)                  │  │
│  │                                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐           │  │
│  │  │ ChatScreen│ │OrderPages│ │Sidebar(Characters)│           │  │
│  │  └─────┬────┘ └────┬─────┘ └────────┬─────────┘           │  │
│  │        │            │               │                      │  │
│  │  ┌─────┴────────────┴───────────────┴───────────────────┐  │  │
│  │  │  SWR Hooks + SSE Client + API Client                 │  │  │
│  │  └───────────────┬──────────────────┬───────────────────┘  │  │
│  └──────────────────┼──────────────────┼──────────────────────┘  │
│                     │                  │                          │
│     /api/* (rewrites)│                  │SSE 직접 호출             │
│     (REST API)       │                  │(NEXT_PUBLIC_API_URL)    │
└─────────────────────┼──────────────────┼─────────────────────────┘
                      │                  │
              Docker Network              │
                      │                  │
┌─────────────────────┼──────────────────┼─────────────────────────┐
│          Backend Container (:8000)      │                         │
│  ┌──────────────────┴──────────────────┴──────────────────────┐  │
│  │  FastAPI Application                                       │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌───────────┐  ┌────────────────┐          │  │
│  │  │ Routes   │  │ Schemas   │  │ Models (ORM)   │          │  │
│  │  │ chat.py  │  │ (Pydantic)│  │ Conversation   │          │  │
│  │  │ orders.py│  │           │  │ Message        │          │  │
│  │  │ export.py│  │           │  │ Order          │          │  │
│  │  │character.│  │           │  │ Character      │          │  │
│  │  │ py       │  │           │  │ ChatSession    │          │  │
│  │  └─────┬────┘  └───────────┘  └───────┬────────┘          │  │
│  │        │                               │                   │  │
│  │  ┌─────┴───────────────────────────────┴────────────────┐  │  │
│  │  │  AI Services (Provider Pattern)                      │  │  │
│  │  │                                                      │  │  │
│  │  │  AIProvider (ABC)                                    │  │  │
│  │  │  ├── DemoProvider     (키워드 응답)                  │  │  │
│  │  │  ├── OpenAICompatibleService (ABC)                   │  │  │
│  │  │  │   ├── OpenAIService   (OpenAI SDK)                │  │  │
│  │  │  │   └── DeepSeekService (OpenAI SDK)                │  │  │
│  │  │  └── GeminiService    (Google GenAI SDK)             │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └───────────────────────┬────────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────┴────────────────────────────────────┐  │
│  │  SQLite (./data/chatbook.db)                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.4 Provider 추상화 패턴

```
                    AIProvider (ABC)
                    │  stream_chat()
                    │  get_models()
                    │  get_provider_name()
                    │
    ┌───────────────┼──────────────────┐
    │               │                  │
DemoProvider  OpenAICompatible    GeminiService
(키워드 매칭)  Service (ABC)      (google-genai SDK)
               │
        ┌──────┴──────┐
        │              │
   OpenAIService  DeepSeekService
   (openai SDK)   (openai SDK + custom base_url)
```

**ProviderRegistry** (Monostate 싱글톤)가 모든 Provider 인스턴스를 관리합니다.

- `USE_DEMO_MODE=true` → DemoProvider 등록 + 실제 키 있으면 함께 등록 (demo + real 병존)
- `USE_DEMO_MODE=false` → 실제 Provider만 등록, 없으면 DemoProvider 폴백

**이중 Provider 소스**: 서버 환경변수로 등록된 Provider(ProviderRegistry)와 사용자가 UI에서 직접 입력한 API 키로 생성된 Provider(`create_provider_instance()`)가 동시에 운영됩니다. 사용자는 자신의 API 키를 프론트엔드에서 입력하여 개인 과금으로 AI 서비스를 이용할 수 있습니다.

### 4.5 핵심 아키텍처 결정사항

| # | 결정 | 설명 |
|---|------|------|
| **1** | **계층적 Provider 상속** | `AIProvider`(ABC) → `OpenAICompatibleService`(ABC) → `OpenAIService` / `DeepSeekService`. OpenAI와 DeepSeek가 동일한 `stream_chat()` 구현을 공유하여 코드 중복을 제거했습니다. 새 Provider 추가 시 5줄 이내로 구현 가능합니다. |
| **2** | **Gemini system role 우회** | Gemini API는 system role을 지원하지 않습니다. 이를 `[System Instructions]` 프리픽스를 첫 번째 user 메시지 앞에 병합하는 방식으로 해결했습니다. `_convert_messages()`가 OpenAI 형식의 메시지를 Gemini Contents 형식으로 변환하며 system 메시지를 자동 병합합니다. |
| **3** | **SSE StreamingResponse + 별도 DB 세션** | `StreamingResponse`는 제너레이터 실행 전에 응답이 먼저 반환되므로 요청 스코프 DB 세션이 이미 종료된 상태입니다. 이 문제를 `SessionLocal()`로 격리된 별도 DB 세션을 생성하여 AI 응답을 저장하고 `finally` 블록에서 정리하는 패턴으로 해결했습니다. |
| **4** | **SSE rewrite 우회** | Next.js의 `rewrites`가 스트리밍 응답을 버퍼링/변형하는 문제를 피하기 위해, SSE 요청만 `NEXT_PUBLIC_API_URL`로 백엔드를 직접 호출합니다. 일반 REST API는 `rewrites`를 통한 프록시를 사용합니다. |
| **5** | **Non-root Docker + 멀티스테이지 빌드** | 프론트엔드는 3-스테이지 빌드(builder → production deps → runner)로 최종 이미지에 빌드 도구를 제외하고 standalone output만 포함합니다. 백엔드도 멀티스테이지로 빌드됩니다. 모든 컨테이너는 non-root 사용자(`nextjs`, uid 1001)로 실행되어 보안을 강화했습니다. |
| **6** | **SWR 낙관적 업데이트 + 이중 캐시 롤백** | 주문 상태 변경 시 상세 캐시와 목록 캐시를 동시에 즉시 갱신(Optimistic Update)합니다. 서버 요청 실패 시 `prevData`를 사용해 두 캐시 모두 원래 상태로 자동 롤백하여 데이터 정합성을 보장합니다. |
| **7** | **멱등적 시드 데이터 + DemoProvider 자동 폴백** | `seed.py`는 테이블이 비어 있을 때만 실행되는 멱등적 설계로, 컨테이너 재시작 시에도 데이터가 중복 생성되지 않습니다. `USE_DEMO_MODE=false`이고 API 키가 없는 Provider는 DemoProvider가 자동 폴백합니다. |
| **8** | **DB CHECK + Pydantic + API 삼중 검증** | 주문 상태와 메시지 role에 대해 DB CHECK 제약, Pydantic 정규식 검증, API `valid_transitions` 딕셔너리 검증의 3단계 방어(Belt-and-Suspenders)를 적용했습니다. |

### 4.6 프로젝트 디렉토리 구조

```
chatbook/
├── docker-compose.yml              # 2-서비스 오케스트레이션 (healthcheck 의존성)
├── Dockerfile.frontend             # Next.js 3-스테이지 멀티스테이지 빌드
├── .env.example                    # 환경변수 템플릿
├── .gitignore                      # Git 추적 제외 규칙
├── setup.bat / start.bat           # 로컬 개발 (Portable Python/Node.js)
├── start-docker.bat                # Docker 실행 (Windows)
├── test-docker.bat / test-docker.sh # Docker 통합 테스트
├── clean.bat                       # 프로젝트 초기화
│
├── backend/                        # FastAPI (Python 3.12)
│   ├── Dockerfile                  # 백엔드 컨테이너 (멀티스테이지)
│   ├── requirements.txt            # Python 의존성
│   ├── pytest.ini                  # pytest 설정
│   ├── tests/                      # 백엔드 테스트 (24개 케이스)
│   │   ├── conftest.py             # Fixture, 인메모리 SQLite
│   │   ├── test_chat_api.py        # 대화방 API (6개)
│   │   ├── test_orders_api.py      # 주문 API (7개)
│   │   ├── test_export_api.py      # 익스포트 API (3개)
│   │   └── test_providers.py       # Provider 단위 (8개)
│   └── app/
│       ├── main.py                 # 진입점 (lifespan, CORS, 예외 핸들러)
│       ├── config.py               # Pydantic Settings (환경변수)
│       ├── database.py             # SQLAlchemy 엔진·세션
│       ├── schemas.py              # 15+ Pydantic 요청·응답 스키마
│       ├── seed.py                 # 멱등적 더미 데이터 (대화방 3, 주문 2, 캐릭터 1)
│       ├── models/                 # SQLAlchemy ORM 모델
│       │   ├── conversation.py     # Conversation, Message
│       │   ├── order.py            # Order
│       │   └── character.py        # Character, ChatSession, CharacterSettings
│       ├── routes/                 # API 라우터
│       │   ├── chat.py             # 대화방 CRUD + SSE 채팅
│       │   ├── orders.py           # 주문 CRUD + 상태 머신
│       │   ├── export.py           # JSON/ZIP 익스포트
│       │   └── character.py        # 캐릭터 CRUD + 세션·설정
│       └── services/               # AI Provider 계층
│           ├── __init__.py         # ProviderRegistry + init_providers() + create_provider_instance()
│           ├── base.py             # AIProvider (ABC)
│           ├── base_ai_service.py  # OpenAICompatibleService (ABC)
│           ├── demo_service.py     # DemoProvider (키워드 응답)
│           ├── openai_service.py   # OpenAIService
│           ├── gemini_service.py   # GeminiService (system role 병합, Contents 변환)
│           └── deepseek_service.py # DeepSeekService
│
├── data/                           # SQLite DB 파일 (Docker 볼륨 마운트)
│   └── .gitkeep
│
└── frontend/                       # Next.js 16 (TypeScript)
    ├── .env.local                  # 프론트엔드 전용 환경변수 (NEXT_PUBLIC_API_URL)
    ├── package.json                # 의존성 + 스크립트
    ├── next.config.ts              # standalone + rewrites
    ├── tailwind.config.ts          # Tailwind v4 + dark mode
    ├── tsconfig.json               # TypeScript (strict)
    ├── vitest.config.ts            # Vitest (jsdom)
    ├── app/                        # App Router
    │   ├── layout.tsx              # 루트 레이아웃 (ThemeProvider, ErrorBoundary)
    │   ├── page.tsx                # 메인 채팅 페이지
    │   ├── globals.css             # Tailwind + CSS 변수 + 스크롤바
    │   ├── error.tsx               # Next.js 에러 페이지
    │   ├── loading.tsx             # 로딩 스켈레톤
    │   ├── not-found.tsx           # 404 페이지
    │   └── orders/                 # 주문 페이지 (/orders)
    │       ├── page.tsx            # 주문 목록
    │       └── [id]/page.tsx       # 주문 상세
    ├── components/
    │   ├── Chat/                   # ChatScreen, Message, MessageInput,
    │   │                           # ProviderSelector, StreamingText
    │   ├── Sidebar/                # CharacterList, CharacterItem,
    │   │                           # CharacterSettingsPanel, ChatList,
    │   │                           # ConversationItem
    │   ├── Orders/                 # OrderList, OrderDetail, OrderForm,
    │   │                           # ExportButton
    │   ├── Layout/                 # Header, ThemeToggle
    │   └── ui/                     # ErrorBoundary, Spinner, Modal, Badge
    ├── hooks/                      # SWR 기반 커스텀 훅
    │   ├── useChat.ts              # 대화방 CRUD
    │   ├── useStreamingChat.ts     # SSE 스트리밍 (AbortController, 낙관적 업데이트)
    │   ├── useOrders.ts            # 주문 CRUD (이중 캐시 낙관적 업데이트+롤백)
    │   └── useApiKeys.ts           # API 키 localStorage 관리
    ├── providers/                  # React Context
    │   ├── theme-provider.tsx      # next-themes 래퍼
    │   └── provider-context.tsx    # AI Provider/Model 전역 상태
    ├── lib/                        # API 클라이언트 + 타입
    │   ├── api.ts                  # fetchApi + ApiError + SSE 파서
    │   └── types.ts                # TypeScript 타입 정의 (단일 진실 공급원)
    └── __tests__/                  # Vitest (jsdom)
        ├── setup.ts
        ├── ChatScreen.test.tsx     # 스모크 테스트
        └── OrderForm.test.tsx      # 모달 렌더링 테스트
```

---

## 5. AI 도구 사용 내역

이 프로젝트는 "바이브코딩(Vibe Coding)" 방식으로 개발되었으며, 아래 AI 도구를 적극적으로 활용했습니다.

| AI 도구 | 주요 활용 내용 | 활용 구간 |
|---------|---------------|-----------|
| **Roo Code** (VS Code Extension) | 전체 아키텍처 설계, Strategy + Template Method Provider 패턴 구상, ERD 데이터 모델링, SSE 스트리밍 파이프라인 설계, 프로젝트 디렉토리 구조 기획 | 프로젝트 초기 기획·설계 |
| **Roo Code** (VS Code Extension) | FastAPI 백엔드 구현 (config.py, database.py, main.py, schemas.py, seed.py) | 백엔드 코어 인프라 |
| **Roo Code** (VS Code Extension) | AI Provider 계층 구현 (base.py, base_ai_service.py, openai/gemini/deepseek/demo_service.py, ProviderRegistry, create_provider_instance) | AI Provider 레이어 |
| **Roo Code** (VS Code Extension) | API 라우트 구현 (chat.py SSE 스트리밍, orders.py 상태 머신, export.py ZIP 내보내기, character.py 캐릭터 CRUD) | 백엔드 API |
| **Roo Code** (VS Code Extension) | 프론트엔드 컴포넌트 구현 (ChatScreen, StreamingText, ProviderSelector, CharacterList, OrderDetail, ExportButton 등 28개 컴포넌트) | 프론트엔드 UI |
| **Roo Code** (VS Code Extension) | SWR Hooks 구현 (useChat, useStreamingChat, useOrders 낙관적 업데이트+롤백, useApiKeys) | 프론트엔드 데이터 레이어 |
| **Roo Code** (VS Code Extension) | 테스트 코드 작성 (pytest 24개 + Vitest 2개), Docker 설정 (Dockerfile, docker-compose.yml, 멀티스테이지 빌드, non-root 사용자), 배치 스크립트 작성 (start-docker.bat, test-docker.bat) | 테스트·인프라·배포 |
| **Roo Code** (VS Code Extension) | 더미 데이터 설계 및 생성 (seed.py 멱등적 시드), 시스템 프롬프트 작성 (할머니 캐릭터 설정), README.md 작성 | 시드 데이터·문서화 |
| **Google Gemini** (Antigravity) | PDF 요구사항 분석, 코드 리뷰, 교차 검토, 추가 아이디어 검토, 디버깅 보조 | 문서화·분석·검토 |

> **AI 활용 철학**: Roo Code를 주 설계·구현 도구로 사용하고, Google Gemini를 독립적 검토자/분석자로 활용하여 "AI가 설계·구현한 것을 다른 AI가 검증"하는 교차 검증 워크플로우를 구축했습니다. 특히 Provider 추상화 계층 설계, SSE StreamingResponse의 별도 DB 세션 문제 해결, 주문 상태 머신 삼중 검증 등 아키텍처상 중요한 결정은 AI의 제안을 비판적으로 검토한 후 채택했습니다.

---

## 6. 설계 의도

### 6.1 서비스 아이디어 선택 이유

ChatBook은 "AI와의 대화 자체가 소장 가치 있는 콘텐츠가 될 수 있다"는 통찰에서 출발했습니다.

1. **일상 속 AI 사용의 기록화**: 현대인은 하루에도 여러 번 AI에게 질문하고 조언을 구합니다. 코딩 공부, 맛집 탐색, 여행 계획 등 AI와 나눈 대화는 개인의 지적 자산이지만 대부분 휘발됩니다. ChatBook은 이 대화들을 체계적으로 보관하고 책이라는 물리적 형태로 환원합니다.

2. **캐릭터 기반 스토리텔링**: 단순 Q&A를 넘어, "할머니가 읽어주는 동화책"처럼 AI에 페르소나를 부여하여 감성적인 콘텐츠를 창작할 수 있습니다. 이는 AI 챗봇의 활용 범위를 기능적 도구에서 창의적 파트너로 확장합니다.


### 6.2 사업적 가능성 / 확장성

| 관점 | 분석 |
|------|------|
| **시장 적합성** | AI 사용자 증가 + 셀프 퍼블리싱 트렌드와 맞물려 성장 가능성 높음. AI 대화를 자동으로 책으로 변환하는 서비스는 아직 초기 시장 |
| **수익 모델** | 기본 AI 채팅 무료 (사용자 자신의 API 키를 이용한 과금) + 책 제작 시 과금(스위트북 API 연동), 프리미엄 Provider 구독, 캐릭터 마켓플레이스 |
| **확장 가능성** | Provider 추가(Claude, Llama 등), 멀티미디어 콘텐츠(SD 모델 계열을 이용한 이미지/삽화 등을 대화에 생성/삽입), 협업 대화방, 책 템플릿 |

### 6.3 추가 구현 희망 기능 (시간이 더 있었다면)

| 우선순위 | 기능 | 설명 |
|----------|------|------|
| ⭐⭐⭐ | **책 미리보기** | 주문 전 대화 내용을 실제 책 레이아웃으로 미리보기, 페이지네이션 |
| ⭐⭐⭐ | **다양한 캐릭터** | 할머니 외 다양한 RP 캐릭터(역사 선생님, 여행 가이드, 요리사 등) 프리셋 |
| ⭐⭐ | **대화 검색** | 전체 대화 내용 전문 검색 (FTS), 태그 기반 분류 |
| ⭐⭐ | **책 표지 커스터마이징** | 커버 스타일 프리셋 확장, 사용자 업로드 이미지 지원 |
| ⭐⭐ | **대화 내보내기 템플릿** | PDF, EPUB 등 추가 출력 형식 지원 |
| ⭐ | **협업 대화방** | 여러 사용자가 동일 AI와 함께 대화하는 멀티플레이어 모드 |
| ⭐ | **사용자 인증** | OAuth(Google, GitHub) 로그인, 개인별 대화·주문 관리 |
| ⭐ | **음성 입력** | Web Speech API를 활용한 음성→텍스트 입력 지원 |

---

## 7. API 엔드포인트

### 7.1 대화 및 채팅

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/models` | 등록된 Provider별 사용 가능 모델 목록 |
| `GET` | `/api/conversations` | 대화방 목록 (message_count 포함, N+1 방지 서브쿼리) |
| `POST` | `/api/conversations` | 새 대화방 생성 |
| `GET` | `/api/conversations/{id}` | 대화방 상세 (메시지 포함) |
| `PATCH` | `/api/conversations/{id}` | 대화방 제목 수정 |
| `DELETE` | `/api/conversations/{id}` | 대화방 삭제 (CASCADE) |
| `POST` | `/api/chat/send` | **SSE 스트리밍** 채팅 메시지 전송 |

### 7.2 주문

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/orders` | 주문 목록 (대화방·캐릭터 정보 포함, N+1 방지 벌크 조회) |
| `POST` | `/api/orders` | 새 주문 생성 (중복 방지, 409 Conflict) |
| `GET` | `/api/orders/{id}` | 주문 상세 (대화 메시지 포함) |
| `PATCH` | `/api/orders/{id}/status` | 주문 상태 변경 (삼중 검증: DB CHECK + Pydantic + valid_transitions) |
| `DELETE` | `/api/orders/{id}` | 주문 취소 (접수 상태만 가능) |

### 7.3 데이터 익스포트

| 메서드 | 경로 | 쿼리 파라미터 | 설명 |
|--------|------|---------------|------|
| `GET` | `/api/orders/{id}/export` | `format=json` | JSON 형식으로 익스포트 |
| `GET` | `/api/orders/{id}/export` | `format=zip` | ZIP 형식으로 익스포트 (인메모리 `io.BytesIO` + `zipfile`) |

### 7.4 캐릭터

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/characters` | 캐릭터 목록 |
| `POST` | `/api/characters` | 새 캐릭터 생성 (중복 이름 자동 접미사) |
| `GET` | `/api/characters/{id}` | 캐릭터 상세 |
| `PUT` | `/api/characters/{id}` | 캐릭터 정보 수정 |
| `DELETE` | `/api/characters/{id}` | 캐릭터 삭제 (CASCADE) |
| `GET` | `/api/characters/{id}/sessions` | 캐릭터의 세션 목록 |
| `POST` | `/api/characters/{id}/sessions` | 새 대화 세션 생성 |
| `DELETE` | `/api/characters/{id}/sessions/{sid}` | 세션 삭제 |
| `GET` | `/api/characters/{id}/settings` | 캐릭터 설정 조회 |
| `PUT` | `/api/characters/{id}/settings` | 캐릭터 설정 업데이트 |

### 7.5 SSE 스트리밍 상세 흐름

1. 클라이언트 → `POST /api/chat/send` (JSON: conversation_id, message, provider, model, api_key, session_id)
2. 서버: 대화방 확인 → 사용자 메시지 저장 → 히스토리 조회 → (캐릭터 세션이면 system prompt 빌드) → Provider 선택
3. `StreamingResponse` (`text/event-stream`) 반환 + `X-Accel-Buffering: no` 헤더 (Nginx 버퍼링 방지)
4. Provider.stream_chat() → 토큰 단위로 `data: {"type":"token","content":"..."}` 전송
5. **별도 DB 세션** (`SessionLocal()`)에서 AI 응답 메시지 저장 (StreamingResponse 제너레이터가 요청 스코프 세션 종료 후 실행되기 때문)
6. 완료 시 `data: {"type":"done","message_id":"...","provider":"...","model":"..."}` 전송
7. 에러 시 `data: {"type":"error","message":"..."}` 전송

### 7.6 SSE 이벤트 형식

| 이벤트 타입 | JSON 구조 | 설명 |
|------------|-----------|------|
| `token` | `{"type":"token","content":"텍스트"}` | AI 응답의 각 토큰 |
| `done` | `{"type":"done","message_id":"...","provider":"...","model":"..."}` | 스트리밍 완료 |
| `error` | `{"type":"error","message":"에러 메시지"}` | 오류 발생 |

---

## 8. 데이터베이스 모델

### 8.1 ER 다이어그램 (텍스트)

```
┌─────────────────┐       ┌─────────────────┐
│  Conversation   │       │     Order       │
├─────────────────┤       ├─────────────────┤
│ id (UUID, PK)   │←──────│ conversation_id │
│ title           │       │ id (UUID, PK)   │
│ provider        │       │ status          │
│ model           │       │ quantity        │
│ character_id (FK)│      │ cover_style     │
│ created_at      │       │ memo            │
│ updated_at      │       │ created_at      │
└────────┬────────┘       │ updated_at      │
         │                └─────────────────┘
         │ 1:N
         │
┌────────┴────────┐       ┌─────────────────┐
│    Message      │       │   Character     │
├─────────────────┤       ├─────────────────┤
│ id (UUID, PK)   │       │ id (INT, PK)    │
│ conversation_id │       │ name (UNIQUE)   │
│ role            │       └────────┬────────┘
│ content         │                │ 1:1
│ session_id (FK) │──┐    ┌────────┴────────┐
│ created_at      │  │    │CharacterSettings │
└─────────────────┘  │    ├─────────────────┤
                     │    │ character_id(FK) │
                     │    │ description     │
                     │    │ persona         │
                     │    │ lorebook        │
                     │    │ prompt          │
                     │    └─────────────────┘
                     │
              ┌──────┘
              │
    ┌─────────┴──────────┐
    │    ChatSession     │
    ├────────────────────┤
    │ id (INT, PK)       │
    │ character_id (FK)  │
    │ created_at         │
    └────────────────────┘
```

### 8.2 모델 상세

| 모델 | 주요 필드 | 제약 조건 |
|------|-----------|-----------|
| **Conversation** | `id` (UUID PK), `title`, `provider`, `model`, `character_id` (FK→Character, nullable), `created_at`, `updated_at` | provider CHECK ('openai','gemini','deepseek','demo'), title 길이 제한 |
| **Message** | `id` (UUID PK), `conversation_id` (FK), `role`, `content`, `session_id` (FK→ChatSession, nullable), `created_at` | role CHECK ('user','assistant','system') |
| **Order** | `id` (UUID PK), `conversation_id` (FK), `status`, `quantity`, `cover_style`, `memo`, `created_at`, `updated_at` | status CHECK ('접수','제작중','완료','취소'), quantity ≥ 1 |
| **Character** | `id` (INT PK AUTO), `name` (UNIQUE) | name 고유 |
| **CharacterSettings** | `character_id` (FK, PK), `description`, `persona`, `lorebook`, `prompt` | Character와 1:1 |
| **ChatSession** | `id` (INT PK AUTO), `character_id` (FK), `created_at` | Character와 N:1, Message.session_id와 1:N |

### 8.3 PK 전략

| 엔티티 | PK 타입 | 이유 |
|--------|---------|------|
| Conversation, Message, Order | UUID (String) | 외부 노출(URL, API 응답)에 안전, 분산 환경 대응 |
| Character, ChatSession, CharacterSettings | Auto-increment (Integer) | 내부 관리용, 단순성 및 조회 성능 |

### 8.4 CASCADE 동작

- **Conversation 삭제** → 연관 Message, Order 모두 삭제
- **Character 삭제** → 연관 ChatSession, CharacterSettings 삭제
- **ChatSession 삭제** → 연관 Message의 `session_id`가 SET NULL (대화 데이터 보존)

> `character_id`는 nullable로 설계되어 일반 대화(NULL)와 RP 캐릭터 대화(값)를 단일 `conversations` 테이블에서 통합 관리합니다. 이를 통해 대화방 CRUD 로직을 재사용하면서 필터링으로 모드를 전환할 수 있습니다.

---

## 9. 테스트

### 9.1 테스트 현황

| 구분 | 파일 수 | 테스트 수 | 환경 |
|------|---------|-----------|------|
| 백엔드 (pytest) | 4 | 24 | 인메모리 SQLite + StaticPool |
| 프론트엔드 (Vitest) | 2 | 2 | jsdom + Testing Library |
| Docker 통합 | 2 | 5단계 | curl 기반 API 검증 |

### 9.2 백엔드 테스트 실행

```bash
cd backend
pytest -v                          # 전체 테스트
pytest tests/test_chat_api.py -v   # 대화방 API
pytest tests/test_orders_api.py -v # 주문 API (상태 전이 검증)
pytest tests/test_providers.py -v  # Provider 단위 테스트
pytest -k "test_create" -v         # 키워드 필터
```

### 9.3 프론트엔드 테스트 실행

```bash
cd frontend
pnpm test          # Vitest run
pnpm test:watch    # Watch 모드
```

### 9.4 Docker 통합 테스트

```bash
# Linux/Mac
bash test-docker.sh

# Windows
test-docker.bat
```

---

## 10. 라이선스

MIT License

---

## 11. PDF 제출 체크리스트

> 아래 체크리스트는 스위트북 개발 과제 안내문( PDF)에서 명시한 제출 요건 및 README 필수 포함 항목입니다. 각 항목의 충족 여부를 표시했습니다.

### ✅ 서비스 소개 (필수)

- [x] 어떤 서비스인지 한 문장 설명 → [Section 1.1](#11-한-줄-설명)
- [x] 타겟 사용자 명시 → [Section 1.2](#12-타겟-사용자)
- [x] 주요 기능 목록 → [Section 1.3](#13-주요-기능)

### ✅ 실행 방법 (필수)

- [x] Docker 실행 가능: `docker compose up -d` 또는 `start-docker.bat` 더블클릭으로 1회 실행 → [Section 2.2](#22-빠른-실행)
- [x] 환경변수 설정 방법 (`.env.example` → `.env`) → [Section 2.5](#25-환경변수-설정)
- [x] 접속 URL (`http://localhost:3000`, `http://localhost:8000/docs`) → [Section 2.2](#22-빠른-실행)
- [x] 포트 변경 방법 명시 → [Section 2.6](#26-포트-변경)
- [x] 복사-붙여넣기만으로 실행 가능한 명령어 → [Section 2.2](#22-빠른-실행)

### ✅ 완성한 레벨 (필수)

- [x] 구현 완료한 레벨 (Lv1, Lv1+, Lv2, Lv3) 명시 → [Section 3](#3-완성한-레벨-및-구현-내용)
- [x] 각 레벨에서 구체적으로 구현한 내용 기술 → [Section 3](#3-완성한-레벨-및-구현-내용)
- [x] 평가 포인트 (서비스 플로우 완성도, 비즈니스 로직, 데이터 모델링) 명시 → [Section 3](#3-완성한-레벨-및-구현-내용)

### ✅ 기술 스택 및 아키텍처 (필수)

- [x] 프론트엔드/백엔드/DB 기술 스택 → [Section 4.1](#41-기술-스택)
- [x] 기술 스택 선택 이유 → [Section 4.2](#42-기술-선택-이유)
- [x] 아키텍처 다이어그램 → [Section 4.3](#43-아키텍처-다이어그램)
- [x] 디렉터리 구조 → [Section 4.6](#46-프로젝트-디렉토리-구조)
- [x] 핵심 아키텍처 결정사항 → [Section 4.5](#45-핵심-아키텍처-결정사항)

### ✅ AI 도구 사용 내역 (필수)

- [x] 사용한 AI 도구 목록 (Roo Code, Google Gemini) → [Section 5](#5-ai-도구-사용-내역)
- [x] 각 도구별 활용 내용 및 구간 → [Section 5](#5-ai-도구-사용-내역)
- [x] AI 활용 철학 및 교차 검증 워크플로우 → [Section 5](#5-ai-도구-사용-내역)

### ✅ 설계 의도 (필수)

- [x] 서비스 아이디어 선택 이유 → [Section 6.1](#61-서비스-아이디어-선택-이유)
- [x] 사업적 가능성에 대한 견해 → [Section 6.2](#62-사업적-가능성--확장성)
- [x] 추가 시간이 있었다면 구현했을 기능 → [Section 6.3](#63-추가-구현-희망-기능-시간이-더-있었다면)

### ✅ 그 외 제출 요건 확인

- [x] `.env` 파일이 `.gitignore`에 등록되어 있는가 → `.gitignore`에 `.env` 포함
- [x] GitHub 저장소가 **Public**인가 → Public 저장소
- [x] `docker compose up`으로 정상 실행되는가 → `start-docker.bat` / `docker compose up -d` 검증 완료
- [x] 더미 데이터가 포함되어 있는가 (로그인 없이 확인 가능) → 멱등적 시드 데이터 (대화방 3, 주문 2, 캐릭터봇 1)
- [x] 포트 변경이 환경변수로 가능한가 → `BACKEND_PORT`, `FRONTEND_PORT` 환경변수 지원
- [x] README.md만 보고 실행 가능한가 → Section 2에서 단계별 실행 가이드 제공

---

> **제출 정보**: 본 프로젝트는 (주)스위트북 바이브코딩 풀스택 개발자 채용 과제로 제작되었습니다.
>
> **구글폼 제출 링크**: [https://forms.gle/4EuYDFXH1bBdMfGT7](https://forms.gle/4EuYDFXH1bBdMfGT7)
>
> **문의**: 과제 관련 문의는 (주)스위트북 개발팀장 이정훈 ([jpun@sweetbook.com](mailto:jpun@sweetbook.com)) 으로 연락 바랍니다.
