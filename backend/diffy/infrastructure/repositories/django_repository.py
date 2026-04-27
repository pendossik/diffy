from typing import Any, List, Optional
from django.db.models import Q

from infrastructure.repositories.repository import AbstractRepository


class PaginatedResult:
    def __init__(self, items: List[Any], total: int, page: int, page_size: int):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = (total + page_size - 1) // page_size

    def to_dict(self) -> dict:
        return {
            'items': self.items,
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
        }


    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


class DjangoRepository(AbstractRepository):
    default_ordering = 'name'
    select_related = []
    prefetch_related = []
    search_fields = ['name']

    def get_queryset(self):
        queryset = self.model.objects.all()

        if self.select_related:
            queryset = queryset.select_related(*self.select_related)
        if self.prefetch_related:
            queryset = queryset.prefetch_related(*self.prefetch_related)

        return queryset

    def _apply_filters(self, queryset, search: Optional[str] = None, **filters):
        for key, value in filters.items():
            if value is not None:
                queryset = queryset.filter(**{key: value})

        if search and search.strip():
            queryset = queryset.filter(self._build_search_filter(search))

        ordering = self.default_ordering
        if isinstance(ordering, (list, tuple)):
            return queryset.order_by(*ordering)
        return queryset.order_by(ordering)

    def _to_dict(self, obj) -> dict:
        result = {}
        for field in obj._meta.fields:
            name = field.name
            value = getattr(obj, name)
            if hasattr(field, 'remote_field') and field.remote_field:
                fk_id_name = f'{name}_id'
                if hasattr(obj, fk_id_name):
                    result[fk_id_name] = getattr(obj, fk_id_name)
            result[name] = value
        return result

    def _build_search_filter(self, search: str) -> Q:
        if not search or not self.search_fields:
            return Q()
        
        search = search.strip()
        q = Q()
        for field in self.search_fields:
            q |= Q(**{f'{field}__icontains': search})
        return q

    def get_all(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **filters
    ) -> List[dict]:
        queryset = self._apply_filters(self.get_queryset(), search, **filters)
        offset = (page - 1) * page_size
        items = [self._to_dict(obj) for obj in queryset[offset:offset + page_size]]
        return items

    def get_all_paginated(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        **filters
    ) -> PaginatedResult:
        base_queryset = self._apply_filters(self.get_queryset(), search, **filters)
        total = base_queryset.count()
        
        offset = (page - 1) * page_size
        items = [self._to_dict(obj) for obj in base_queryset[offset:offset + page_size]]

        return PaginatedResult(items, total, page, page_size)

    def list(self, search: Optional[str] = None, **filters) -> List[dict]:
        return self.get_all(search=search, **filters)

    def get_by_id(self, id: int) -> dict:
        from infrastructure.exceptions import ObjectNotFoundError
        try:
            obj = self.get_queryset().get(pk=id)
            return self._to_dict(obj)
        except self.model.DoesNotExist:
            raise ObjectNotFoundError(self.model.__name__, id)

    def create(self, **kwargs) -> dict:
        obj = self.model.objects.create(**kwargs)
        return self._to_dict(obj)

    def update(self, id: int, **kwargs) -> dict:
        from infrastructure.exceptions import ObjectNotFoundError
        obj = self.get_queryset().get(pk=id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        obj.save()
        return self._to_dict(obj)

    def delete(self, id: int) -> bool:
        from infrastructure.exceptions import ObjectNotFoundError
        obj = self.get_queryset().get(pk=id)
        obj.delete()
        return True