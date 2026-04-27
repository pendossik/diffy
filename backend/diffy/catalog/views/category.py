"""API для категорий - получение списка и создание."""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from catalog.services.category import CategoryService
from catalog.serializers import (
    CategoryListSerializer, CategoryCreateSerializer, CategoryUpdateSerializer, CategoryDetailSerializer
)
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

logger = logging.getLogger('catalog')

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


@extend_schema(
    tags=['Каталог - Категории'],
    summary='Получение списка категорий',
    description=(
        'Пагинированный список всех категорий с поддержкой поиска.\n\n'
        '**Доступ:** всем пользователям.'
    ),
    parameters=[
        OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Поисковая подстрока', required=False),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Номер страницы', required=False),
        OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Размер страницы', required=False),
    ],
    responses={200: CategoryListSerializer(many=True), 400: {'type': 'object'}, 500: {'type': 'object'}},
    operation_id='catalog_categories_list',
)
@extend_schema(
    tags=['Каталог - Категории'],
    summary='Создание новой категории',
    description=(
        'Создать новую категорию.\n\n'
        '**Требования:** Только для администраторов.'
    ),
    request=CategoryCreateSerializer,
    responses={
        201: CategoryDetailSerializer,
        400: {'type': 'object'},
        401: {'type': 'object'},
        403: {'type': 'object'},
        409: {'type': 'object'},
    },
    operation_id='catalog_categories_create',
)
class CategoryView(APIView):
    """Получение списка и создание категорий."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get('search')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        try:
            service = CategoryService()
            categories = service.get_list(search=search, page=page, page_size=page_size)
            return Response(CategoryListSerializer(categories, many=True).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка получения категорий: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CategoryService()
            category = service.create(user=request.user, name=serializer.validated_data['name'])
            return Response(CategoryDetailSerializer(category).data, status=status.HTTP_201_CREATED)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            logger.error(f"Ошибка создания категории: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Каталог - Категории'],
    summary='Получение категории',
    responses={200: CategoryDetailSerializer, 404: {'type': 'object'}},
    operation_id='catalog_categories_retrieve',
)
@extend_schema(
    tags=['Каталог - Категории'],
    summary='Обновление категории',
    request=CategoryCreateSerializer,
    responses={200: CategoryDetailSerializer, 400: {}, 403: {}, 404: {}, 409: {}},
    operation_id='catalog_categories_update',
)
@extend_schema(
    tags=['Каталог - Категории'],
    summary='Удаление категории',
    responses={200: {}, 403: {}, 404: {}},
    operation_id='catalog_categories_destroy',
)
class CategoryDetailView(APIView):
    """Получение, обновление и удаление категории."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        try:
            service = CategoryService()
            return Response(CategoryDetailSerializer(service.get_by_id(id)).data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка получения категории {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: int):
        serializer = CategoryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CategoryService()
            name = serializer.validated_data.get('name')
            category = service.update(user=request.user, category_id=id, name=name)
            return Response(CategoryDetailSerializer(category).data, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка обновления категории {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id: int):
        try:
            service = CategoryService()
            service.delete(user=request.user, category_id=id)
            return Response({'message': 'Категория удалена'}, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка удаления категории {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)