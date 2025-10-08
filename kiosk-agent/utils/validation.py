# -*- coding: utf-8 -*-
"""
검증 유틸리티 모듈
입력 데이터 및 주문 검증 기능
"""
from typing import List, Dict, Any
from models.schemas import ValidationResult, Order, OrderItem
from models.menu import menu_db


class OrderValidator:
    """주문 검증 클래스"""
    
    @staticmethod
    def validate_order(order: Order) -> ValidationResult:
        """
        주문 전체 검증
        
        Args:
            order: 검증할 주문
            
        Returns:
            검증 결과
        """
        errors = []
        warnings = []
        
        # 주문 아이템 존재 확인
        if not order.items:
            errors.append("주문에 아이템이 없습니다")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 각 아이템 검증
        for i, item in enumerate(order.items):
            item_result = OrderValidator.validate_order_item(item)
            if not item_result.is_valid:
                errors.extend([f"아이템 {i+1}: {err}" for err in item_result.errors])
            warnings.extend([f"아이템 {i+1}: {warn}" for warn in item_result.warnings])
        
        # 총 금액 검증
        if order.total_price <= 0:
            errors.append("총 금액이 0원 이하입니다")
        
        # 최대 금액 확인 (경고)
        if order.total_price > 100000:
            warnings.append(f"주문 금액이 매우 높습니다: {order.total_price:,}원")
        
        # 아이템 개수 확인 (경고)
        if order.item_count > 20:
            warnings.append(f"주문 아이템이 매우 많습니다: {order.item_count}개")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_order_item(item: OrderItem) -> ValidationResult:
        """
        주문 아이템 검증
        
        Args:
            item: 검증할 주문 아이템
            
        Returns:
            검증 결과
        """
        errors = []
        warnings = []
        
        # 메뉴 존재 확인
        menu = menu_db.get_menu_by_id(item.menu_id)
        if not menu:
            errors.append(f"메뉴 ID '{item.menu_id}'를 찾을 수 없습니다")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 재고 확인
        if not menu.available:
            errors.append(f"'{menu.name}'은(는) 현재 품절입니다")
        
        # 수량 검증
        if item.quantity < 1:
            errors.append("수량은 1 이상이어야 합니다")
        elif item.quantity > 10:
            warnings.append(f"수량이 많습니다: {item.quantity}개")
        
        # 가격 검증
        if item.price != menu.price:
            warnings.append(
                f"가격 불일치: 아이템 가격 {item.price}원, "
                f"메뉴 가격 {menu.price}원"
            )
        
        # 옵션 검증
        for option in item.options:
            if option not in menu.options:
                warnings.append(f"'{option}'은(는) 유효하지 않은 옵션입니다")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_menu_name(menu_name: str) -> ValidationResult:
        """
        메뉴 이름 검증
        
        Args:
            menu_name: 메뉴 이름
            
        Returns:
            검증 결과
        """
        errors = []
        warnings = []
        
        if not menu_name or not menu_name.strip():
            errors.append("메뉴 이름이 비어있습니다")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 메뉴 존재 확인
        menu = menu_db.get_menu_by_name(menu_name)
        if not menu:
            errors.append(f"'{menu_name}' 메뉴를 찾을 수 없습니다")
        elif not menu.available:
            errors.append(f"'{menu.name}'은(는) 현재 품절입니다")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_quantity(quantity: int) -> ValidationResult:
        """
        수량 검증
        
        Args:
            quantity: 수량
            
        Returns:
            검증 결과
        """
        errors = []
        warnings = []
        
        if quantity < 1:
            errors.append("수량은 1 이상이어야 합니다")
        elif quantity > 99:
            errors.append("수량은 99 이하여야 합니다")
        elif quantity > 10:
            warnings.append(f"수량이 많습니다: {quantity}개")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_user_input(user_input: str) -> ValidationResult:
        """
        사용자 입력 검증
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            검증 결과
        """
        errors = []
        warnings = []
        
        if not user_input or not user_input.strip():
            errors.append("입력이 비어있습니다")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 입력 길이 확인
        if len(user_input) > 500:
            warnings.append("입력이 너무 깁니다")
        
        # 위험한 문자 확인 (보안)
        dangerous_chars = ['<script>', 'javascript:', 'onerror=']
        for char in dangerous_chars:
            if char.lower() in user_input.lower():
                errors.append("허용되지 않는 문자가 포함되어 있습니다")
                break
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )


class InputSanitizer:
    """입력 정제 클래스"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        텍스트 정제
        
        Args:
            text: 원본 텍스트
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return ""
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 연속된 공백을 하나로
        text = " ".join(text.split())
        
        # 특수 문자 제거 (선택적)
        # 필요에 따라 추가 정제 로직 구현
        
        return text
    
    @staticmethod
    def extract_number(text: str) -> int:
        """
        텍스트에서 숫자 추출
        
        Args:
            text: 텍스트
            
        Returns:
            추출된 숫자 (없으면 1)
        """
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return 1
    
    @staticmethod
    def normalize_menu_name(name: str) -> str:
        """
        메뉴 이름 정규화
        
        Args:
            name: 메뉴 이름
            
        Returns:
            정규화된 메뉴 이름
        """
        # 공백 정제
        name = InputSanitizer.sanitize_text(name)
        
        # 일반적인 표현 통일
        replacements = {
            "햄버거": "버거",
            "감튀": "감자튀김",
            "콜": "콜라",
        }
        
        for old, new in replacements.items():
            if old in name:
                name = name.replace(old, new)
        
        return name