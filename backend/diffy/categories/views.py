"""API-представления приложения categories."""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
import logging
from .services import CategoryService
from .serializers import (
    CategoryListSerializer, CategoryDetailSerializer,
    CategoryCreateSerializer, CategoryUpdateSerializer,
    CategorySearchSerializer
)

logger = logging.getLogger('categories')


class CategoryPagination(PageNumberPagination):
    """Настройки пагинации для категорий."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


@extend_schema_view(
    get=extend_schema(
        tags=['Категории'],
        summary='Получение списка категорий',
        description=(
            'Пагинированный список всех категорий с поддержкой поиска.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор категории\n'
            '- `name` — название на текущем языке запроса (определяется заголовком `Accept-Language`)\n'
            '- `name_ru` — название на русском языке\n'
            '- `name_en` — название на английском языке\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример использования:**\n'
            '```\n'
            'GET /api/categories/?search=тех&page=1&page_size=20\n'
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
                    OpenApiExample('Поиск технологий', value='тех'),
                    OpenApiExample('Поиск дизайна', value='дизайн'),
                ]
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
            200: CategoryListSerializer(many=True),
        },
        operation_id='categories_list',
    ),
    post=extend_schema(
        tags=['Категории'],
        summary='Создание новой категории',
        description=(
            'Создать новую категорию с указанным названием.\n\n'
            '**Требования:**\n'
            '- Только для администраторов (`role: admin` или `superuser`)\n'
            '- Название должно быть уникальным (регистронезависимая проверка)\n'
            '- Поддерживает мультиязычность: можно указать `name_ru` и/или `name_en`\n\n'
            '**Правила:**\n'
            '- Если `name_ru`/`name_en` не указаны, используется значение из `name`\n'
            '- Название автоматически приводится к формату с заглавной буквы\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/categories/\n'
            '{\n'
            '  "name": "Веб-разработка",\n'
            '  "name_ru": "Веб-разработка",\n'
            '  "name_en": "Web Development"\n'
            '}\n'
            '```'
        ),
        request=CategoryCreateSerializer,
        responses={
            201: CategoryDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут создавать категории'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория с таким именем уже существует'}}},
        },
        examples=[
            OpenApiExample(
                'Базовое создание',
                value={'name': 'Веб-разработка'},
                request_only=True,
            ),
            OpenApiExample(
                'Создание с переводами',
                value={
                    'name': 'Веб-разработка',
                    'name_ru': 'Веб-разработка',
                    'name_en': 'Web Development'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Успешное создание',
                value={
                    'id': 42,
                    'name': 'Веб-разработка',
                    'name_ru': 'Веб-разработка',
                    'name_en': 'Web Development'
                },
            ),
        ],
        operation_id='categories_create',
    ),
)
class CategoryListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком категорий.

    **GET** — получение списка категорий с поиском и пагинацией (доступно всем).
    **POST** — создание новой категории (только для администраторов).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    pagination_class = CategoryPagination

    def get(self, request):
        """Получить список категорий с опциональным поиском."""
        search_serializer = CategorySearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            # HIGH #4: Не раскрывать детали валидации
            return Response(
                {'error': 'Неверный формат поискового запроса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        search = search_serializer.validated_data.get('search')

        try:
            categories = CategoryService.get_categories_list(search)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategoryListSerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Создать новую категорию."""
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                category = CategoryService.create_category(
                    user=request.user,
                    name=serializer.validated_data['name']
                )
                logger.info(f"Категория создана: '{category.name}' (пользователь: {request.user.email})")
                # MEDIUM #2: Добавить заголовок Location
                from django.urls import reverse
                headers = {'Location': reverse('category-detail', args=[category.pk])}
                return Response(
                    CategoryDetailSerializer(category).data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            except PermissionError as e:
                logger.warning(f"Попытка создания категории без прав: {request.user.email}")
                # MEDIUM #1: Унифицированный формат ошибок
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                # HIGH #3: 409 Conflict для дубликатов
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        # MEDIUM #1: Унифицированный формат ошибок валидации
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Категории'],
        summary='Получение детальной информации о категории',
        description=(
            'Получить полную информацию о категории по её идентификатору.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор\n'
            '- `name` — название на текущем языке запроса\n'
            '- `name_ru` — название на русском\n'
            '- `name_en` — название на английском\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/categories/42/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=42)],
            ),
        ],
        responses={
            200: CategoryDetailSerializer,
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
        },
        operation_id='categories_retrieve',
    ),
    put=extend_schema(
        tags=['Категории'],
        summary='Полное обновление категории',
        description=(
            'Полностью обновить данные категории (все поля обязательны).\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n'
            '- Новое название должно быть уникальным\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PUT /api/categories/42/\n'
            '{\n'
            '  "name": "Мобильная разработка",\n'
            '  "name_ru": "Мобильная разработка",\n'
            '  "name_en": "Mobile Development"\n'
            '}\n'
            '```'
        ),
        request=CategoryUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=42)],
            ),
        ],
        responses={
            200: CategoryDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять категории'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория с таким именем уже существует'}}},
        },
        examples=[
            OpenApiExample(
                'Полное обновление',
                value={
                    'name': 'Мобильная разработка',
                    'name_ru': 'Мобильная разработка',
                    'name_en': 'Mobile Development'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Результат обновления',
                value={
                    'id': 42,
                    'name': 'Мобильная разработка',
                    'name_ru': 'Мобильная разработка',
                    'name_en': 'Mobile Development'
                },
            ),
        ],
        operation_id='categories_update',
    ),
    patch=extend_schema(
        tags=['Категории'],
        summary='Частичное обновление категории',
        description=(
            'Частично обновить данные категории (только указанные поля).\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PATCH /api/categories/42/\n'
            '{\n'
            '  "name_en": "Mobile Apps"\n'
            '}\n'
            '```'
        ),
        request=CategoryUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=42)],
            ),
        ],
        responses={
            200: CategoryDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять категории'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория с таким именем уже существует'}}},
        },
        examples=[
            OpenApiExample(
                'Частичное обновление (только английский перевод)',
                value={'name_en': 'Mobile Apps'},
                request_only=True,
            ),
        ],
        operation_id='categories_partial_update',
    ),
    delete=extend_schema(
        tags=['Категории'],
        summary='Удаление категории',
        description=(
            'Безвозвратно удалить категорию по идентификатору.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Внимание:** операция необратима!\n\n'
            '**Пример:**\n'
            '```\n'
            'DELETE /api/categories/42/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=42)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Категория успешно удалена'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут удалять категории'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
        },
        operation_id='categories_destroy',
    ),
)
class CategoryDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельной категорией.

    **GET** — получение детальной информации (доступно всем).
    **PUT** — полное обновление (все поля обязательны, только администраторы).
    **PATCH** — частичное обновление (только указанные поля, только администраторы).
    **DELETE** — удаление категории (только администраторы).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        """Получить детальную информацию о категории."""
        try:
            category = CategoryService.get_category_detail(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _handle_update(self, request, id: int):
        """Внутренний метод для обработки PUT/PATCH запросов."""
        try:
            category = CategoryService.get_category_detail(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoryUpdateSerializer(instance=category, data=request.data)
        if serializer.is_valid():
            try:
                category = CategoryService.update_category(
                    user=request.user,
                    category_id=id,
                    name=serializer.validated_data['name']
                )
                logger.info(f"Категория обновлена: ID={id}, '{category.name}' (пользователь: {request.user.email})")
                return Response(
                    CategoryDetailSerializer(category).data,
                    status=status.HTTP_200_OK
                )
            except PermissionError as e:
                logger.warning(f"Попытка изменения категории без прав: {request.user.email}")
                # MEDIUM #1: Унифицированный формат ошибок
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                # HIGH #3: 409 Conflict для дубликатов
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        # MEDIUM #1: Унифицированный формат ошибок валидации
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, id: int):
        """Полное обновление категории."""
        return self._handle_update(request, id)

    def patch(self, request, id: int):
        """Частичное обновление категории."""
        return self._handle_update(request, id)

    def delete(self, request, id: int):
        """Удалить категорию."""
        try:
            CategoryService.delete_category(
                user=request.user,
                category_id=id
            )
            logger.info(f"Категория удалена: ID={id} (пользователь: {request.user.email})")
            return Response(
                {'message': 'Категория успешно удалена'},
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка удаления категории без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
