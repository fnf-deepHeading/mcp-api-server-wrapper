#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 서버 템플릿
이 파일의 표시된 부분만 수정하여 API를 래핑하세요.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp-server")

# =========================================================
# 여기부터 수정하세요
# =========================================================

# API 설정 클래스
@dataclass
class APISettings:
    """API 설정"""
    api_url: str = "YOUR_API_URL"  # 여기에 API URL 입력
    api_key: str = ""              # 커맨드라인이나 환경변수에서 설정

# =========================================================
# 여기까지 수정하세요
# =========================================================

def parse_args():
    """커맨드 라인 인자를 파싱합니다."""
    parser = argparse.ArgumentParser(description='MCP 서버')
    
    # =========================================================
    # 여기부터 수정하세요
    # =========================================================
    
    # API 인증 설정 (필요한 인자를 추가하세요)
    parser.add_argument('--api_key', help='API 키 (환경변수 API_KEY로도 설정 가능)')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    
    # =========================================================
    # 여기까지 수정하세요
    # =========================================================
    
    args = parser.parse_args()
    return args

# =========================================================
# 여기부터 수정하세요
# =========================================================

# 서버 수명주기 관리
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
    settings.api_key = args.api_key or os.getenv("API_KEY")
    if not settings.api_key:
        raise ValueError("API 키가 설정되지 않았습니다. --api_key 옵션이나 API_KEY 환경변수를 설정해주세요.")
    
    try:
        yield settings
    finally:
        logger.info("서버 종료 중...")

# =========================================================
# 여기까지 수정하세요
# =========================================================

# MCP 서버 생성 (여기에서 서버 이름을 수정하세요)
SERVER_NAME = "MCP-Server"  # 이 부분을 원하는 이름으로 변경하세요 (예: "Naver-Trend-MCP")

mcp = FastMCP(
    SERVER_NAME,
    host="0.0.0.0",
    port=8080,
    lifespan=app_lifespan,
    dependencies=["requests"]
)

# =========================================================
# 여기부터 수정하세요
# =========================================================

@mcp.tool()
async def my_api_call(
    ctx: Context,
    param1: str,    # 필요한 파라미터로 수정
    param2: int     # 필요한 파라미터로 수정
) -> str:
    """API 설명을 여기에 작성"""
    try:
        # 설정 가져오기
        settings = ctx.request_context.lifespan_context
        
        # API 호출 (메서드와 파라미터를 수정하세요)
        response = requests.get(
            settings.api_url,
            headers={
                "Authorization": f"Bearer {settings.api_key}"  # 인증 방식에 맞게 수정
            },
            params={
                "param1": param1,
                "param2": param2
            }
        )
        
        # 응답 확인
        response.raise_for_status()
        
        # 응답 반환 (필요한 경우 수정하세요)
        return response.json()
        
    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {str(e)}")
        return {"error": str(e)}

# =========================================================
# 여기까지 수정하세요
# =========================================================

def main():
    """MCP 서버 실행"""
    try:
        # 서버 시작
        logger.info("MCP 서버 시작")
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("서버가 종료되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 