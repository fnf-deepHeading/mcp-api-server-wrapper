# MCP API Server Template

API 통합을 위한 MCP 서버 템플릿입니다. AI를 활용하여 외부 API를 쉽게 MCP 서버로 래핑할 수 있습니다.

## 특징

- AI를 활용한 자동 API 통합
- 명령줄 인자를 통한 설정 관리
- Docker 지원
- 상세한 가이드 문서 제공

## AI로 MCP 서버 만들기

이 템플릿을 사용하면 AI의 도움을 받아 외부 API를 쉽게 MCP 서버로 래핑할 수 있습니다.

### 사용 방법

1. 프로젝트 클론
   ```bash
   git clone https://github.com/fnf-deepHeading/mcp-api-server-wrapper.git your-api-name-mcp
   cd your-api-name-mcp
   ```

2. 개발 환경 설정
   ```bash
   # 의존성 동기화
   uv sync
   ```

3. AI에게 다음과 같은 형식으로 요청하세요:
   ```
   "HOWTOMAKE.md 가이드와 {API 문서 URL}을 참고해서 {API 이름} MCP Server를 만들어줘"
   ```

   예시:
   ```
   "HOWTOMAKE.md 가이드와 https://api.example.com/docs를 참고해서 네이버 검색량 MCP Server를 만들어줘"
   ```

4. AI가 자동으로:
   - API 문서를 분석
   - MCP 서버 코드 생성
   - 설정 파일 구성
   - 실행 방법 안내
   를 수행합니다.

### Claude에서 사용하기

Claude에서 MCP 서버를 사용하려면 다음과 같이 설정하세요:

설정 예시:
   ```json
   {
       "mcp-your-api": {
           "command": "uv",
           "args": [
               "--directory",
               "/path/to/your/mcp-server",
               "run",
               "server.py"
           ]
       }
   }
   ```

### 장점

- 직접 코딩 없이 API 통합 가능
- API 문서만 있으면 빠른 구현
- 표준화된 MCP 서버 구조 유지
- 즉시 실행 가능한 코드 생성
- Claude와 같은 AI 도구에서 바로 사용 가능

## 라이선스

MIT License 