# API를 MCP 서버로 래핑하는 방법

**[중요] AI 어시스턴트를 위한 핵심 지침:**

*   **주요 수정 대상**: 이 가이드의 목표는 **`server.py` 템플릿 파일을 수정**하여 MCP 서버를 만드는 것입니다. 하지만 API 구현 및 환경 구성에 따라 다음 파일들의 수정이 필요할 수 있습니다:
    *   **`pyproject.toml`**: Python 의존성(라이브러리) 추가/변경 시.
    *   **`requirements.txt`**: `pyproject.toml`과 동기화하거나, 별도로 의존성 관리 시.
    *   **`Dockerfile`**: 시스템 의존성 추가, Python 버전 변경, 빌드/실행 방식 변경 시.
*   **템플릿 구조 유지**: `server.py`는 제공된 템플릿 구조(`APIConfig`, `ToolNames`, `@list_tools`, `@call_tool` 등)를 **반드시 유지**해야 합니다. **절대로 새로운 파일을 만들거나 Flask, FastAPI 등 다른 웹 프레임워크를 사용하지 마세요.**
*   **API 호출 위치**: 모든 외부 API 호출 로직은 반드시 **`@call_tool` 함수 내부의 `match` 블록 안에서** 구현되어야 합니다.
*   **의존성 관리**: API 호출 등에 새로운 Python 라이브러리가 필요하면, **반드시 `pyproject.toml` 파일의 `[project.dependencies]` 섹션에 추가**하고, 필요한 경우 **`requirements.txt` 파일도 동기화**해야 합니다. (참고: `uv pip compile pyproject.toml -o requirements.txt` 와 같은 명령어를 사용할 수 있습니다.)
*   **환경 구성**: 시스템 라이브러리 설치 등이 필요하면 **`Dockerfile`을 수정**해야 할 수 있습니다.
*   **최종 목표**: 결과물은 **MCP 프로토콜을 따르는 서버**여야 합니다. 일반적인 API 서버를 만들지 않도록 주의하세요.
*   **문서 업데이트**: `README.md`는 새로 구축하는 MCP Server 사용자를 위한 최종 문서입니다. 현재의 `README.md`는 템플릿 프로젝트를 위한 문서이니 새로 작성해주세요. `server.py`나 **다른 파일(`pyproject.toml`, `requirements.txt`, `Dockerfile` 등)의 변경 사항(새로운 기능, 의존성, 환경 설정, 실행 방법 등)을 정확하게 반영**하여 업데이트해야 합니다.

---

이 가이드는 외부 API를 MCP 서버로 래핑하는 방법을 단계별로 설명합니다.
AI 어시스턴트는 이 가이드를 따라 API 문서만으로 MCP 서버를 구현할 수 있습니다.

## 0단계: 프로젝트 설정하기

1. 템플릿을 다운로드하고 프로젝트 이름을 설정합니다:
```bash
# 템플릿 다운로드
git clone [저장소 URL]
cd [프로젝트 이름]
```

## 1단계: API 문서 확인하기

API 문서에서 다음 정보를 찾아 정리하세요:

1. API 기본 정보
   - 기본 URL (base URL)
   - API 버전 정보
   - 인증 방식 (API 키, OAuth 토큰 등)

2. API 엔드포인트 정보
   - 엔드포인트 경로
   - HTTP 메서드 (GET, POST 등)
   - 요청 파라미터와 타입
   - 응답 형식과 타입

3. 필요한 Python 라이브러리
   - API 클라이언트 라이브러리
   - 데이터 처리 라이브러리
   - 유틸리티 라이브러리

## 2단계: server.py 수정하기

`server.py` 파일을 다음 순서로 수정하세요:

### 2-1. API 요청 모델 정의

1. 각 API 엔드포인트에 대한 Pydantic 모델을 정의합니다.
2. 예시 모델(SearchRequestModel, UserRequestModel)을 삭제하고 실제 API 모델로 교체합니다.
3. 각 필드의 타입과 제약조건을 명시합니다.

예시:
```python
class MyAPIRequestModel(BaseModel):
    """API 요청 모델 설명"""
    required_field: str
    optional_field: int = 10
```

### 2-2. API 도구 이름 정의

1. ToolNames 클래스에서 예시 상수(SEARCH, GET_USER)를 삭제합니다.
2. 실제 API 엔드포인트에 맞는 상수를 정의합니다.
3. 각 상수는 명확하고 직관적인 이름을 사용합니다.

예시:
```python
class ToolNames:
    """API 도구 이름 상수"""
    GET_TRENDING = "get_trending"
    CREATE_POST = "create_post"
```

### 2-3. API 설정 구성

1. APIConfig 클래스의 base_url을 실제 API URL로 수정합니다.
2. API 인증 방식에 맞게 get_headers 메서드를 수정합니다.
3. 필요한 경우 추가 설정 메서드를 구현합니다.

### 2-4. API 도구 구현

1. list_tools 함수에서 예시 도구를 삭제하고 실제 도구를 등록합니다.
   - 각 Tool 객체에 대해 inputSchema를 Pydantic 모델로 설정합니다. 예를 들어, inputSchema=MyAPIRequestModel.schema()와 같이 설정합니다.
2. call_tool 함수에서 예시 case를 삭제하고 실제 API 호출을 구현합니다.
   - TextContent 객체를 생성할 때 필수 필드(type, text 등)를 설정합니다.
   - Pydantic 모델의 데이터를 가져올 때는 model_dump 메서드를 사용합니다.
3. 각 API 호출에 대한 에러 처리를 구현합니다.

## 3단계: API 키 설정 및 실행하기

API 키는 다음 우선순위로 설정됩니다:

1. **커맨드라인 인자** (최우선)
```bash
uv run server.py --API_KEY your_api_key
```

2. **.env 파일**
```env
API_KEY=your_api_key
```
```bash
uv run server.py
```

3. **환경변수**
```bash
export MCP_API_KEY=your_api_key
uv run server.py
```

4. Docker로 실행:
```bash
# 커맨드라인에서 API 키 전달
docker run -p 8080:8080 my-api-server --API_KEY your_api_key

# 환경변수로 API 키 전달
docker run -e MCP_API_KEY=your_api_key -p 8080:8080 my-api-server

# .env 파일로 API 키 전달
docker run -p 8080:8080 --env-file .env my-api-server
```

## 4단계: 의존성 관리하기

### 4-1. 필요한 라이브러리 확인

API 구현에 필요한 라이브러리를 정리합니다:
- API 클라이언트 라이브러리
- 데이터 처리 라이브러리
- 유틸리티 라이브러리

### 4-2. pyproject.toml 및 requirements.txt 수정

*   `pyproject.toml` 파일의 `[project.dependencies]` 섹션에 필요한 라이브러리와 버전을 명시합니다.
*   필요한 경우, `requirements.txt` 파일도 업데이트합니다. (예: `uv pip compile pyproject.toml -o requirements.txt`)

```toml
[project]
name = "your-api-mcp"
version = "0.1.0"
description = "Your API MCP Server"
dependencies = [
    "mcp>=1.6.0",            # MCP 서버 코어
    "pydantic>=2.0.0",       # 데이터 모델 유효성 검사
    "pydantic-settings>=2.0.0", # 설정 관리 (.env 파일 포함)
    "aiohttp>=3.8.0",        # 비동기 HTTP 클라이언트 (API 호출용)
    "anyio>=3.6.0"           # 비동기 실행기 (serve 함수 실행용)
    # 필요한 라이브러리 추가 (예: "python-dotenv>=1.0.0")
]
```

### 4-3. 의존성 설치

```bash
# 의존성 설치 (pyproject.toml 기반)
uv sync
# 또는 (requirements.txt 기반)
# uv pip install -r requirements.txt
```

## 5단계: 빌드 및 실행하기 (Dockerfile 수정 확인)

*   만약 시스템 의존성 추가 등으로 `Dockerfile`을 수정했다면, 변경 사항이 올바르게 적용되었는지 확인합니다.

```bash
# Docker 이미지 빌드 (수정된 Dockerfile 사용)
docker build -t my-api-server .

# 서버 실행
docker run -p 8080:8080 --env-file .env my-api-server
```

## 6단계: README.md 작성하기

사용자를 위한 README.md를 작성합니다:
1. 프로젝트 설명과 주요 기능
2. 설치 및 실행 방법
3. MCP 클라이언트 설정 방법
4. API 사용 예시
5. 문제 해결 가이드

## 최종 점검 사항

구현이 완료되면 다음 사항들을 확인하세요:

1. API 기능
   - 모든 API 엔드포인트가 올바르게 구현되었는지 확인
   - 에러 처리가 적절히 구현되었는지 확인

2. 설정 관리
   - API 키와 기타 설정이 올바르게 관리되는지 확인
   - 환경 변수가 올바르게 로드되는지 확인

3. 의존성 및 환경 관리
    *   **`pyproject.toml`과 `requirements.txt`에 필요한 모든 라이브러리가 명시**되었는지 확인
    *   모든 의존성이 호환되는 버전인지 확인
    *   **`Dockerfile`에 필요한 시스템 설정이나 의존성이 반영**되었는지 확인

4. 문서화
    *   `README.md`가 `server.py` 및 **기타 관련 파일(`pyproject.toml`, `Dockerfile` 등)의 현재 상태**와 정확히 일치하는지 확인
    *   README.md가 사용자 친화적으로 작성되었는지 확인
    *   API 사용 예제가 포함되어 있는지 확인

5. 테스트
   - 기본 API 호출이 정상 작동하는지 확인
   - 에러 상황에서 올바르게 동작하는지 확인
   - Claude에서 실제로 호출 가능한지 확인 