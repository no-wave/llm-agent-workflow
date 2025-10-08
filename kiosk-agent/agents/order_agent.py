"""
주문 에이전트 모듈
햄버거 주문을 처리하는 메인 에이전트
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from agents.base_agent import BaseAgent
from tools.menu_tools import MenuTools, MENU_TOOL_DEFINITIONS
from tools.order_tools import OrderTools, ORDER_TOOL_DEFINITIONS
from utils.validation import OrderValidator, InputSanitizer
from models.schemas import AgentResponse


class OrderAgent(BaseAgent):
    """주문 처리 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        주문 에이전트 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        system_prompt = """
        당신은 햄버거 가게의 친절한 주문 키오스크 AI 직원입니다.
        
        역할:
        1. 고객의 주문을 정확하게 받습니다
        2. 메뉴에 대한 정보를 제공합니다
        3. 추가 주문이나 사이드 메뉴를 제안합니다
        4. 주문 내역을 확인하고 최종 확정을 도와줍니다
        5. 친절하고 명확하게 응대합니다
        
        지침:
        - 항상 예의바르고 친절하게 응대하세요
        - 고객의 의도를 정확히 파악하세요
        - 주문 내역을 명확히 확인하세요
        - 필요시 추가 질문을 하세요
        - 주문 완료 시 감사 인사를 전하세요
        """
        
        super().__init__(
            name="OrderAgent",
            system_prompt=system_prompt,
            api_key=api_key
        )
        
        # 도구 초기화
        self.menu_tools = MenuTools()
        self.order_tools = OrderTools()
        self.validator = OrderValidator()
        self.sanitizer = InputSanitizer()
        
        # 모든 도구 정의
        self.tools = MENU_TOOL_DEFINITIONS + ORDER_TOOL_DEFINITIONS
    
    @staticmethod
    def _json_serializer(obj):
        """
        JSON 직렬화를 위한 커스텀 serializer
        datetime 객체를 문자열로 변환
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    async def process(
        self,
        user_input: str,
        user_id: Optional[str] = None
    ) -> AgentResponse:
        """
        사용자 입력 처리 (도구 호출 포함)
        
        Args:
            user_input: 사용자 입력
            user_id: 사용자 ID
            
        Returns:
            에이전트 응답
        """
        try:
            # 입력 검증 및 정제
            validation_result = self.validator.validate_user_input(user_input)
            if not validation_result.is_valid:
                error_message = self.error_handler.handle_validation_error(
                    validation_result.errors
                )
                return AgentResponse(
                    message=error_message,
                    success=False
                )
            
            user_input = self.sanitizer.sanitize_text(user_input)
            
            # 메모리에 추가
            await self.memory.add_message("user", user_input, user_id)
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # LLM 호출 (도구 사용 포함)
            success, result = await self.recovery.retry_async(
                self._call_llm_with_tools,
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
    
    async def _call_llm_with_tools(self, user_input: str) -> str:
        """
        도구 호출을 포함한 LLM 호출
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            최종 응답 메시지
        """
        # 메시지 준비
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 최근 대화 기록 추가
        recent_history = self.conversation_history[-10:]
        messages.extend(recent_history)
        
        # 반복적으로 도구 호출 처리
        max_iterations = 5
        for iteration in range(max_iterations):
            # LLM 호출 (temperature 제거)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # 도구 호출이 없으면 응답 반환
            if not response_message.tool_calls:
                return response_message.content
            
            # 메시지 히스토리에 어시스턴트 응답 추가
            messages.append(response_message)
            
            # 각 도구 호출 처리
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                
                # JSON 파싱 시 인코딩 에러 처리
                try:
                    # arguments가 문자열인지 확인
                    args_str = tool_call.function.arguments
                    if isinstance(args_str, bytes):
                        args_str = args_str.decode('utf-8', errors='ignore')
                    
                    function_args = json.loads(args_str)
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
                    print(f"JSON 파싱 에러: {e}")
                    print(f"원본 데이터: {tool_call.function.arguments}")
                    # 기본값 사용
                    function_args = {}
                
                # 도구 실행
                try:
                    function_response = self._execute_tool(
                        function_name,
                        function_args
                    )
                except Exception as e:
                    print(f"도구 실행 에러 ({function_name}): {e}")
                    function_response = {
                        "success": False,
                        "message": f"도구 실행 실패: {str(e)}"
                    }
                
                # 도구 응답을 메시지에 추가
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response, ensure_ascii=False, default=self._json_serializer)
                })
        
        # 최대 반복 도달 시 마지막 메시지 반환
        return "주문 처리 중 문제가 발생했습니다. 다시 시도해주세요."
    
    def _execute_tool(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        도구 실행
        
        Args:
            function_name: 함수 이름
            arguments: 함수 인자
            
        Returns:
            함수 실행 결과
        """
        # 메뉴 도구
        if function_name == "get_menu_info":
            return self.menu_tools.get_menu_info(**arguments)
        elif function_name == "get_all_menus":
            return self.menu_tools.get_all_menus()
        elif function_name == "get_menus_by_category":
            return self.menu_tools.get_menus_by_category(**arguments)
        elif function_name == "search_menus":
            return self.menu_tools.search_menus(**arguments)
        
        # 주문 도구
        elif function_name == "add_item":
            return self.order_tools.add_item(**arguments)
        elif function_name == "remove_item":
            return self.order_tools.remove_item(**arguments)
        elif function_name == "get_current_order":
            return self.order_tools.get_current_order()
        elif function_name == "confirm_order":
            return self.order_tools.confirm_order()
        elif function_name == "add_special_request":
            return self.order_tools.add_special_request(**arguments)
        
        else:
            return {
                "success": False,
                "message": f"알 수 없는 함수: {function_name}"
            }
    
    def get_current_order_info(self) -> Dict[str, Any]:
        """
        현재 주문 정보 조회
        
        Returns:
            주문 정보
        """
        return self.order_tools.get_current_order()
    
    def validate_current_order(self) -> Dict[str, Any]:
        """
        현재 주문 검증
        
        Returns:
            검증 결과
        """
        order_info = self.order_tools.get_current_order()
        if not order_info["success"] or not order_info["order"]:
            return {
                "is_valid": False,
                "errors": ["주문이 비어있습니다"],
                "warnings": []
            }
        
        from models.schemas import Order
        order = Order(**order_info["order"])
        validation_result = self.validator.validate_order(order)
        
        return validation_result.dict()
    
    async def reset_order(self, user_id: Optional[str] = None):
        """
        주문 및 대화 초기화
        
        Args:
            user_id: 사용자 ID
        """
        self.order_tools.clear_order()
        await self.reset(user_id)