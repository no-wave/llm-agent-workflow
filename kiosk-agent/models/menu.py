# -*- coding: utf-8 -*-
"""
메뉴 데이터 관리 모듈
햄버거 가게의 메뉴 정보를 관리합니다.
"""
from typing import List, Dict, Optional
from models.schemas import MenuItem, MenuCategory


class MenuDatabase:
    """메뉴 데이터베이스 클래스"""
    
    def __init__(self):
        """메뉴 데이터 초기화"""
        self.menus: Dict[str, MenuItem] = {}
        self._initialize_menus()
    
    def _initialize_menus(self):
        """초기 메뉴 데이터 설정"""
        menu_items = [
            # 버거 메뉴
            MenuItem(
                id="B001",
                name="클래식 버거",
                category=MenuCategory.BURGER,
                price=5900,
                description="신선한 소고기 패티와 채소가 들어간 클래식 버거",
                options=["치즈 추가", "베이컨 추가", "패티 추가"]
            ),
            MenuItem(
                id="B002",
                name="치즈 버거",
                category=MenuCategory.BURGER,
                price=6900,
                description="고소한 치즈가 듬뿍 들어간 치즈 버거",
                options=["베이컨 추가", "패티 추가", "치즈 추가"]
            ),
            MenuItem(
                id="B003",
                name="베이컨 버거",
                category=MenuCategory.BURGER,
                price=7900,
                description="바삭한 베이컨이 들어간 프리미엄 버거",
                options=["치즈 추가", "베이컨 추가", "패티 추가"]
            ),
            MenuItem(
                id="B004",
                name="더블 버거",
                category=MenuCategory.BURGER,
                price=8900,
                description="패티 2장이 들어간 푸짐한 버거",
                options=["치즈 추가", "베이컨 추가", "패티 추가"]
            ),
            
            # 사이드 메뉴
            MenuItem(
                id="S001",
                name="감자튀김",
                category=MenuCategory.SIDE,
                price=2500,
                description="바삭바삭한 황금 감자튀김",
                options=["사이즈 업그레이드"]
            ),
            MenuItem(
                id="S002",
                name="치즈스틱",
                category=MenuCategory.SIDE,
                price=3500,
                description="쫄깃한 모차렐라 치즈스틱",
                options=[]
            ),
            MenuItem(
                id="S003",
                name="어니언링",
                category=MenuCategory.SIDE,
                price=3000,
                description="바삭한 양파링",
                options=[]
            ),
            
            # 음료 메뉴
            MenuItem(
                id="D001",
                name="콜라",
                category=MenuCategory.DRINK,
                price=2000,
                description="시원한 콜라",
                options=["사이즈 업그레이드"]
            ),
            MenuItem(
                id="D002",
                name="사이다",
                category=MenuCategory.DRINK,
                price=2000,
                description="상큼한 사이다",
                options=["사이즈 업그레이드"]
            ),
            MenuItem(
                id="D003",
                name="아메리카노",
                category=MenuCategory.DRINK,
                price=2500,
                description="진한 아메리카노",
                options=["사이즈 업그레이드", "샷 추가"]
            ),
            
            # 디저트 메뉴
            MenuItem(
                id="DS001",
                name="아이스크림",
                category=MenuCategory.DESSERT,
                price=2000,
                description="부드러운 소프트 아이스크림",
                options=[]
            ),
            MenuItem(
                id="DS002",
                name="애플파이",
                category=MenuCategory.DESSERT,
                price=2500,
                description="따뜻한 애플파이",
                options=[]
            ),
        ]
        
        for item in menu_items:
            self.menus[item.id] = item
    
    def get_menu_by_id(self, menu_id: str) -> Optional[MenuItem]:
        """
        ID로 메뉴 조회
        
        Args:
            menu_id: 메뉴 ID
            
        Returns:
            MenuItem 또는 None
        """
        return self.menus.get(menu_id)
    
    def get_menu_by_name(self, name: str) -> Optional[MenuItem]:
        """
        이름으로 메뉴 조회 (부분 일치)
        
        Args:
            name: 메뉴 이름
            
        Returns:
            MenuItem 또는 None
        """
        name_lower = name.lower()
        for menu in self.menus.values():
            if name_lower in menu.name.lower():
                return menu
        return None
    
    def get_menus_by_category(self, category: MenuCategory) -> List[MenuItem]:
        """
        카테고리별 메뉴 조회
        
        Args:
            category: 메뉴 카테고리
            
        Returns:
            MenuItem 리스트
        """
        return [menu for menu in self.menus.values() if menu.category == category]
    
    def get_all_menus(self) -> List[MenuItem]:
        """
        전체 메뉴 조회
        
        Returns:
            MenuItem 리스트
        """
        return list(self.menus.values())
    
    def get_available_menus(self) -> List[MenuItem]:
        """
        재고가 있는 메뉴만 조회
        
        Returns:
            MenuItem 리스트
        """
        return [menu for menu in self.menus.values() if menu.available]
    
    def search_menus(self, keyword: str) -> List[MenuItem]:
        """
        키워드로 메뉴 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            MenuItem 리스트
        """
        keyword_lower = keyword.lower()
        results = []
        for menu in self.menus.values():
            if (keyword_lower in menu.name.lower() or 
                keyword_lower in menu.description.lower()):
                results.append(menu)
        return results


# 전역 메뉴 데이터베이스 인스턴스
menu_db = MenuDatabase()