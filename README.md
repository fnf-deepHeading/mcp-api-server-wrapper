# MCP API Server Template

API 통합을 위한 MCP 서버 템플릿입니다. AI를 활용하여 외부 API를 쉽게 MCP 서버로 래핑할 수 있습니다.

## 특징

* AI를 활용한 자동 API 통합
* 명령줄 인자를 통한 설정 관리
* Docker 지원
* 상세한 가이드 문서 제공

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
# 목표: ~~ API를 호출할 수 있는 MCP 서버 구현
# 지침: `HOWTOMAKE.md` 파일에 명시된 지침, 특히 **"AI 어시스턴트를 위한 핵심 지침"** 섹션을 반드시 따라주세요. (필수 프롬프트)
# API 정보:
# 1. 기능1: [링크]
# 2. 기능2: [링크]
# 작업방식: (선택 프롬프트)
전체 작업을 한 번에 처리하지 않고, 할 일 목록(TODO.md)과 세부 실행계획 파일을 만들고 하나씩 체크하며 진행하세요.
세부 실행계획은 진행여부 묻지 말고 한번에 진행하세요.
```  
예시:  
```  
# 목표: 네이버 API 3개(블로그 검색, 뉴스 검색, 검색량 조회)를 호출할 수 있는 MCP 서버 구현

# 지침: `HOWTOMAKE.md` 파일에 명시된 지침, 특히 **"AI 어시스턴트를 위한 핵심 지침"** 섹션을 반드시 따라주세요.

# API 정보:
# 1. 네이버 블로그 검색: https://developers.naver.com/docs/serviceapi/search/blog/blog.md#%EB%B8%94%EB%A1%9C%EA%B7%B8 
# 2. 네이버 뉴스 검색: https://developers.naver.com/docs/serviceapi/search/news/news.md#%EB%89%B4%EC%8A%A4 
# 3. 네이버 검색량 조회: https://developers.naver.com/docs/serviceapi/datalab/search/search.md#%ED%86%B5%ED%95%A9-%EA%B2%80%EC%83%89%EC%96%B4-%ED%8A%B8%EB%A0%8C%EB%93%9C
```
4. AI가 자동으로:  
   * API 문서를 분석  
   * MCP 서버 코드 생성  
   * 설정 파일 구성  
   * 실행 방법 안내를 수행합니다.

5. (추천 마무리 단계) 코드 점검을 위해 AI에게 다음과 같이 요청하세요:
```
코드를 점검해주세요.  
다음 기준에 따라 피드백을 주고 수정해주세요:
1. 문법 오류나 실행 시 오류 발생 가능성
2. 비효율적인 로직이나 중복 코드
3. 성능 개선이 가능한 부분
4. 가독성을 높일 수 있는 개선사항
5. 일반적인 코드 컨벤션 위반 여부 (예: PEP8, Google Style 등)
```


### Claude에서 사용하기

Claude에서 MCP 서버를 사용하려면 다음과 같이 설정하세요:

설정 예시:

```json
{
  "mcpServers": {
    "[서버 이름]": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project",
        "run",
        "server.py",
        "--API_KEY",
        "your_api_key"
      ]
    }
  }
}
```

## 문제 해결

### 자주 발생하는 문제

1. **API 키 오류**
   - `.env` 파일이 올바른 위치에 있는지 확인
   - API 키가 올바른 형식인지 확인

2. **의존성 오류**
   - `uv sync` 명령어로 의존성 재설치
   - Python 버전이 3.10 이상인지 확인

3. **Docker 관련 오류**
   - Docker 데몬이 실행 중인지 확인
   - 이미지가 올바르게 빌드되었는지 확인

### 디버그 모드 사용

* 직접 코딩 없이 API 통합 가능
* API 문서만 있으면 빠른 구현
* 표준화된 MCP 서버 구조 유지
* 즉시 실행 가능한 코드 생성
* Claude와 같은 AI 도구에서 바로 사용 가능

## 라이선스

MIT License 