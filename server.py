#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 서버 템플릿

이 템플릿은 외부 API를 MCP 서버로 래핑하는 기본 구조를 제공합니다.
AI 어시스턴트가 API 문서를 읽고 이 템플릿을 수정하여 MCP 서버를 만들 수 있도록 설계되었습니다.

수정 가이드:
1. API 문서를 읽고 필요한 요청/응답 모델을 정의합니다.
2. API 엔드포인트에 맞는 도구 이름을 정의합니다.
3. API 설정(인증, 기본 URL 등)을 구성합니다.
4. API 호출 로직을 구현합니다.

주의사항:
- API 키는 항상 환경변수나 커맨드라인 인자로 전달받아야 합니다.
- 에러 처리를 통해 API 호출 실패 시 적절한 메시지를 반환해야 합니다.
- 디버그 모드에서는 상세한 로깅이 제공되어야 합니다.
"""

import logging
import sys
import json
import traceback
import argparse  # argparse 임포트를 상단으로 이동
from typing import Any, Dict, List, Optional

# 외부 라이브러리
import aiohttp
import anyio
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings

# mcp 라이브러리
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# =========================================================
# 서버 설정
# 커맨드라인 인자와 환경변수를 통합 관리합니다.
# =========================================================

class ServerSettings(BaseSettings):
    """서버 설정
    
    우선순위:
    1. 커맨드라인 인자
    2. 환경변수
    3. .env 파일
    4. 기본값

    
    환경변수 예시:
    - MCP_API_KEY: API 키 (커맨드라인: --API_KEY)
    - MCP_DEBUG: 디버그 모드 (true/false, 커맨드라인: --debug)

    API 문서를 참고하여 필요한 환경변수를 수정 및 추가하세요.
    예시:
    - MCP_API_KEY: API 키
    - MCP_ANOTHER_KEY: 다른 API 키
    """
    API_KEY: str
    debug: bool = False
    
    class Config:
        env_prefix = "MCP_"  # 환경변수 접두사

# =========================================================
# 로깅 설정
# 디버그 모드에서는 더 상세한 로그가 출력됩니다.
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================================================
# API 요청/응답 모델
# =========================================================

# --- 예시 요청 모델 ---
# AI는 실제 API에 맞게 이 모델들을 수정/삭제/추가해야 합니다.
class ExampleTool1RequestModel(BaseModel):
    """예시 도구 1 요청 모델"""
    param1: str  # 필수 파라미터 (이전 query)
    optional_param: int = 10 # 선택적 파라미터 (이전 limit)

class ExampleTool2RequestModel(BaseModel):
    """예시 도구 2 요청 모델"""
    user_id: str
    include_details: bool = False
# --- 예시 요청 모델 끝 ---

# =========================================================
# API 설정 클래스
# =========================================================

class APIConfig:
    """API 설정을 관리하는 클래스
    
    API 키와 엔드포인트별 기본 URL을 관리합니다.
    AI는 이 클래스를 수정하여 실제 API 설정을 반영해야 합니다.
    """
    
    def __init__(self, settings: ServerSettings):
        self.API_KEY = settings.API_KEY
        
        # 여기를 수정하세요: 각 도구 이름(ToolNames의 상수)을 키로,
        # 해당 API 엔드포인트의 기본 URL을 값으로 하는 딕셔너리를 정의합니다.
        self.base_urls: Dict[str, str] = {
            "default": "https://api.example.com/v1",  # 기본 URL 예시 (AI는 실제 기본 URL로 수정, default는 필수가 아닐 수 있습니다)
            "another_endpoint": "https://another.api.example.com/v2", # 다른 엔드포인트 URL 예시
            # 필요한 만큼 도구 이름과 URL을 추가하세요.
            # 예: ToolNames.SEARCH_BLOGS: "https://api.example.com/search/blogs"
        }
    
    def get_base_url(self, endpoint_name: str) -> str:
        """지정된 엔드포인트 이름에 해당하는 기본 URL을 반환합니다.
        
        만약 해당 엔드포인트 이름이 base_urls에 정의되지 않았다면,
        'default' 키에 해당하는 URL을 반환합니다.
        AI는 필요에 따라 이 로직을 수정할 수 있습니다.
        """
        # 먼저 해당 엔드포인트 이름으로 URL 검색
        url = self.base_urls.get(endpoint_name)
        if url:
            return url
        # 없으면 'default' URL 반환 (이것도 없으면 None 반환)
        return self.base_urls.get("default")

    def get_headers(self) -> Dict[str, str]:
        """API 요청에 필요한 헤더를 반환합니다.
        AI는 이 메서드를 실제 API 인증 방식에 맞게 수정해야 합니다.
        """
        return {
            "Authorization": f"Bearer {self.API_KEY}",  # 인증 방식 예시 (Bearer 토큰)
            "Content-Type": "application/json"
        }

# =========================================================
# API 도구 이름 정의
# 각 API 엔드포인트에 대한 도구 이름을 정의하세요.
# =========================================================

class ToolNames:
    """API 도구 이름 상수
    
    이 클래스에 실제 API 엔드포인트에 맞는 도구 이름을 정의하세요.
    도구 이름은 명확하고 직관적이어야 합니다.
    
    아래의 SEARCH와 GET_USER는 예시입니다.
    실제 API에 맞게 이 예시 상수들을 삭제하고 새로운 상수를 정의하세요.
    
    예시:
    - search: 검색 API
    - get_user: 사용자 정보 조회
    - create_post: 게시물 생성
    - update_profile: 프로필 업데이트
    """
    # 아래 상수들은 예시입니다. 실제 구현 시 API에 맞는 상수로 교체하세요.
    SEARCH = "search"        # 이 예시 상수를 삭제하고 실제 API 도구 이름으로 교체하세요
    GET_USER = "get_user"    # 이 예시 상수를 삭제하고 실제 API 도구 이름으로 교체하세요

# =========================================================
# MCP 서버 구현
# =========================================================

async def serve(settings: ServerSettings) -> None:
    """MCP 서버를 실행합니다."""

    if settings.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("디버그 모드가 활성화되었습니다.")

    # API 설정 초기화
    api_config = APIConfig(settings)
    
    # 서버 인스턴스 생성
    server = Server("mcp-api-template")  # 실제 서버 이름으로 수정하세요
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """사용 가능한 API 도구 목록을 반환합니다.
        
        새로운 API 엔드포인트를 추가할 때:
        1. ToolNames에 도구 이름을 추가
        2. 요청 모델 클래스 정의
        3. 여기에 도구 정의 추가
        
        아래 예시 도구들은 실제 API에 맞게 교체하세요.
        """
        return [
            # 아래 도구 정의는 예시입니다. 실제 API에 맞게 수정하세요.
            Tool(
                name=ToolNames.SEARCH,  # 이 예시 상수를 실제 API 도구 이름으로 교체하세요
                description="검색 API를 호출합니다",  # 적절한 설명으로 수정하세요
                inputSchema=SearchRequestModel.schema()  # 적절한 요청 모델로 교체하세요
            ),
            Tool(
                name=ToolNames.GET_USER,  # 이 예시 상수를 실제 API 도구 이름으로 교체하세요
                description="사용자 정보를 조회합니다",  # 적절한 설명으로 수정하세요
                inputSchema=UserRequestModel.schema()  # 적절한 요청 모델로 교체하세요
            )
            # 필요한 만큼 도구를 추가하세요
        ]
        # --- 예시 도구 목록 끝 ---

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """API 도구를 호출합니다.
        
        AI는 이 함수를 수정하여 실제 API 호출을 구현해야 합니다:
        1. API 엔드포인트별 case 추가 (ToolNames 상수 사용)
        2. 인자 검증 (Pydantic 모델 사용 권장)
        3. 각 도구에 맞는 base_url 가져오기 (api_config.get_base_url 사용)
        4. API 호출 구현 (**aiohttp** 사용 권장)
        5. 응답 처리 및 반환 형식 맞추기 (TextContent 리스트)
        6. 에러 처리
        
        아래 case 문의 예시들은 실제 API에 맞게 교체하세요.
        """
        logger.debug(f"도구 호출: {name}, 인자: {arguments}")

        try:
            # 도구에 맞는 base_url 가져오기 (함수 시작 시 확인)
            base_url = api_config.get_base_url(name)
            if not base_url:
                logger.error(f"도구 '{name}'에 대한 base_url 설정 없음 (default 포함)")
                return [TextContent(type="text", text=f"오류: '{name}' 도구의 API URL이 설정되지 않았습니다.")]

            match name:
                # 여기를 수정하세요: 각 ToolNames 상수에 대한 case를 추가합니다.
                # --- 예시 도구 구현 ---
                case ToolNames.EXAMPLE_TOOL_1:
                    # 1. Pydantic 모델로 인자 검증
                    try:
                        request_data = ExampleTool1RequestModel(**arguments)
                    except ValidationError as e:
                        logger.warning(f"'{name}' 인자 검증 오류: {e}")
                        # 사용자에게 친숙한 오류 메시지 생성 (e.errors() 활용 가능)
                        error_details = ', '.join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
                        error_msg = f"오류: 입력값이 잘못되었습니다. ({len(e.errors())}개 오류) - {error_details}"
                        return [TextContent(type="text", text=error_msg)]

                    # 2. API 호출 URL 구성
                    api_endpoint = f"{base_url}/search" # 실제 경로로 수정
                    # Pydantic 모델을 사용하여 파라미터 구성
                    params = request_data.model_dump(exclude_unset=True) # 값이 설정된 필드만 포함

                    # 3. API 호출 (aiohttp 예시)
                    logger.debug(f"'{name}' API 호출: {api_endpoint}, Params: {params}")
                    async with aiohttp.ClientSession(headers=api_config.get_headers()) as session:
                        # HTTP 메서드(GET, POST 등)와 파라미터 전달 방식(json, params 등)은
                        # 실제 API 문서에 맞게 수정해야 합니다.
                        async with session.get(api_endpoint, params=params) as response:
                            response.raise_for_status() # 오류 발생 시 예외 발생
                            result = await response.json()
                            # TODO: 필요한 경우 result를 JSON 문자열 또는 다른 적절한 텍스트 형식으로 가공하여 반환
                            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

                case ToolNames.EXAMPLE_TOOL_2:
                    # 1. Pydantic 모델로 인자 검증
                    try:
                        request_data = ExampleTool2RequestModel(**arguments)
                    except ValidationError as e:
                        logger.warning(f"'{name}' 인자 검증 오류: {e}")
                        error_details = ', '.join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
                        error_msg = f"오류: 입력값이 잘못되었습니다. ({len(e.errors())}개 오류) - {error_details}"
                        return [TextContent(type="text", text=error_msg)]

                    # 2. API 호출 URL 구성 (경로 파라미터 예시)
                    api_endpoint = f"{base_url}/users/{request_data.user_id}"
                    params = {"details": str(request_data.include_details).lower()} # 쿼리 파라미터 (bool->str)

                    # 3. API 호출 (aiohttp 예시)
                    logger.debug(f"'{name}' API 호출: {api_endpoint}, Params: {params}")
                    async with aiohttp.ClientSession(headers=api_config.get_headers()) as session:
                        async with session.get(api_endpoint, params=params) as response:
                            response.raise_for_status()
                            result = await response.json()
                            # TODO: 필요한 경우 result를 가공하여 반환
                            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                # --- 예시 도구 구현 끝 ---

                case _:
                    logger.warning(f"알 수 없는 도구 이름: {name}")
                    return [TextContent(type="text", text=f"오류: 알 수 없는 도구 '{name}' 입니다.")]

        except aiohttp.ClientResponseError as e:
            logger.error(f"API 호출 중 오류 발생 ('{name}'): {e.status} {e.message}")
            # TODO: 사용자에게 더 친숙한 오류 메시지 고려 (e.g., API 서버 문제 가능성 언급)
            return [TextContent(type="text", text=f"API 통신 오류 ({e.status}): 요청 처리 중 문제가 발생했습니다.")]
        except Exception as e:
            logger.error(f"도구 실행 중 예외 발생 ('{name}'): {str(e)}\n{traceback.format_exc()}")
            return [TextContent(type="text", text=f"오류: 도구 '{name}' 실행 중 내부 문제가 발생했습니다.")]

    # 서버 실행
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

# =========================================================
# 커맨드라인 인자 파싱
# =========================================================

def parse_args() -> ServerSettings:
    """커맨드라인 인자를 파싱하여 ServerSettings 객체를 반환합니다.
    
    AI는 API 문서를 참고하여 필요한 인자 (API 키, 설정 등)를 추가해야 합니다.
    인자 이름은 ServerSettings 클래스의 필드 이름과 일치시키는 것이 좋습니다.
    """
    parser = argparse.ArgumentParser(description="MCP API 서버 템플릿")
    
    # 여기를 수정하세요: 필요한 커맨드라인 인자를 추가합니다.
    # ServerSettings에 정의된 필드와 이름을 맞추는 것이 좋습니다.
    parser.add_argument("--API_KEY", help="API 키 (필수, 환경변수 MCP_API_KEY로도 설정 가능)")
    parser.add_argument("--debug", action="store_true", help="디버그 모드 활성화 (환경변수 MCP_DEBUG=true로도 설정 가능)")
    # 예시: parser.add_argument("--ANOTHER_KEY", help="다른 설정값")

    args = parser.parse_args()

    # 여기를 수정하세요: 파싱된 인자를 사용하여 ServerSettings 객체를 생성합니다.
    # 기본값 처리 로직이 필요할 수 있습니다 (예: 인자가 없으면 None 전달).
    # ServerSettings 생성 시 Pydantic이 환경변수, .env 파일 등도 고려함
    # 커맨드라인 인자가 우선순위가 가장 높음
    # args에 없는 필드는 Pydantic이 다른 소스에서 찾음
    try:
        # 커맨드라인 인자가 제공된 경우만 명시적으로 전달
        settings_data = {}
        if args.API_KEY:
            settings_data['API_KEY'] = args.API_KEY
        if args.debug:
            settings_data['debug'] = args.debug
        # 추가된 인자에 대해서도 동일하게 처리

        settings = ServerSettings(**settings_data)

        # 최종적으로 API_KEY가 설정되었는지 확인 (어떤 소스에서든)
        # ServerSettings 정의에 따라 API_KEY는 필수 필드이므로,
        # Pydantic이 값을 찾지 못하면 여기서 ValidationError가 이미 발생했어야 함.
        # 하지만 명시적으로 확인하여 혹시 모를 상황 방지 및 더 명확한 오류 메시지 제공
        if not hasattr(settings, 'API_KEY') or not settings.API_KEY:
             # 이 경우는 사실상 Pydantic 검증 실패 시 발생
             raise ValueError("API_KEY가 설정되지 않았습니다. 커맨드라인 인자(--API_KEY), 환경변수(MCP_API_KEY), 또는 .env 파일을 확인하세요.")

        return settings
    except ValidationError as e:
        logger.error(f"설정 유효성 검사 오류: {e}")
        # 사용자에게 어떤 설정이 문제인지 알려주는 것이 좋음
        error_details = ', '.join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
        print(f"설정 오류: 필요한 설정값이 누락되었거나 잘못되었습니다 - {error_details}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e: # 위에서 raise한 ValueError 포함
        logger.error(f"설정 값 오류: {e}")
        print(f"설정 오류: {e}", file=sys.stderr)
        sys.exit(1)

# =========================================================
# 메인 실행
# =========================================================

if __name__ == "__main__":
    logger.info("서버 초기화 중...")
    settings: Optional[ServerSettings] = None # settings 변수 선언 및 초기화
    try:
        # 설정 로드 (커맨드라인 > 환경변수 > .env 파일 > 기본값)
        # parse_args() 내부에서 ServerSettings가 초기화되면서 설정 로딩이 처리됩니다.
        settings = parse_args() # 여기서 오류 발생 시 sys.exit(1) 호출됨

        # 서버 실행 (anyio 사용)
        logger.info(f"MCP 서버 시작 (API_KEY: {'설정됨' if settings.API_KEY else '설정안됨'}, Debug: {settings.debug})")
        anyio.run(serve, settings)

    except KeyboardInterrupt:
        logger.info("Ctrl+C 감지. 서버를 종료합니다.")
        sys.exit(0)
    except Exception as e:
        # parse_args에서 처리되지 않은 예외 (주로 serve 함수 실행 중 발생)
        log_message = f"서버 실행 중 예기치 않은 오류 발생: {str(e)}\n{traceback.format_exc()}"
        if settings:
             logger.error(log_message)
        else:
             # 설정 로드 중 다른 오류 (이론상 parse_args에서 처리되어야 함)
             logger.error(f"서버 초기화 중 예기치 않은 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"심각한 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        logger.info("서버 종료됨.") 