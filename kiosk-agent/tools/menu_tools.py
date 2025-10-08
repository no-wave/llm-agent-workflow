# -*- coding: utf-8 -*-
"""
메뉴 관련 도구 모듈
메뉴 조회 및 검색 기능을 제공합니다.
"""
from typing import List, Dict, Any, Optional
from models.menu import menu_db
from models.schemas import MenuItem, MenuCategory


class MenuTools:
    """메뉴 관련 도구 클래스"""
    
    @staticmethod
    def get_menu_info(menu_name: str) -> Dict[str, Any]:
        """
        메뉴 정보 조회
        
        Args:
            menu_name: 메뉴 이름
            
        Returns:
            메뉴 정보 딕셔너리
        """
        menu = menu_db.get_menu_by_name(menu_name)
        if menu:
            return {
                "success": True,
                "menu": menu.dict(),
                "message": f"{menu.name}를 찾았습니다."
            }
        return {
            "success": False,
            "menu": None,
            "message": f"{menu_name}를 찾을 수 없습니다."
        }
    
    @staticmethod
    def get_all_menus() -> Dict[str, Any]:
        """
        전체 메뉴 조회
        
        Returns:
            전체 메뉴 리스트
        """
        menus = menu_db.get_available_menus()
        return {
            "success": True,
            "menus": [menu.dict() for menu in menus],
            "count": len(menus),
            "message": f"총 {len(menus)}개의 메뉴가 있습니다."
        }
    
    @staticmethod
    def get_menus_by_category(category: str) -> Dict[str, Any]:
        """
        카테고리별 메뉴 조회
        
        Args:
            category: 카테고리 이름 (burger, side, drink, dessert)
            
        Returns:
            카테고리별 메뉴 리스트
        """
        try:
            menu_category = MenuCategory(category.lower())
            menus = menu_db.get_menus_by_category(menu_category)
            
            category_names = {
                MenuCategory.BURGER: "버거",
                MenuCategory.SIDE: "사이드",
                MenuCategory.DRINK: "음료",
                MenuCategory.DESSERT: "디저트"
            }
            
            return {
                "success": True,
                "menus": [menu.dict() for menu in menus],
                "count": len(menus),
                "message": f"{category_names.get(menu_category)} 카테고리에 {len(menus)}개의 메뉴가 있습니다."
            }
        except ValueError:
            return {
                "success": False,
                "menus": [],
                "count": 0,
                "message": f"'{category}'는 유효하지 않은 카테고리입니다."
            }
    
    @staticmethod
    def search_menus(keyword: str) -> Dict[str, Any]:
        """
        키워드로 메뉴 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            검색 결과
        """
        menus = menu_db.search_menus(keyword)
        return {
            "success": True,
            "menus": [menu.dict() for menu in menus],
            "count": len(menus),
            "message": f"'{keyword}'로 {len(menus)}개의 메뉴를 찾았습니다."
        }
    
    @staticmethod
    def check_menu_availability(menu_id: str) -> Dict[str, Any]:
        """
        메뉴 재고 확인
        
        Args:
            menu_id: 메뉴 ID
            
        Returns:
            재고 여부
        """
        menu = menu_db.get_menu_by_id(menu_id)
        if menu:
            return {
                "success": True,
                "available": menu.available,
                "message": f"{menu.name}는 {'주문 가능' if menu.available else '품절'}입니다."
            }
        return {
            "success": False,
            "available": False,
            "message": "메뉴를 찾을 수 없습니다."
        }
    
    @staticmethod
    def get_menu_options(menu_id: str) -> Dict[str, Any]:
        """
        메뉴 옵션 조회
        
        Args:
            menu_id: 메뉴 ID
            
        Returns:
            메뉴 옵션 리스트
        """
        menu = menu_db.get_menu_by_id(menu_id)
        if menu:
            return {
                "success": True,
                "options": menu.options,
                "message": f"{menu.name}의 옵션: {', '.join(menu.options) if menu.options else '없음'}"
            }
        return {
            "success": False,
            "options": [],
            "message": "메뉴를 찾을 수 없습니다."
        }
    
    @staticmethod
    def format_menu_list(menus: List[MenuItem]) -> str:
        """
        메뉴 리스트를 보기 좋게 포맷팅
        
        Args:
            menus: 메뉴 리스트
            
        Returns:
            포맷팅된 메뉴 문자열
        """
        if not menus:
            return "메뉴가 없습니다."
        
        result = []
        for menu in menus:
            result.append(f"- {menu.name}: {menu.price:,}원")
            result.append(f"  {menu.description}")
            if menu.options:
                result.append(f"  옵션: {', '.join(menu.options)}")
        
        return "\n".join(result)


# 도구 함수 매핑 (OpenAI Function Calling용)
MENU_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_menu_info",
            "description": "특정 메뉴의 상세 정보를 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_name": {
                        "type": "string",
                        "description": "조회할 메뉴 이름"
                    }
                },
                "required": ["menu_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_menus",
            "description": "전체 메뉴 리스트를 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_menus_by_category",
            "description": "카테고리별 메뉴를 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["burger", "side", "drink", "dessert"],
                        "description": "메뉴 카테고리 (burger: 버거, side: 사이드, drink: 음료, dessert: 디저트)"
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_menus",
            "description": "키워드로 메뉴를 검색합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "검색할 키워드"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]