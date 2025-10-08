"""
기본 에이전트 클래스
모든 에이전트의 베이스 클래스
"""
from typing import List, Dict, Any, Optional
import asyncio
from openai import AsyncOpenAI
from config.settings import settings
from memory.memory_manager import MemoryManager
from utils.recovery import RecoveryManager, ErrorHandler
from models.schemas import AgentResponse


class BaseAgent:
    """기본 에이전트 클래스"""
    
    def __init__(
        self,
        name: str = "BaseAgent",
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        에이전트 초기화
        
        Args:
            name: 에이전트 이름
            system_prompt: 시스템 프롬프트
            api_key: OpenAI API 키
        """
        self.name = name
        self.system_prompt = system_prompt or settings.system_prompt
        
        # OpenAI 클라이언트 초기화
        self.client = AsyncOpenAI(
            api_key=api_key or settings.openai_api_key
        )
        self.model = settings.openai_model
        
        # 메모리 관리자
        self.memory = MemoryManager()
        
        # 복구 관리자
        self.recovery = RecoveryManager(
            max_retries=settings.max_retries
        )
        
        # 에러 핸들러
        self.error_handler = ErrorHandler()
        
        # 대화 기록
        self.conversation_history: List[Dict[str, str]] = []
    
    async def process(
        self,
        user_input: str,
        user_id: Optional[str] = None
    ) -> AgentResponse:
        """
        사용자 입력 처리
        
        Args:
            user_input: 사용자 입력
            user_id: 사용자 ID
            
        Returns:
            에이전트 응답
        """
        try:
            # 메모리에 사용자 메시지 추가
            await self.memory.add_message("user", user_input, user_id)
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # LLM 호출 (재시도 로직 포함)
            success, result = await self.recovery.retry_async(
                self._call_llm,
                user_input
            )
            
            if not success:
                error_info = self.error_handler.handle_api_error(result)
                return AgentResponse(
                    message=error_info["message"],
                    success=False,
                    error=str(result)
                )
            
            response_message = result
            
            # 메모리에 응답 추가
            await self.memory.add_message("assistant", response_message, user_id)
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message
            })
            
            return AgentResponse(
                message=response_message,
                success=True
            )
            
        except Exception as e:
            error_message = self.error_handler.create_user_friendly_message(e)
            return AgentResponse(
                message=error_message,
                success=False,
                error=str(e)
            )
    
    async def _call_llm(self, user_input: str) -> str:
        """
        LLM 호출
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            LLM 응답
        """
        # 메시지 준비
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 최근 대화 기록 추가 (최대 10개)
        recent_history = self.conversation_history[-10:]
        messages.extend(recent_history)
        
        # LLM 호출 (temperature 제거)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        
        return response.choices[0].message.content
    
    async def reset(self, user_id: Optional[str] = None):
        """
        에이전트 상태 초기화
        
        Args:
            user_id: 사용자 ID
        """
        self.conversation_history = []
        await self.memory.clear_history(user_id)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        대화 기록 조회
        
        Returns:
            대화 기록 리스트
        """
        return self.conversation_history
    
    async def get_context_summary(self, user_id: Optional[str] = None) -> str:
        """
        현재 컨텍스트 요약
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            컨텍스트 요약
        """
        return await self.memory.get_context_summary(user_id)