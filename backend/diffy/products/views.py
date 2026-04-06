"""API-представления приложения products."""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
import logging
from .services import ProductService
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductUpdateSerializer,
    ProductSearchSerializer
)

logger = logging.getLogger('products')


class ProductPagination(PageNumberPagination):
    """Настройки пагинации для товаров."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


@extend_schema_view(
    get=extend_schema(
        tags=['Товары'],
        summary='Получение списка товаров',
        description=(
            'Пагинированный список всех товаров с поддержкой поиска и фильтрации по категории.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор товара\n'
            '- `name` — название на текущем языке запроса\n'
            '- `name_ru` — название на русском языке\n'
            '- `name_en` — название на английском языке\n'
            '- `category` — ID категории\n'
            '- `category_info` — информация о категории\n'
            '- `img` — путь к изображению\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример использования:**\n'
            '```\n'
            'GET /api/products/?search=ноутбук&category=1&page=1&page_size=20\n'
            '```\n\n'
            '**Поиск:** регистронезависимый поиск по полям `name_ru` и `name_en`.'
        ),
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Поисковая подстрока (мин. 2 символа)',
                required=False,
                examples=[
                    OpenApiExample('Поиск ноутбуков', value='ноутбук'),
                    OpenApiExample('Поиск телефонов', value='телефон'),
                ]
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID категории для фильтрации',
                required=False,
                examples=[OpenApiExample('ID категории', value=1)],
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Номер страницы (по умолчанию: 1)',
                required=False,
                examples=[OpenApiExample('Первая страница', value=1)]
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Количество элементов на странице (20–100, по умолчанию: 20)',
                required=False,
                examples=[
                    OpenApiExample('По умолчанию', value=20),
                    OpenApiExample('Максимум', value=100),
                ]
            ),
        ],
        responses={
            200: ProductListSerializer(many=True),
        },
        operation_id='products_list',
    ),
    post=extend_schema(
        tags=['Товары'],
        summary='Создание нового товара',
        description=(
            'Создать новый товар с указанным названием в категории.\n\n'
            '**Требования:**\n'
            '- Только для администраторов (`role: admin` или `superuser`)\n'
            '- Название должно быть уникальным в рамках категории (регистронезависимая проверка)\n'
            '- Поддерживает мультиязычность: можно указать `name_ru` и/или `name_en`\n'
            '- Категория должна существовать\n\n'
            '**Правила:**\n'
            '- Если `name_ru`/`name_en` не указаны, используется значение из `name`\n'
            '- Изображение должно начинаться с `products/`\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/products/\n'
            '{\n'
            '  "name": "Ноутбук Dell XPS 15",\n'
            '  "name_ru": "Ноутбук Dell XPS 15",\n'
            '  "name_en": "Dell XPS 15 Laptop",\n'
            '  "category": 1,\n'
            '  "img": "products/dell-xps-15.jpg"\n'
            '}\n'
            '```'
        ),
        request=ProductCreateSerializer,
        responses={
            201: ProductDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут создавать товары'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар с таким именем уже существует в этой категории'}}},
        },
        examples=[
            OpenApiExample(
                'Базовое создание',
                value={
                    'name': 'Ноутбук Dell XPS 15',
                    'name_ru': 'Ноутбук Dell XPS 15',
                    'name_en': 'Dell XPS 15 Laptop',
                    'category': 1,
                    'img': 'products/dell-xps-15.jpg'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Создание без изображения',
                value={
                    'name': 'Смартфон iPhone 15',
                    'name_ru': 'Смартфон iPhone 15',
                    'name_en': 'iPhone 15 Smartphone',
                    'category': 2
                },
                request_only=True,
            ),
            OpenApiExample(
                'Успешное создание',
                value={
                    'id': 42,
                    'name': 'Ноутбук Dell XPS 15',
                    'name_ru': 'Ноутбук Dell XPS 15',
                    'name_en': 'Dell XPS 15 Laptop',
                    'category': 1,
                    'category_info': {
                        'id': 1,
                        'name': 'Электроника',
                        'name_ru': 'Электроника',
                        'name_en': 'Electronics'
                    },
                    'img': 'products/dell-xps-15.jpg'
                },
            ),
        ],
        operation_id='products_create',
    ),
)
class ProductListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком товаров.

    **GET** — получение списка товаров с поиском, фильтрацией и пагинацией (доступно всем).
    **POST** — создание нового товара (только для администраторов).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    pagination_class = ProductPagination

    def get(self, request):
        """Получить список товаров с опциональным поиском и фильтрацией."""
        search_serializer = ProductSearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            return Response(
                {'error': 'Неверный формат поискового запроса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        search = search_serializer.validated_data.get('search')
        category_id = search_serializer.validated_data.get('category')

        try:
            products = ProductService.get_products_list(
                search=search,
                category_id=category_id
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Создать новый товар."""
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                category_id = serializer.validated_data['category'].id
                product = ProductService.create_product(
                    user=request.user,
                    name=serializer.validated_data['name'],
                    category_id=category_id,
                    img=serializer.validated_data.get('img'),
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en')
                )
                logger.info(f"Товар создан: '{product.name}' (пользователь: {request.user.email})")
                from django.urls import reverse
                headers = {'Location': reverse('product-detail', args=[product.pk])}
                return Response(
                    ProductDetailSerializer(product).data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            except PermissionError as e:
                logger.warning(f"Попытка создания товара без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Товары'],
        summary='Получение детальной информации о товаре',
        description=(
            'Получить полную информацию о товаре по его идентификатору.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор\n'
            '- `name` — название на текущем языке запроса\n'
            '- `name_ru` — название на русском\n'
            '- `name_en` — название на английском\n'
            '- `category` — ID категории\n'
            '- `category_info` — информация о категории\n'
            '- `img` — путь к изображению\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/products/42/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=42)],
            ),
        ],
        responses={
            200: ProductDetailSerializer,
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар не найден'}}},
        },
        operation_id='products_retrieve',
    ),
    put=extend_schema(
        tags=['Товары'],
        summary='Полное обновление товара',
        description=(
            'Полностью обновить данные товара (все поля обязательны).\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n'
            '- Новое название должно быть уникальным в рамках категории\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PUT /api/products/42/\n'
            '{\n'
            '  "name": "Ноутбук Dell XPS 17",\n'
            '  "name_ru": "Ноутбук Dell XPS 17",\n'
            '  "name_en": "Dell XPS 17 Laptop",\n'
            '  "category": 1,\n'
            '  "img": "products/dell-xps-17.jpg"\n'
            '}\n'
            '```'
        ),
        request=ProductUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=42)],
            ),
        ],
        responses={
            200: ProductDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять товары'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар не найден'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар с таким именем уже существует в этой категории'}}},
        },
        examples=[
            OpenApiExample(
                'Полное обновление',
                value={
                    'name': 'Ноутбук Dell XPS 17',
                    'name_ru': 'Ноутбук Dell XPS 17',
                    'name_en': 'Dell XPS 17 Laptop',
                    'category': 1,
                    'img': 'products/dell-xps-17.jpg'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Результат обновления',
                value={
                    'id': 42,
                    'name': 'Ноутбук Dell XPS 17',
                    'name_ru': 'Ноутбук Dell XPS 17',
                    'name_en': 'Dell XPS 17 Laptop',
                    'category': 1,
                    'category_info': {
                        'id': 1,
                        'name': 'Электроника',
                        'name_ru': 'Электроника',
                        'name_en': 'Electronics'
                    },
                    'img': 'products/dell-xps-17.jpg'
                },
            ),
        ],
        operation_id='products_update',
    ),
    patch=extend_schema(
        tags=['Товары'],
        summary='Частичное обновление товара',
        description=(
            'Частично обновить данные товара (только указанные поля).\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PATCH /api/products/42/\n'
            '{\n'
            '  "name_en": "Dell XPS 15 Updated",\n'
            '  "img": "products/dell-xps-15-new.jpg"\n'
            '}\n'
            '```'
        ),
        request=ProductUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=42)],
            ),
        ],
        responses={
            200: ProductDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять товары'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар не найден'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар с таким именем уже существует в этой категории'}}},
        },
        examples=[
            OpenApiExample(
                'Частичное обновление (только изображение)',
                value={'img': 'products/new-image.jpg'},
                request_only=True,
            ),
            OpenApiExample(
                'Частичное обновление (название и изображение)',
                value={
                    'name': 'Обновлённый товар',
                    'name_ru': 'Обновлённый товар',
                    'name_en': 'Updated Product',
                    'img': 'products/new-image.jpg'
                },
                request_only=True,
            ),
        ],
        operation_id='products_partial_update',
    ),
    delete=extend_schema(
        tags=['Товары'],
        summary='Удаление товара',
        description=(
            'Безвозвратно удалить товар по идентификатору.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Внимание:** операция необратима!\n\n'
            '**Пример:**\n'
            '```\n'
            'DELETE /api/products/42/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=42)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Товар успешно удален'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут удалять товары'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар не найден'}}},
        },
        operation_id='products_destroy',
    ),
)
class ProductDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельным товаром.

    **GET** — получение детальной информации (доступно всем).
    **PUT** — полное обновление (все поля обязательны, только администраторы).
    **PATCH** — частичное обновление (только указанные поля, только администраторы).
    **DELETE** — удаление товара (только администраторы).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        """Получить детальную информацию о товаре."""
        try:
            product = ProductService.get_product_detail(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _handle_update(self, request, id: int):
        """Внутренний метод для обработки PUT/PATCH запросов."""
        try:
            product = ProductService.get_product_detail(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductUpdateSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            try:
                category_id = serializer.validated_data.get('category')
                # category_id теперь int или None (не объект Category)

                product = ProductService.update_product(
                    user=request.user,
                    product_id=id,
                    name=serializer.validated_data.get('name'),
                    category_id=category_id,
                    img=serializer.validated_data.get('img'),
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en')
                )
                logger.info(f"Товар обновлен: ID={id}, '{product.name}' (пользователь: {request.user.email})")
                return Response(
                    ProductDetailSerializer(product).data,
                    status=status.HTTP_200_OK
                )
            except PermissionError as e:
                logger.warning(f"Попытка изменения товара без прав: {request.user.email}")
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, id: int):
        """Полное обновление товара."""
        return self._handle_update(request, id)

    def patch(self, request, id: int):
        """Частичное обновление товара."""
        return self._handle_update(request, id)

    def delete(self, request, id: int):
        """Удалить товар."""
        try:
            ProductService.delete_product(
                user=request.user,
                product_id=id
            )
            logger.info(f"Товар удален: ID={id} (пользователь: {request.user.email})")
            return Response(
                {'message': 'Товар успешно удален'},
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка удаления товара без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
