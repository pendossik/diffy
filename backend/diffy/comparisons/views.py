"""API-представления приложения comparisons."""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from .services import FavoriteComparisonService, ComparisonCharacteristicsService
from .serializers import (
    FavoriteComparisonListSerializer,
    FavoriteComparisonDetailSerializer,
    FavoriteComparisonCreateSerializer,
)

logger = logging.getLogger('comparisons')


@extend_schema_view(
    get=extend_schema(
        tags=['Избранные сравнения'],
        summary='Список избранных сравнений',
        description=(
            'Получить список всех избранных сравнений текущего пользователя.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор сравнения\n'
            '- `products_count` — количество товаров в сравнении\n'
            '- `products_preview` — превью первых 3 товаров\n'
            '- `created_at` — дата добавления в избранное\n\n'
            '**Доступ:** только авторизованным пользователям.'
        ),
        responses={
            200: FavoriteComparisonListSerializer(many=True),
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
        },
        operation_id='favorite_comparisons_list',
    ),
    post=extend_schema(
        tags=['Избранные сравнения'],
        summary='Добавить сравнение в избранное',
        description=(
            'Добавить набор товаров в избранные сравнения.\n\n'
            '**Требования:**\n'
            '- Минимум 2 товара для сравнения\n'
            '- Все товары должны существовать\n'
            '- Сравнение не должно быть уже в избранных (проверка по набору товаров)\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/comparisons/favorites/\n'
            '{\n'
            '  "product_ids": [1, 2, 3]\n'
            '}\n'
            '```'
        ),
        request=FavoriteComparisonCreateSerializer,
        responses={
            201: FavoriteComparisonDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Для сравнения необходимо минимум 2 товара'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Такое сравнение уже есть в избранных'}}},
        },
        examples=[
            OpenApiExample(
                'Добавление сравнения',
                value={'product_ids': [1, 2, 3]},
                request_only=True,
            ),
            OpenApiExample(
                'Успешное создание',
                value={
                    'id': 42,
                    'products': [
                        {'id': 1, 'name': 'Ноутбук Dell', 'name_ru': 'Ноутбук Dell', 'name_en': 'Dell Laptop'},
                        {'id': 2, 'name': 'Ноутбук HP', 'name_ru': 'Ноутбук HP', 'name_en': 'HP Laptop'},
                        {'id': 3, 'name': 'Ноутбук Lenovo', 'name_ru': 'Ноутбук Lenovo', 'name_en': 'Lenovo Laptop'},
                    ],
                    'products_count': 3,
                    'created_at': '2026-03-30T12:00:00Z'
                },
            ),
        ],
        operation_id='favorite_comparisons_create',
    ),
)
class FavoriteComparisonListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком избранных сравнений.

    **GET** — список избранных сравнений пользователя.
    **POST** — добавить сравнение в избранное.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить список избранных сравнений пользователя."""
        try:
            comparisons = FavoriteComparisonService.get_user_comparisons(request.user)
            serializer = FavoriteComparisonListSerializer(comparisons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Ошибка получения списка сравнений: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении списка сравнений'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Добавить сравнение в избранное."""
        serializer = FavoriteComparisonCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                comparison = FavoriteComparisonService.add_to_favorites(
                    user=request.user,
                    product_ids=serializer.validated_data['product_ids']
                )
                logger.info(f"Пользователь {request.user.email} добавил сравнение ID={comparison.id}")
                return Response(
                    FavoriteComparisonDetailSerializer(comparison).data,
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                # Проверяем тип ошибки для правильного кода ответа
                error_message = str(e)
                if 'уже есть в избранных' in error_message:
                    return Response(
                        {'error': error_message},
                        status=status.HTTP_409_CONFLICT
                    )
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Избранные сравнения'],
        summary='Детали избранного сравнения',
        description=(
            'Получить полную информацию об одном избранном сравнении.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор сравнения\n'
            '- `products` — полный список товаров в сравнении\n'
            '- `products_count` — количество товаров\n'
            '- `created_at` — дата добавления в избранное\n\n'
            '**Доступ:** только авторизованным пользователям (только свои сравнения).'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор сравнения',
                examples=[OpenApiExample('ID сравнения', value=42)],
            ),
        ],
        responses={
            200: FavoriteComparisonDetailSerializer,
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'У вас нет доступа к этому сравнению'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Сравнение не найдено'}}},
        },
        operation_id='favorite_comparisons_retrieve',
    ),
    delete=extend_schema(
        tags=['Избранные сравнения'],
        summary='Удалить сравнение из избранного',
        description=(
            'Удалить сравнение из избранных.\n\n'
            '**Требования:**\n'
            '- Сравнение должно существовать\n'
            '- Сравнение должно принадлежать пользователю\n\n'
            '**Внимание:** операция необратима!'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор сравнения',
                examples=[OpenApiExample('ID сравнения', value=42)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Сравнение удалено из избранного'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'У вас нет доступа к этому сравнению'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Сравнение не найдено'}}},
        },
        operation_id='favorite_comparisons_destroy',
    ),
)
class FavoriteComparisonDetailView(APIView):
    """
    REST API эндпоинт для работы с одним избранным сравнением.

    **GET** — детали сравнения.
    **DELETE** — удалить сравнение из избранного.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id: int):
        """Получить детали одного сравнения."""
        try:
            comparison = FavoriteComparisonService.get_comparison_detail(
                user=request.user,
                comparison_id=id
            )
            serializer = FavoriteComparisonDetailSerializer(comparison)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            error_message = str(e)
            if 'нет доступа' in error_message:
                return Response(
                    {'error': error_message},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {'error': error_message},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Ошибка получения деталей сравнения: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении деталей сравнения'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, id: int):
        """Удалить сравнение из избранного."""
        try:
            FavoriteComparisonService.remove_from_favorites(
                user=request.user,
                comparison_id=id
            )
            logger.info(f"Пользователь {request.user.email} удалил сравнение ID={id}")
            return Response(
                {'message': 'Сравнение удалено из избранного'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            error_message = str(e)
            if 'нет доступа' in error_message:
                return Response(
                    {'error': error_message},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {'error': error_message},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Ошибка удаления сравнения: {str(e)}")
            return Response(
                {'error': 'Ошибка при удалении сравнения'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Сравнение товаров'],
        summary='Сравнение товаров по характеристикам',
        description=(
            'Сравнить несколько товаров по их характеристикам.\n\n'
            '**Возвращает:**\n'
            '- `products_count` — количество товаров в сравнении\n'
            '- `products` — список товаров\n'
            '- `groups` — группы характеристик со значениями для каждого товара\n\n'
            '**Доступ:** всем пользователям.'
        ),
        parameters=[
            OpenApiParameter(
                name='product_ids',
                type={'type': 'array', 'items': {'type': 'integer'}},
                location=OpenApiParameter.QUERY,
                description='Список ID товаров для сравнения (минимум 2)',
                required=True,
                examples=[OpenApiExample('Сравнение 3 товаров', value=[1, 2, 3])],
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'products_count': {'type': 'integer', 'example': 3},
                    'products': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer', 'example': 1},
                                'product_name': {'type': 'string', 'example': 'Ноутбук Dell XPS 15'}
                            }
                        }
                    },
                    'groups': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'group_id': {'type': 'integer', 'example': 1},
                                'group_name': {'type': 'string', 'example': 'Основные'},
                                'group_name_ru': {'type': 'string', 'example': 'Основные'},
                                'group_name_en': {'type': 'string', 'example': 'Basic'},
                                'order': {'type': 'integer', 'example': 0},
                                'characteristics': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'template_id': {'type': 'integer', 'example': 1},
                                            'template_name': {'type': 'string', 'example': 'Процессор'},
                                            'template_name_ru': {'type': 'string', 'example': 'Процессор'},
                                            'template_name_en': {'type': 'string', 'example': 'Processor'},
                                            'values': {
                                                'type': 'object',
                                                'additionalProperties': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'value': {'type': 'string', 'example': 'Intel Core i7'},
                                                        'value_ru': {'type': 'string', 'example': 'Intel Core i7'},
                                                        'value_en': {'type': 'string', 'example': 'Intel Core i7'}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Для сравнения необходимо минимум 2 товара'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Один или несколько товаров не найдены'}}},
        },
        examples=[
            OpenApiExample(
                'Сравнение 3 товаров',
                value={
                    'products_count': 3,
                    'products': [
                        {'product_id': 1, 'product_name': 'Ноутбук Dell XPS 15'},
                        {'product_id': 2, 'product_name': 'Ноутбук HP Pavilion'},
                        {'product_id': 3, 'product_name': 'Ноутбук Lenovo ThinkPad'}
                    ],
                    'groups': [
                        {
                            'group_id': 1,
                            'group_name': 'Основные',
                            'group_name_ru': 'Основные',
                            'group_name_en': 'Basic',
                            'order': 0,
                            'characteristics': [
                                {
                                    'template_id': 1,
                                    'template_name': 'Процессор',
                                    'template_name_ru': 'Процессор',
                                    'template_name_en': 'Processor',
                                    'values': {
                                        '1': {'value': 'Intel Core i7-12700H', 'value_ru': 'Intel Core i7-12700H', 'value_en': 'Intel Core i7-12700H'},
                                        '2': {'value': 'AMD Ryzen 7 5800H', 'value_ru': 'AMD Ryzen 7 5800H', 'value_en': 'AMD Ryzen 7 5800H'},
                                        '3': {'value': 'Intel Core i5-12500H', 'value_ru': 'Intel Core i5-12500H', 'value_en': 'Intel Core i5-12500H'}
                                    }
                                },
                                {
                                    'template_id': 2,
                                    'template_name': 'Оперативная память',
                                    'template_name_ru': 'Оперативная память',
                                    'template_name_en': 'RAM',
                                    'values': {
                                        '1': {'value': '16 ГБ', 'value_ru': '16 ГБ', 'value_en': '16 GB'},
                                        '2': {'value': '16 ГБ', 'value_ru': '16 ГБ', 'value_en': '16 GB'},
                                        '3': {'value': '8 ГБ', 'value_ru': '8 ГБ', 'value_en': '8 GB'}
                                    }
                                }
                            ]
                        }
                    ]
                },
            ),
        ],
        operation_id='compare_products_characteristics',
    ),
)
class ComparisonCharacteristicsView(APIView):
    """
    REST API эндпоинт для сравнения товаров по характеристикам.

    **GET** — сравнение товаров по характеристикам.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Сравнить товары по характеристикам."""
        # Получаем все значения product_ids (Swagger передаёт как список)
        product_ids_param = request.query_params.getlist('product_ids')
        
        if not product_ids_param:
            # Пробуем получить как comma-separated list
            product_ids_str = request.query_params.get('product_ids')
            if product_ids_str:
                product_ids_param = product_ids_str.split(',')
            else:
                return Response(
                    {'error': 'Требуется параметр product_ids'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            product_ids = [int(x) for x in product_ids_param]
        except ValueError:
            return Response(
                {'error': 'Неверный формат product_ids (ожидаются целые числа)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comparison_data = ComparisonCharacteristicsService.compare_products_by_characteristics(
                product_ids=product_ids
            )
            return Response(comparison_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка сравнения товаров: {str(e)}")
            return Response(
                {'error': 'Ошибка при сравнении товаров'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
