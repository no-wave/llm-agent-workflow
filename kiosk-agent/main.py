"""
햄버거 키오스크 메인 실행 파일
"""
import asyncio
from typing import Optional
from agents.order_agent import OrderAgent
from models.schemas import AgentResponse


class KioskInterface:
    """키오스크 인터페이스 클래스"""
    
    def __init__(self):
        """키오스크 초기화"""
        self.agent = OrderAgent()
        self.session_id = None
        self.is_running = False
    
    async def start(self):
        """키오스크 시작"""
        self.is_running = True
        print("\n" + "="*60)
        print("      햄버거 가게 주문 키오스크에 오신 것을 환영합니다!")
        print("="*60)
        print("\n사용 가능한 명령어:")
        print("  - '메뉴'또는 '메뉴 보여줘': 전체 메뉴 확인")
        print("  - '주문': 메뉴 주문하기")
        print("  - '확인': 현재 주문 내역 확인")
        print("  - '취소': 주문 초기화")
        print("  - '종료': 프로그램 종료")
        print("\n자연스럽게 대화하듯이 주문하실 수 있습니다!")
        print("예: '클래식 버거 2개랑 콜라 주세요'\n")
        
        await self._main_loop()
    
    async def _main_loop(self):
        """메인 실행 루프"""
        while self.is_running:
            try:
                # 사용자 입력 받기
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                
                # 종료 명령 확인
                if self._is_exit_command(user_input):
                    await self._handle_exit()
                    break
                
                # 취소 명령 확인
                if self._is_cancel_command(user_input):
                    await self._handle_cancel()
                    continue
                
                # 에이전트로 입력 전달
                response = await self.agent.process(user_input, self.session_id)
                
                # 응답 출력
                self._display_response(response)
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"\n오류 발생: {e}")
                print(f"오류 타입: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                print("다시 시도해주세요.\n")
    
    async def _get_user_input(self) -> str:
        """
        사용자 입력 받기
        
        Returns:
            사용자 입력
        """
        try:
            # asyncio에서 input 사용
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(
                None,
                input,
                "\n고객님: "
            )
            return user_input.strip()
        except EOFError:
            return ""
    
    def _display_response(self, response: AgentResponse):
        """
        응답 출력
        
        Args:
            response: 에이전트 응답
        """
        print(f"\n키오스크: {response.message}")
        
        if not response.success and response.error:
            print(f"[오류 정보: {response.error}]")
        
        # 추가 정보 출력
        if response.data:
            if "total_price" in response.data:
                print(f"\n현재 주문 금액: {response.data['total_price']:,}원")
    
    def _is_exit_command(self, user_input: str) -> bool:
        """
        종료 명령어 확인
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            종료 명령어 여부
        """
        exit_keywords = ["종료", "끝", "exit", "quit", "bye"]
        return any(keyword in user_input.lower() for keyword in exit_keywords)
    
    def _is_cancel_command(self, user_input: str) -> bool:
        """
        취소 명령어 확인
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            취소 명령어 여부
        """
        cancel_keywords = ["취소", "초기화", "처음부터", "cancel", "reset"]
        return any(keyword in user_input.lower() for keyword in cancel_keywords)
    
    async def _handle_exit(self):
        """종료 처리"""
        print("\n주문을 확정하시겠습니까? (예/아니오)")
        
        loop = asyncio.get_event_loop()
        confirm = await loop.run_in_executor(None, input, "답변: ")
        
        if confirm.strip().lower() in ["예", "yes", "y", "네"]:
            # 주문 확정
            order_info = self.agent.get_current_order_info()
            if order_info["success"] and order_info["order"]:
                validation = self.agent.validate_current_order()
                
                if validation["is_valid"]:
                    confirm_result = self.agent.order_tools.confirm_order()
                    print(f"\n{confirm_result['message']}")
                    print("\n" + confirm_result['summary'])
                    print("\n주문해주셔서 감사합니다!")
                else:
                    print("\n주문에 오류가 있습니다:")
                    for error in validation["errors"]:
                        print(f"  - {error}")
            else:
                print("\n주문 내역이 없습니다.")
        
        print("\n다음에 또 이용해주세요. 감사합니다!")
        self.is_running = False
    
    async def _handle_cancel(self):
        """취소 처리"""
        await self.agent.reset_order(self.session_id)
        print("\n주문이 초기화되었습니다. 새로 주문하실 수 있습니다.")


async def main():
    """메인 함수"""
    try:
        kiosk = KioskInterface()
        await kiosk.start()
    except Exception as e:
        print(f"\n프로그램 실행 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())