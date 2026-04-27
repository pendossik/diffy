"""API для товаров - получение списка и создание."""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from catalog.services.product import ProductService
from catalog.serializers import (
    ProductListSerializer, ProductCreateSerializer, ProductUpdateSerializer, ProductDetailSerializer
)
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

logger = logging.getLogger('catalog')

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


@extend_schema(
    tags=['Каталог - Товары'],
    summary='Получение списка товаров',
    description='Пагинированный список товаров с поиском и фильтрацией.',
    parameters=[
        OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Поиск', required=False),
        OpenApiParameter(name='category_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Фильтр по категории', required=False),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Страница', required=False),
        OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Размер страницы', required=False),
    ],
    responses={200: ProductListSerializer(many=True), 400: {}, 500: {}},
    operation_id='catalog_products_list',
)
@extend_schema(
    tags=['Каталог - Товары'],
    summary='Создание товара',
    description='Создать новый товар. Только для администраторов.',
    request=ProductCreateSerializer,
    responses={201: ProductDetailSerializer, 400: {}, 401: {}, 403: {}, 404: {}, 409: {}},
    operation_id='catalog_products_create',
)
class ProductView(APIView):
    """Получение списка и создание товаров."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get('search')
        category_id = request.query_params.get('category_id')
        if category_id:
            category_id = int(category_id)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        try:
            service = ProductService()
            products = service.get_list(search=search, category_id=category_id, page=page, page_size=page_size)
            return Response(ProductListSerializer(products, many=True).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка получения товаров: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = ProductService()
            product = service.create(
                user=request.user,
                name=serializer.validated_data['name'],
                category_id=serializer.validated_data['category_id'],
                img_url=serializer.validated_data.get('img_url')
            )
            return Response(ProductDetailSerializer(product).data, status=status.HTTP_201_CREATED)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка создания товара: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Каталог - Товары'],
    summary='Получение товара',
    responses={200: ProductDetailSerializer, 404: {}},
    operation_id='catalog_products_retrieve',
)
@extend_schema(
    tags=['Каталог - Товары'],
    summary='Обновление товара',
    request=ProductCreateSerializer,
    responses={200: ProductDetailSerializer, 400: {}, 403: {}, 404: {}, 409: {}},
    operation_id='catalog_products_update',
)
@extend_schema(
    tags=['Каталог - Товары'],
    summary='Удаление товара',
    responses={200: {}, 403: {}, 404: {}},
    operation_id='catalog_products_destroy',
)
class ProductDetailView(APIView):
    """Получение, обновление и удаление товара."""
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        try:
            service = ProductService()
            return Response(ProductDetailSerializer(service.get_by_id(id)).data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка получения товара {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: int):
        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = ProductService()
            product = service.update(
                user=request.user,
                product_id=id,
                name=serializer.validated_data.get('name'),
                category_id=serializer.validated_data.get('category_id'),
                img_url=serializer.validated_data.get('img_url')
            )
            return Response(ProductDetailSerializer(product).data, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка обновления товара {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id: int):
        try:
            service = ProductService()
            service.delete(user=request.user, product_id=id)
            return Response({'message': 'Товар удалён'}, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка удаления товара {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)