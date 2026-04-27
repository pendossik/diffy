from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AbstractRepository(ABC):
    model: Any = None

    @abstractmethod
    def get_all(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **filters
    ) -> List[dict]:
        pass

    @abstractmethod
    def get_all_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **filters
    ) -> dict:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> dict:
        pass

    @abstractmethod
    def create(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def update(self, id: int, **kwargs) -> dict:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass