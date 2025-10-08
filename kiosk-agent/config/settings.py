# -*- coding: utf-8 -*-
"""
설정 관리 모듈
환경 변수 및 애플리케이션 설정을 관리합니다.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    환경 변수에서 설정을 로드합니다.
    """
    
    # OpenAI 설정
    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    
    # Mem0 설정
    mem0_api_key: Optional[str] = None
    
    # 애플리케이션 설정
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # 시스템 프롬프트
    system_prompt: str = """
    당신은 햄버거 가게의 친절한 주문 키오스크 AI 직원입니다.
    고객의 주문을 정확하게 받고, 추가 주문을 제안하며, 최종 확인을 도와줍니다.
    항상 예의바르고 명확하게 응대하세요.
    """
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()