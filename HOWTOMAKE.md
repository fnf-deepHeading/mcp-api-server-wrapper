# API를 MCP 서버로 래핑하는 방법

이 가이드는 외부 API를 MCP 서버로 래핑하는 방법을 단계별로 설명합니다. 이 템플릿을 사용하면 복잡한 MCP 서버 구현 없이도 쉽게 API를 Claude와 통합할 수 있습니다.

## 0단계: 프로젝트 설정하기

1. 템플릿을 다운로드하고 프로젝트 이름을 설정합니다:
```bash
# 템플릿 다운로드
git clone https://github.com/your-username/mcp-server-template.git

# 프로젝트 이름 설정 (예: naver-trend-mcp)
mv mcp-server-template your-project-name
cd your-project-name

# server.py에서 서버 이름 수정
# "MCP-Server"를 원하는 이름으로 변경
mcp = FastMCP(
    "Your-API-Name-MCP",  # 여기를 수정하세요
    host="0.0.0.0",
    port=8080,
    lifespan=app_lifespan,
    dependencies=["requests"]
)
```

2. 프로젝트 설명 업데이트:
- `README.md` 파일의 프로젝트 이름과 설명을 수정합니다.
- Docker 이미지 이름을 프로젝트에 맞게 변경합니다.

예시:
```bash
# Docker 이미지 이름을 프로젝트에 맞게 지정
docker build -t your-project-name .
docker run -p 8080:8080 your-project-name --api_key YOUR_API_KEY
```

## 1단계: API 문서 확인하기

먼저 래핑하려는 API 문서를 확인하고 다음 정보를 찾으세요:

- API 엔드포인트 URL
- 인증 방식 (API 키, OAuth 토큰 등)
- 필요한 요청 파라미터
- 응답 형식

## 2단계: server.py 수정하기

`server.py` 파일에서 `# 여기부터 수정하세요`와 `# 여기까지 수정하세요` 사이의 부분만 수정하면 됩니다.

### 2-1. API 설정 클래스 수정

```python
@dataclass
class APISettings:
    """API 설정"""
    api_url: str = "https://api.example.com/v1"  # 여기에 실제 API URL 입력
    api_key: str = ""  # 커맨드라인이나 환경변수에서 설정
    # 필요한 추가 설정을 여기에 입력하세요
```

### 2-2. 커맨드라인 인자 추가

```python
def parse_args():
    parser = argparse.ArgumentParser(description='MCP 서버')
    
    # API 인증 설정
    parser.add_argument('--api_key', help='API 키 (환경변수 API_KEY로도 설정 가능)')
    # 필요한 추가 인자를 여기에 추가하세요
    # 예: parser.add_argument('--client_secret', help='클라이언트 시크릿')
    
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    return parser.parse_args()
```

### 2-3. API 호출 함수 수정

```python
@mcp.tool()
async def search_data(
    ctx: Context,
    query: str,
    limit: int = 10
) -> str:
    """검색 API를 호출하여 데이터를 검색합니다."""
    try:
        # 설정 가져오기
        settings = ctx.request_context.lifespan_context
        
        # API 호출
        response = requests.get(
            f"{settings.api_url}/search",
            headers={
                "Authorization": f"Bearer {settings.api_key}"
            },
            params={
                "q": query,
                "limit": limit
            }
        )
        
        # 응답 확인
        response.raise_for_status()
        
        # 응답 반환
        return response.json()
        
    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {str(e)}")
        return {"error": str(e)}
```

## 3단계: 환경 변수 설정하기 (선택사항)

`.env` 파일을 생성하여 API 키와 같은 민감한 정보를 저장할 수 있습니다:

```
API_KEY=your_api_key_here
DEBUG=false
```

## 4단계: 빌드 및 실행하기

```bash
# Docker 이미지 빌드
docker build -t my-api-server .

# 서버 실행 (API 키를 커맨드라인으로 전달)
docker run -p 8080:8080 my-api-server --api_key YOUR_API_KEY

# 또는 환경 변수 파일을 사용하여 실행
docker run -p 8080:8080 --env-file .env my-api-server
```

## 5단계: Claude에서 사용하기

Claude에서 다음과 같이 API를 호출할 수 있습니다:

```python
# 예시: 검색 API 호출
response = await mcp.tools.search_data(
    query="인공지능",
    limit=5
)
```

## 실제 API 예제

### 네이버 검색어 트렌드 API

1. API 설정 클래스 수정:
```python
@dataclass
class APISettings:
    """API 설정"""
    api_url: str = "https://openapi.naver.com/v1/datalab/search"
    client_id: str = ""     # 커맨드라인이나 환경변수에서 설정
    client_secret: str = "" # 커맨드라인이나 환경변수에서 설정
```

2. 커맨드라인 인자 추가:
```python
def parse_args():
    parser = argparse.ArgumentParser(description='네이버 검색어 트렌드 MCP 서버')
    parser.add_argument('--client_id', help='네이버 API 클라이언트 ID')
    parser.add_argument('--client_secret', help='네이버 API 클라이언트 시크릿')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    return parser.parse_args()
```

3. 서버 수명주기 관리 함수 수정:
```python
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[APISettings]:
    """애플리케이션 수명주기를 관리합니다."""
    logger.info("서버 시작 중...")
    
    # 인자 파싱
    args = parse_args()
    
    # 디버그 모드 설정
    if args.debug:
        logging.getLogger("mcp-server").setLevel(logging.DEBUG)
    
    # API 설정
    settings = APISettings()
    
    # API 키 설정 (커맨드라인 > 환경변수)
    settings.client_id = args.client_id or os.getenv("NAVER_CLIENT_ID")
    settings.client_secret = args.client_secret or os.getenv("NAVER_CLIENT_SECRET")
    
    if not settings.client_id or not settings.client_secret:
        raise ValueError("네이버 API 클라이언트 ID와 시크릿이 설정되지 않았습니다.")
    
    try:
        yield settings
    finally:
        logger.info("서버 종료 중...")
```

4. API 호출 함수 추가:
```python
@mcp.tool()
async def search_trend(
    ctx: Context,
    keywords: List[str],
    start_date: str,
    end_date: str
) -> str:
    """네이버 검색어 트렌드를 조회합니다."""
    try:
        settings = ctx.request_context.lifespan_context
        
        # 키워드 그룹 생성
        keyword_groups = [
            {"groupName": keyword, "keywords": [keyword]} for keyword in keywords[:5]
        ]
        
        # API 호출
        response = requests.post(
            settings.api_url,
            headers={
                "X-Naver-Client-Id": settings.client_id,
                "X-Naver-Client-Secret": settings.client_secret,
                "Content-Type": "application/json"
            },
            json={
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": "month",
                "keywordGroups": keyword_groups
            }
        )
        
        # 응답 확인
        response.raise_for_status()
        
        # 응답 반환
        return response.json()
        
    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {str(e)}")
        return {"error": str(e)}
```

## 주의사항

1. API 키는 절대로 코드에 직접 입력하지 마세요. 항상 커맨드라인 인자나 환경변수로 전달하세요.
2. 에러 처리를 통해 API 호출 실패 시 적절한 메시지를 반환하세요.
3. 로깅을 활용하여 문제 해결에 도움이 되는 정보를 기록하세요.
4. 대용량 데이터를 반환하는 API인 경우, 페이지네이션을 구현하거나 데이터를 적절히 필터링하세요. 

# 🤝 도움받기

문제가 생기면 다음을 확인해보세요:
1. API 문서를 다시 한 번 확인
2. API 키가 올바르게 전달되었는지 확인
3. 파라미터 형식이 올바른지 확인
4. 응답 에러 메시지 확인

## 📚 참고 자료

- [MCP SDK 문서](https://github.com/your-username/mcp-python-sdk)
- [Requests 라이브러리 문서](https://requests.readthedocs.io/)
- [Python Type Hints 가이드](https://docs.python.org/3/library/typing.html) 