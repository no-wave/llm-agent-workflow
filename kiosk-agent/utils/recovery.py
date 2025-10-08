# -*- coding: utf-8 -*-
"""
에러 복구 유틸리티 모듈
에러 처리 및 재시도 로직
"""
import asyncio
from typing import Callable, Any, Optional, TypeVar, Dict
from functools import wraps
import traceback
from datetime import datetime


T = TypeVar('T')


class RecoveryManager:
    """에러 복구 관리 클래스"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        복구 관리자 초기화
        
        Args:
            max_retries: 최대 재시도 횟수
            base_delay: 기본 지연 시간 (초)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_log: list = []
    
    async def retry_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[bool, Any]:
        """
        비동기 함수 재시도
        
        Args:
            func: 실행할 비동기 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            (성공 여부, 결과 또는 에러)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                self._log_error(func.__name__, e, attempt + 1)
                
                if attempt < self.max_retries - 1:
                    # 지수 백오프
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        return False, last_error
    
    def retry_sync(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[bool, Any]:
        """
        동기 함수 재시도
        
        Args:
            func: 실행할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            (성공 여부, 결과 또는 에러)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                self._log_error(func.__name__, e, attempt + 1)
                
                if attempt < self.max_retries - 1:
                    # 지수 백오프
                    import time
                    delay = self.base_delay * (2 ** attempt)
                    time.sleep(delay)
        
        return False, last_error
    
    def _log_error(self, func_name: str, error: Exception, attempt: int):
        """
        에러 로깅
        
        Args:
            func_name: 함수 이름
            error: 에러 객체
            attempt: 시도 횟수
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "function": func_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "attempt": attempt,
            "traceback": traceback.format_exc()
        }
        self.error_log.append(error_info)
        
        print(f"[에러 {attempt}/{self.max_retries}] {func_name}: {error}")
    
    def get_error_log(self) -> list:
        """
        에러 로그 조회
        
        Returns:
            에러 로그 리스트
        """
        return self.error_log
    
    def clear_error_log(self):
        """에러 로그 초기화"""
        self.error_log = []


def with_recovery(max_retries: int = 3, base_delay: float = 1.0):
    """
    에러 복구 데코레이터 (비동기 함수용)
    
    Args:
        max_retries: 최대 재시도 횟수
        base_delay: 기본 지연 시간
        
    Returns:
        데코레이터 함수
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"[재시도 {attempt + 1}/{max_retries}] {func.__name__}: {e}")
                    
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            
            # 모든 재시도 실패
            raise last_error
        
        return wrapper
    return decorator


def with_fallback(fallback_value: Any = None):
    """
    대체값 제공 데코레이터
    
    Args:
        fallback_value: 에러 시 반환할 대체값
        
    Returns:
        데코레이터 함수
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"[대체값 사용] {func.__name__}: {e}")
                return fallback_value
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[대체값 사용] {func.__name__}: {e}")
                return fallback_value
        
        # 비동기 함수 여부 확인
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class ErrorHandler:
    """에러 핸들러 클래스"""
    
    @staticmethod
    def handle_api_error(error: Exception) -> Dict[str, Any]:
        """
        API 에러 처리
        
        Args:
            error: 에러 객체
            
        Returns:
            에러 응답 딕셔너리
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # 에러 타입별 처리
        if "timeout" in error_message.lower():
            return {
                "success": False,
                "error_type": "timeout",
                "message": "요청 시간이 초과되었습니다. 다시 시도해주세요.",
                "recoverable": True
            }
        elif "rate limit" in error_message.lower():
            return {
                "success": False,
                "error_type": "rate_limit",
                "message": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                "recoverable": True
            }
        elif "authentication" in error_message.lower():
            return {
                "success": False,
                "error_type": "authentication",
                "message": "인증에 실패했습니다. 설정을 확인해주세요.",
                "recoverable": False
            }
        else:
            return {
                "success": False,
                "error_type": error_type,
                "message": f"오류가 발생했습니다: {error_message}",
                "recoverable": True
            }
    
    @staticmethod
    def handle_validation_error(errors: list) -> str:
        """
        검증 에러 메시지 생성
        
        Args:
            errors: 에러 리스트
            
        Returns:
            포맷팅된 에러 메시지
        """
        if not errors:
            return ""
        
        if len(errors) == 1:
            return f"오류: {errors[0]}"
        
        error_lines = ["다음 오류들이 발견되었습니다:"]
        for i, error in enumerate(errors, 1):
            error_lines.append(f"{i}. {error}")
        
        return "\n".join(error_lines)
    
    @staticmethod
    def create_user_friendly_message(error: Exception) -> str:
        """
        사용자 친화적 에러 메시지 생성
        
        Args:
            error: 에러 객체
            
        Returns:
            친화적인 에러 메시지
        """
        error_message = str(error).lower()
        
        # 일반적인 에러 메시지 매핑
        if "connection" in error_message:
            return "네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해주세요."
        elif "not found" in error_message:
            return "요청하신 항목을 찾을 수 없습니다."
        elif "invalid" in error_message:
            return "입력하신 정보가 올바르지 않습니다."
        elif "permission" in error_message or "forbidden" in error_message:
            return "권한이 없습니다."
        else:
            return "일시적인 오류가 발생했습니다. 다시 시도해주세요."


# 전역 복구 관리자 인스턴스
recovery_manager = RecoveryManager()