# -*- coding: utf-8 -*-
"""
Pydantic 스키마 정의
주문 및 메뉴 관련 데이터 모델을 정의합니다.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MenuCategory(str, Enum):
    """메뉴 카테고리 열거형"""
    BURGER = "burger"
    SIDE = "side"
    DRINK = "drink"
    DESSERT = "dessert"


class MenuItem(BaseModel):
    """메뉴 아이템 스키마"""
    id: str = Field(..., description="메뉴 고유 ID")
    name: str = Field(..., description="메뉴 이름")
    category: MenuCategory = Field(..., description="메뉴 카테고리")
    price: int = Field(..., ge=0, description="가격 (원)")
    description: str = Field(..., description="메뉴 설명")
    available: bool = Field(default=True, description="재고 여부")
    options: List[str] = Field(default_factory=list, description="선택 가능한 옵션")
    
    @validator('price')
    def validate_price(cls, v):
        """가격 유효성 검증"""
        if v < 0:
            raise ValueError("가격은 0 이상이어야 합니다")
        return v


class OrderItem(BaseModel):
    """주문 아이템 스키마"""
    menu_id: str = Field(..., description="메뉴 ID")
    menu_name: str = Field(..., description="메뉴 이름")
    quantity: int = Field(..., ge=1, description="수량")
    price: int = Field(..., ge=0, description="단가")
    options: List[str] = Field(default_factory=list, description="선택된 옵션")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """수량 유효성 검증"""
        if v < 1:
            raise ValueError("수량은 1 이상이어야 합니다")
        if v > 99:
            raise ValueError("수량은 99 이하여야 합니다")
        return v
    
    @property
    def total_price(self) -> int:
        """아이템 총 가격 계산"""
        return self.price * self.quantity


class Order(BaseModel):
    """주문 스키마"""
    order_id: str = Field(..., description="주문 고유 ID")
    items: List[OrderItem] = Field(default_factory=list, description="주문 아이템 목록")
    created_at: datetime = Field(default_factory=datetime.now, description="주문 생성 시간")
    customer_id: Optional[str] = Field(None, description="고객 ID")
    status: str = Field(default="pending", description="주문 상태")
    special_request: Optional[str] = Field(None, description="특별 요청사항")
    
    @property
    def total_price(self) -> int:
        """주문 총 가격 계산"""
        return sum(item.total_price for item in self.items)
    
    @property
    def item_count(self) -> int:
        """총 아이템 개수"""
        return sum(item.quantity for item in self.items)


class AgentAction(BaseModel):
    """에이전트 액션 스키마"""
    action_type: str = Field(..., description="액션 타입")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="액션 파라미터")
    timestamp: datetime = Field(default_factory=datetime.now, description="실행 시간")


class AgentResponse(BaseModel):
    """에이전트 응답 스키마"""
    message: str = Field(..., description="응답 메시지")
    action: Optional[AgentAction] = Field(None, description="실행된 액션")
    success: bool = Field(default=True, description="성공 여부")
    error: Optional[str] = Field(None, description="에러 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")


class ValidationResult(BaseModel):
    """검증 결과 스키마"""
    is_valid: bool = Field(..., description="유효성 여부")
    errors: List[str] = Field(default_factory=list, description="에러 목록")
    warnings: List[str] = Field(default_factory=list, description="경고 목록")