# -*- coding: utf-8 -*-
"""
주문 관련 도구 모듈
주문 생성, 수정, 확인 기능을 제공합니다.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from models.schemas import Order, OrderItem
from models.menu import menu_db


class OrderTools:
    """주문 관련 도구 클래스"""
    
    def __init__(self):
        """주문 저장소 초기화"""
        self.current_order: Optional[Order] = None
    
    def create_order(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        새 주문 생성
        
        Args:
            customer_id: 고객 ID (선택)
            
        Returns:
            생성된 주문 정보
        """
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        self.current_order = Order(
            order_id=order_id,
            customer_id=customer_id
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "message": "새 주문이 생성되었습니다."
        }
    
    def add_item(self, menu_name: str, quantity: int = 1, 
                 options: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        주문에 아이템 추가
        
        Args:
            menu_name: 메뉴 이름
            quantity: 수량
            options: 선택 옵션
            
        Returns:
            추가 결과
        """
        if not self.current_order:
            self.create_order()
        
        # 메뉴 조회
        menu = menu_db.get_menu_by_name(menu_name)
        if not menu:
            return {
                "success": False,
                "message": f"'{menu_name}' 메뉴를 찾을 수 없습니다."
            }
        
        if not menu.available:
            return {
                "success": False,
                "message": f"'{menu.name}'은(는) 현재 품절입니다."
            }
        
        # 주문 아이템 생성
        try:
            order_item = OrderItem(
                menu_id=menu.id,
                menu_name=menu.name,
                quantity=quantity,
                price=menu.price,
                options=options or []
            )
            
            # 기존 아이템과 병합 또는 추가
            existing_item = self._find_existing_item(menu.id, options or [])
            if existing_item:
                existing_item.quantity += quantity
                message = f"{menu.name} 수량이 {existing_item.quantity}개로 업데이트되었습니다."
            else:
                self.current_order.items.append(order_item)
                message = f"{menu.name} {quantity}개가 추가되었습니다."
            
            return {
                "success": True,
                "item": order_item.dict(),
                "total_items": self.current_order.item_count,
                "total_price": self.current_order.total_price,
                "message": message
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"아이템 추가 실패: {str(e)}"
            }
    
    def remove_item(self, menu_name: str, quantity: Optional[int] = None) -> Dict[str, Any]:
        """
        주문에서 아이템 제거
        
        Args:
            menu_name: 메뉴 이름
            quantity: 제거할 수량 (None이면 전체 제거)
            
        Returns:
            제거 결과
        """
        if not self.current_order or not self.current_order.items:
            return {
                "success": False,
                "message": "주문이 비어있습니다."
            }
        
        # 아이템 찾기
        for i, item in enumerate(self.current_order.items):
            if menu_name.lower() in item.menu_name.lower():
                if quantity is None or quantity >= item.quantity:
                    # 전체 제거
                    removed_item = self.current_order.items.pop(i)
                    message = f"{removed_item.menu_name}이(가) 주문에서 제거되었습니다."
                else:
                    # 일부 제거
                    item.quantity -= quantity
                    message = f"{item.menu_name} {quantity}개가 제거되었습니다. (남은 수량: {item.quantity})"
                
                return {
                    "success": True,
                    "total_items": self.current_order.item_count,
                    "total_price": self.current_order.total_price,
                    "message": message
                }
        
        return {
            "success": False,
            "message": f"'{menu_name}'을(를) 주문에서 찾을 수 없습니다."
        }
    
    def get_current_order(self) -> Dict[str, Any]:
        """
        현재 주문 조회
        
        Returns:
            현재 주문 정보
        """
        if not self.current_order or not self.current_order.items:
            return {
                "success": True,
                "order": None,
                "message": "현재 주문이 비어있습니다."
            }
        
        return {
            "success": True,
            "order": self.current_order.dict(),
            "total_price": self.current_order.total_price,
            "item_count": self.current_order.item_count,
            "message": "현재 주문 내역입니다."
        }
    
    def clear_order(self) -> Dict[str, Any]:
        """
        주문 초기화
        
        Returns:
            초기화 결과
        """
        self.current_order = None
        return {
            "success": True,
            "message": "주문이 초기화되었습니다."
        }
    
    def confirm_order(self) -> Dict[str, Any]:
        """
        주문 확정
        
        Returns:
            확정 결과
        """
        if not self.current_order or not self.current_order.items:
            return {
                "success": False,
                "message": "주문이 비어있어 확정할 수 없습니다."
            }
        
        self.current_order.status = "confirmed"
        order_summary = self._format_order_summary()
        
        return {
            "success": True,
            "order": self.current_order.dict(),
            "summary": order_summary,
            "message": "주문이 확정되었습니다."
        }
    
    def add_special_request(self, request: str) -> Dict[str, Any]:
        """
        특별 요청사항 추가
        
        Args:
            request: 요청사항
            
        Returns:
            추가 결과
        """
        if not self.current_order:
            self.create_order()
        
        self.current_order.special_request = request
        return {
            "success": True,
            "message": f"요청사항이 추가되었습니다: {request}"
        }
    
    def _find_existing_item(self, menu_id: str, options: List[str]) -> Optional[OrderItem]:
        """
        동일한 메뉴와 옵션을 가진 기존 아이템 찾기
        
        Args:
            menu_id: 메뉴 ID
            options: 옵션 리스트
            
        Returns:
            OrderItem 또는 None
        """
        if not self.current_order:
            return None
        
        for item in self.current_order.items:
            if item.menu_id == menu_id and set(item.options) == set(options):
                return item
        return None
    
    def _format_order_summary(self) -> str:
        """
        주문 요약 포맷팅
        
        Returns:
            포맷팅된 주문 요약
        """
        if not self.current_order:
            return "주문 없음"
        
        lines = [f"주문번호: {self.current_order.order_id}", ""]
        
        for item in self.current_order.items:
            lines.append(f"- {item.menu_name} x {item.quantity}")
            if item.options:
                lines.append(f"  옵션: {', '.join(item.options)}")
            lines.append(f"  {item.total_price:,}원")
        
        lines.append("")
        lines.append(f"총 수량: {self.current_order.item_count}개")
        lines.append(f"총 금액: {self.current_order.total_price:,}원")
        
        if self.current_order.special_request:
            lines.append(f"요청사항: {self.current_order.special_request}")
        
        return "\n".join(lines)


# 도구 함수 매핑 (OpenAI Function Calling용)
ORDER_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_item",
            "description": "주문에 메뉴 아이템을 추가합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_name": {
                        "type": "string",
                        "description": "추가할 메뉴 이름"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "수량",
                        "default": 1
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "선택 옵션 리스트"
                    }
                },
                "required": ["menu_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_item",
            "description": "주문에서 메뉴 아이템을 제거합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_name": {
                        "type": "string",
                        "description": "제거할 메뉴 이름"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "제거할 수량 (없으면 전체 제거)"
                    }
                },
                "required": ["menu_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_order",
            "description": "현재 주문 내역을 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_order",
            "description": "주문을 최종 확정합니다",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_special_request",
            "description": "특별 요청사항을 추가합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "특별 요청사항"
                    }
                },
                "required": ["request"]
            }
        }
    }
]