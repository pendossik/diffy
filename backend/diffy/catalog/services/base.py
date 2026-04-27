from abc import ABC
from typing import Any, Optional, Type
from catalog.services.exceptions import PermissionDeniedError


REPOSITORY_MAP = {}


def register_repository(model_name: str, repository_class: Type):
    REPOSITORY_MAP[model_name] = repository_class


class BaseService:
    _repository_class: Optional[Type] = None
    
    def __init__(self, repository: Any = None):
        self._repository = repository

    @property
    def repository(self) -> Any:
        if self._repository is None:
            if self._repository_class is not None:
                self._repository = self._repository_class()
            else:
                raise RuntimeError(f"Repository not set for {self.__class__.__name__}")
        return self._repository

    @staticmethod
    def _is_admin(user) -> bool:
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        return bool(
            getattr(user, 'role', None) in ('admin', 'superuser') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )

    def _check_admin(self, user, action: str = "perform this action"):
        if not self._is_admin(user):
            raise PermissionDeniedError(f"Only administrators can {action}")