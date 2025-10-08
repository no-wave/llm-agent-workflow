# 햄버거 가게 주문 키오스크 에이전트

OpenAI API와 Mem0ai를 활용한 지능형 햄버거 주문 키오스크 시스템입니다.

## 프로젝트 개요

이 프로젝트는 AI 에이전트를 활용하여 자연어로 햄버거를 주문할 수 있는 키오스크 시스템입니다. OpenAI의 GPT 모델과 Function Calling 기능을 사용하여 사용자의 의도를 파악하고, 메뉴 조회, 주문 추가/삭제, 주문 확정 등의 작업을 수행합니다.

### 주요 기술 스택

- **LLM**: OpenAI GPT-4o-mini (Function Calling)
- **Memory**: Mem0ai (대화 기록 관리)
- **Validation**: Pydantic (데이터 검증)
- **Async**: asyncio (비동기 처리)
- **Tools**: 메뉴 조회, 주문 관리 도구
- **Recovery**: 자동 재시도 및 에러 복구

## 프로젝트 구조

```
kiosk-agent/
│
├── config/                      # 설정 관리
│   ├── __init__.py
│   └── settings.py             # 환경 변수 및 앱 설정
│
├── models/                      # 데이터 모델
│   ├── __init__.py
│   ├── schemas.py              # Pydantic 스키마 정의
│   └── menu.py                 # 메뉴 데이터베이스
│
├── agents/                      # AI 에이전트
│   ├── __init__.py
│   ├── base_agent.py           # 기본 에이전트 클래스
│   └── order_agent.py          # 주문 처리 에이전트
│
├── tools/                       # 에이전트 도구
│   ├── __init__.py
│   ├── menu_tools.py           # 메뉴 조회/검색 도구
│   └── order_tools.py          # 주문 생성/관리 도구
│
├── memory/                      # 메모리 관리
│   ├── __init__.py
│   └── memory_manager.py       # Mem0 메모리 관리
│
├── utils/                       # 유틸리티
│   ├── __init__.py
│   ├── validation.py           # 입력 검증 및 정제
│   └── recovery.py             # 에러 복구 및 재시도
│
├── .env                         # 환경 변수 (API 키 등)
├── .gitignore                  # Git 무시 파일
├── requirements.txt            # 의존성 패키지
├── pyproject.toml              # uv 프로젝트 설정
├── main.py                     # 메인 실행 파일
├── test_example.py             # 테스트 파일
└── README.md                   # 프로젝트 문서
```

## 주요 컴포넌트

### 1. Config (설정)
- **settings.py**: 환경 변수 관리 및 전역 설정

### 2. Models (데이터 모델)
- **schemas.py**: Pydantic 기반 데이터 모델 (MenuItem, Order, OrderItem 등)
- **menu.py**: 메뉴 데이터베이스 및 조회 로직

### 3. Agents (에이전트)
- **base_agent.py**: 기본 에이전트 (LLM 호출, 메모리 관리)
- **order_agent.py**: 주문 전문 에이전트 (Function Calling)

### 4. Tools (도구)
- **menu_tools.py**: 메뉴 조회, 검색, 카테고리별 조회
- **order_tools.py**: 주문 생성, 아이템 추가/제거, 주문 확정

### 5. Memory (메모리)
- **memory_manager.py**: Mem0ai를 통한 대화 기록 관리

### 6. Utils (유틸리티)
- **validation.py**: 입력 검증 및 데이터 정제
- **recovery.py**: 에러 복구, 재시도, 지수 백오프

### 7. Main
- **main.py**: 키오스크 인터페이스 및 실행 루프
- **test_example.py**: 각 컴포넌트 테스트

## 설치 방법

### 방법 1: uv 사용 (권장)

[uv](https://github.com/astral-sh/uv)는 빠른 Python 패키지 관리자입니다.

#### 1. uv 설치

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

또는 pip로 설치:
```bash
pip install uv
```

#### 2. 프로젝트 초기화

```bash
# 프로젝트 디렉토리로 이동
cd kiosk-agent

# pyproject.toml 파일 생성 (선택사항, 이미 있다면 건너뛰기)
uv init

# 의존성 설치
uv pip install -r requirements.txt
```

#### 3. .env 파일 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# OpenAI API 설정
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Mem0 설정 (선택사항)
MEM0_API_KEY=your-mem0-api-key-here

# 애플리케이션 설정
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

#### 4. 테스트 실행

```bash
uv run python test_example.py
```

#### 5. 프로그램 실행

```bash
uv run python main.py
```

### 방법 2: 전통적인 venv 사용

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 프로그램 실행
python main.py
```

## pyproject.toml 설정

uv를 사용하는 경우 `pyproject.toml` 파일을 생성하세요:

```toml
[project]
name = "hamburger-kiosk-agent"
version = "1.0.0"
description = "AI-powered hamburger ordering kiosk"
readme = "README.md"
requires-python = ">=3.8"

dependencies = [
    "openai>=1.12.0",
    "mem0ai>=0.0.10",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "aiohttp>=3.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
```

## 사용 방법

### 기본 사용

프로그램을 실행하면 대화형 키오스크가 시작됩니다:

```bash
uv run python main.py
```

### 사용 예시

```
고객님: 안녕하세요
키오스크: 안녕하세요! 햄버거 가게 주문 키오스크입니다. 무엇을 도와드릴까요?

고객님: 메뉴 보여주세요
키오스크: [전체 메뉴 리스트 표시]

고객님: 클래식 버거 2개랑 콜라 주세요
키오스크: 클래식 버거 2개와 콜라 1개가 추가되었습니다.
         현재 주문 금액: 13,800원

고객님: 감자튀김도 추가해주세요
키오스크: 감자튀김 1개가 추가되었습니다.
         현재 주문 금액: 16,300원

고객님: 주문 확인
키오스크: [현재 주문 내역 표시]

고객님: 종료
키오스크: 주문을 확정하시겠습니까? (예/아니오)
```

### 사용 가능한 명령어

- **메뉴**: 전체 메뉴 보기
- **주문**: 메뉴 주문하기
- **확인**: 현재 주문 내역 확인
- **취소**: 주문 초기화
- **종료**: 프로그램 종료

### 자연어 주문

다음과 같이 자연스럽게 주문할 수 있습니다:
- "클래식 버거 2개 주세요"
- "치즈버거랑 감자튀김, 콜라 주문할게요"
- "베이컨 버거에 치즈 추가해주세요"
- "클래식 버거 하나 빼주세요"

## 테스트

시스템의 각 컴포넌트를 테스트하려면:

```bash
uv run python test_example.py
```

테스트 항목:
- 메뉴 데이터베이스 조회
- 메뉴 도구 기능
- 주문 도구 기능
- 입력 검증 및 정제
- 주문 워크플로우
- 에이전트 기본 동작

## 주요 기능

### 1. 자연어 주문 처리
- GPT-4를 활용한 의도 파악
- 자연스러운 대화 흐름

### 2. Function Calling
- 메뉴 조회 함수
- 주문 관리 함수
- 동적 도구 호출

### 3. 데이터 검증
- Pydantic을 통한 강력한 타입 검증
- 입력 데이터 정제
- 주문 유효성 검사

### 4. 에러 복구
- 자동 재시도 (최대 3회)
- 지수 백오프
- 사용자 친화적 에러 메시지

### 5. 메모리 관리
- Mem0ai를 통한 대화 기록 저장
- 컨텍스트 검색
- 로컬 백업

### 6. 비동기 처리
- asyncio를 활용한 효율적인 I/O
- 빠른 응답 속도


## 개발

### 새로운 메뉴 추가

`models/menu.py`의 `_initialize_menus` 메서드에서 메뉴를 추가할 수 있습니다:

```python
MenuItem(
    id="B005",
    name="스페셜 버거",
    category=MenuCategory.BURGER,
    price=9900,
    description="특별한 소스의 프리미엄 버거",
    options=["치즈 추가", "베이컨 추가"]
)
```

### 새로운 도구 추가

`tools/` 디렉토리에 새 도구 파일을 생성:

```python
# tools/payment_tools.py
class PaymentTools:
    @staticmethod
    def process_payment(amount: int, method: str):
        # 결제 처리 로직
        pass

PAYMENT_TOOL_DEFINITIONS = [...]
```

### 새로운 에이전트 추가

`agents/` 디렉토리에 특화 에이전트 생성:

```python
# agents/recommendation_agent.py
class RecommendationAgent(BaseAgent):
    def recommend_menu(self, preferences):
        # 추천 로직
        pass
```

## 문제 해결

### OpenAI API 에러

```
Error: Incorrect API key provided
```
**해결**: `.env` 파일의 `OPENAI_API_KEY` 확인

### 모듈 import 에러

```
ModuleNotFoundError: No module named 'openai'
```
**해결**: 
```bash
uv pip install -r requirements.txt
```

### uv 명령어 인식 안됨

```
command not found: uv
```
**해결**: uv 재설치 또는 PATH 확인
```bash
# macOS/Linux
export PATH="$HOME/.cargo/bin:$PATH"
```

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

## 향후 개선 계획

- [ ] 웹 인터페이스 추가 (FastAPI + React)
- [ ] 데이터베이스 통합 (PostgreSQL)
- [ ] 결제 시스템 연동
- [ ] 다국어 지원
- [ ] 음성 주문 기능
- [ ] 주문 통계 대시보드
- [ ] Docker 컨테이너화