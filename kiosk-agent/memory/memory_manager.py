# -*- coding: utf-8 -*-
"""
메모리 관리 모듈
Mem0ai를 사용한 대화 기록 및 컨텍스트 관리
"""
from typing import List, Dict, Any, Optional
from mem0 import Memory
from config.settings import settings


class MemoryManager:
    """메모리 관리 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        메모리 관리자 초기화
        
        Args:
            api_key: Mem0 API 키 (선택)
        """
        self.api_key = api_key or settings.mem0_api_key
        
        # Mem0 메모리 초기화
        try:
            if self.api_key:
                self.memory = Memory(api_key=self.api_key)
            else:
                # API 키가 없으면 로컬 메모리 사용
                self.memory = Memory()
            self.enabled = True
        except Exception as e:
            print(f"메모리 초기화 실패: {e}")
            self.memory = None
            self.enabled = False
        
        # 로컬 대화 기록 백업
        self.conversation_history: List[Dict[str, str]] = []
    
    async def add_message(self, role: str, content: str, 
                         user_id: Optional[str] = None) -> bool:
        """
        메시지를 메모리에 추가
        
        Args:
            role: 메시지 역할 (user/assistant)
            content: 메시지 내용
            user_id: 사용자 ID
            
        Returns:
            성공 여부
        """
        # 로컬 기록에 추가
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Mem0에 저장
        if self.enabled and self.memory:
            try:
                self.memory.add(
                    messages=[{"role": role, "content": content}],
                    user_id=user_id or "default"
                )
                return True
            except Exception as e:
                print(f"메모리 추가 실패: {e}")
                return False
        
        return True
    
    async def get_conversation_history(self, 
                                      user_id: Optional[str] = None,
                                      limit: int = 10) -> List[Dict[str, str]]:
        """
        대화 기록 조회
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 메시지 수
            
        Returns:
            대화 기록 리스트
        """
        if self.enabled and self.memory:
            try:
                memories = self.memory.get_all(
                    user_id=user_id or "default"
                )
                return memories[-limit:] if memories else []
            except Exception as e:
                print(f"메모리 조회 실패: {e}")
        
        # 로컬 기록 반환
        return self.conversation_history[-limit:]
    
    async def search_memories(self, query: str, 
                             user_id: Optional[str] = None,
                             limit: int = 5) -> List[Dict[str, Any]]:
        """
        메모리 검색
        
        Args:
            query: 검색 쿼리
            user_id: 사용자 ID
            limit: 결과 수
            
        Returns:
            검색 결과 리스트
        """
        if self.enabled and self.memory:
            try:
                results = self.memory.search(
                    query=query,
                    user_id=user_id or "default",
                    limit=limit
                )
                return results
            except Exception as e:
                print(f"메모리 검색 실패: {e}")
        
        # 로컬 검색 (간단한 키워드 매칭)
        results = []
        for msg in self.conversation_history:
            if query.lower() in msg.get("content", "").lower():
                results.append(msg)
                if len(results) >= limit:
                    break
        
        return results
    
    async def clear_history(self, user_id: Optional[str] = None) -> bool:
        """
        대화 기록 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            성공 여부
        """
        # 로컬 기록 초기화
        self.conversation_history = []
        
        # Mem0 메모리 삭제
        if self.enabled and self.memory:
            try:
                self.memory.delete_all(user_id=user_id or "default")
                return True
            except Exception as e:
                print(f"메모리 삭제 실패: {e}")
                return False
        
        return True
    
    async def get_context_summary(self, 
                                 user_id: Optional[str] = None) -> str:
        """
        현재 컨텍스트 요약
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            컨텍스트 요약
        """
        history = await self.get_conversation_history(user_id, limit=5)
        
        if not history:
            return "대화 기록이 없습니다."
        
        summary_parts = []
        for msg in history:
            role = "고객" if msg.get("role") == "user" else "키오스크"
            content = msg.get("content", "")[:100]  # 최대 100자
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    def get_local_history(self) -> List[Dict[str, str]]:
        """
        로컬 대화 기록 조회 (동기)
        
        Returns:
            대화 기록 리스트
        """
        return self.conversation_history
    
    def add_to_local_history(self, role: str, content: str):
        """
        로컬 대화 기록에 추가 (동기)
        
        Args:
            role: 메시지 역할
            content: 메시지 내용
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })