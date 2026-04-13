# View Patterns для REST API

## Назначение

Руководство по созданию view классов для CRUD операций с использованием Django REST Framework и drf-spectacular.

## Базовая структура view класса

### ListCreateView — список и создание

```python
@extend_schema_view(
    get=extend_schema(
        tags=['Название ресурса'],
        summary='Получение списка ресурсов',
        description='Описание эндпоинта с примерами использования.',
        parameters=[...],
        responses={200: Serializer(many=True)},
        operation_id='resource_list',
    ),
    post=extend_schema(
        tags=['Название ресурса'],
        summary='Создание ресурса',
        description='Описание эндпоинта создания.',
        request=CreateSerializer,
        responses={201: DetailSerializer},
        operation_id='resource_create',
    ),
)
class ResourceListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком ресурсов.
    
    **GET** — получение списка с пагинацией и фильтрами.
    **POST** — создание нового ресурса.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ResourcePagination

    def get(self, request):
        """Получить список ресурсов."""
        # Логика получения списка
        pass

    def post(self, request):
        """Создать новый ресурс."""
        # Логика создания
        pass
```

### DetailView — чтение, обновление, удаление

```python
@extend_schema_view(
    get=extend_schema(
        tags=['Название ресурса'],
        summary='Получение деталей ресурса',
        description='Описание эндпоинта.',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор ресурса',
                examples=[OpenApiExample('ID ресурса', value=42)],
            ),
        ],
        responses={200: DetailSerializer},
        operation_id='resource_retrieve',
    ),
    put=extend_schema(
        tags=['Название ресурса'],
        summary='Полное обновление ресурса',
        description='Описание эндпоинта.',
        request=UpdateSerializer,
        responses={200: DetailSerializer},
        operation_id='resource_update',
    ),
    patch=extend_schema(
        tags=['Название ресурса'],
        summary='Частичное обновление ресурса',
        description='Описание эндпоинта.',
        request=UpdateSerializer,
        responses={200: DetailSerializer},
        operation_id='resource_partial_update',
    ),
    delete=extend_schema(
        tags=['Название ресурса'],
        summary='Удаление ресурса',
        description='Описание эндпоинта.',
        responses={200: {'message': 'string'}},
        operation_id='resource_destroy',
    ),
)
class ResourceDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельным ресурсом.
    
    **GET** — получение детальной информации.
    **PUT** — полное обновление.
    **PATCH** — частичное обновление.
    **DELETE** — удаление.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        """Получить детальную информацию о ресурсе."""
        pass

    def _handle_update(self, request, pk: int):
        """Внутренний метод для обработки PUT/PATCH."""
        pass

    def put(self, request, pk: int):
        """Полное обновление ресурса."""
        return self._handle_update(request, pk)

    def patch(self, request, pk: int):
        """Частичное обновление ресурса."""
        return self._handle_update(request, pk)

    def delete(self, request, pk: int):
        """Удалить ресурс."""
        pass
```

## Компоненты @extend_schema

### tags

Группировка эндпоинтов в Swagger UI:

```python
tags=['Категории']  # Все эндпоинты с этим тегом будут в одной группе
```

### summary

Краткое описание (одна строка):

```python
summary='Получение списка категорий'
summary='Создание новой категории'
summary='Обновление категории по ID'
```

### description

Подробное описание с Markdown:

```python
description=(
    'Пагинированный список всех категорий с поддержкой поиска.\n\n'
    '**Возвращает:**\n'
    '- `id` — уникальный идентификатор\n'
    '- `name` — название на текущем языке\n\n'
    '**Доступ:** всем авторизованным пользователям.\n\n'
    '**Пример:**\n'
    '```\n'
    'GET /api/categories/?search=тех\n'
    '```'
)
```

### parameters

Параметры запроса (query, path, header):

```python
from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

parameters=[
    # Query параметр
    OpenApiParameter(
        name='search',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='Поисковая подстрока',
        required=False,
        examples=[
            OpenApiExample('Поиск технологий', value='тех'),
            OpenApiExample('Поиск дизайна', value='дизайн'),
        ]
    ),
    # Path параметр
    OpenApiParameter(
        name='pk',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.PATH,
        description='Уникальный идентификатор',
        examples=[OpenApiExample('ID ресурса', value=42)],
    ),
    # Pagination
    OpenApiParameter(
        name='page',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description='Номер страницы',
        required=False,
    ),
]
```

### responses

Схемы ответов:

```python
responses={
    200: CategoryListSerializer(many=True),
    201: CategoryDetailSerializer,
    400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
    401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
    403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Недостаточно прав'}}},
    404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ресурс не найден'}}},
}
```

### examples

Примеры запросов и ответов:

```python
examples=[
    OpenApiExample(
        'Базовое создание',
        value={'name': 'Веб-разработка'},
        request_only=True,  # Только для запроса
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
        # response_only=True для ответа
    ),
]
```

### operation_id

Уникальный идентификатор операции:

```python
operation_id='categories_list'       # GET /categories/
operation_id='categories_create'     # POST /categories/
operation_id='categories_retrieve'   # GET /categories/{pk}/
operation_id='categories_update'     # PUT /categories/{pk}/
operation_id='categories_partial_update'  # PATCH /categories/{pk}/
operation_id='categories_destroy'    # DELETE /categories/{pk}/
```

## Обработка ошибок

### Валидация данных

```python
def post(self, request):
    serializer = CategoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            category = CategoryService.create_category(
                user=request.user,
                name=serializer.validated_data['name']
            )
            return Response(
                CategoryDetailSerializer(category).data,
                status=status.HTTP_201_CREATED
            )
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Логирование

```python
logger = logging.getLogger('categories')

# В view методах:
logger.info(f"Категория создана: '{category.name}' (пользователь: {request.user.email})")
logger.warning(f"Попытка создания категории без прав: {request.user.email}")
```

## Пагинация

```python
class CategoryPagination(PageNumberPagination):
    """Настройки пагинации для категорий."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

# В view классе:
class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CategoryPagination

    def get(self, request):
        categories = Category.objects.all()
        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategoryListSerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)
```

## Поиск и фильтрация

```python
def get(self, request):
    # Валидация параметров
    search_serializer = CategorySearchSerializer(data=request.query_params)
    if not search_serializer.is_valid():
        return Response(
            {'error': 'Неверный формат запроса', 'details': search_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    search = search_serializer.validated_data.get('search')
    
    # Поиск через сервис
    categories = CategoryService.get_categories_list(search)
    
    # Пагинация
    paginator = self.pagination_class()
    paginated_categories = paginator.paginate_queryset(categories, request)
    serializer = CategoryListSerializer(paginated_categories, many=True)
    
    return paginator.get_paginated_response(serializer.data)
```

## Внутренние методы

Для обработки PUT/PATCH использовать внутренний метод:

```python
def _handle_update(self, request, pk: int):
    """Внутренний метод для обработки PUT/PATCH запросов."""
    try:
        category = CategoryService.get_category_detail(pk)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategoryUpdateSerializer(instance=category, data=request.data)
    if serializer.is_valid():
        try:
            category = CategoryService.update_category(
                user=request.user,
                category_id=pk,
                name=serializer.validated_data['name']
            )
            logger.info(f"Категория обновлена: ID={pk} (пользователь: {request.user.email})")
            return Response(
                CategoryDetailSerializer(category).data,
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка изменения без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def put(self, request, pk: int):
    """Полное обновление категории."""
    return self._handle_update(request, pk)

def patch(self, request, pk: int):
    """Частичное обновление категории."""
    return self._handle_update(request, pk)
```

## Поиск в файле

Искать в этом файле:
- "ListCreateView" — шаблон для списка и создания
- "DetailView" — шаблон для деталей/обновления/удаления
- "parameters" — примеры параметров
- "responses" — схемы ответов
- "examples" — примеры запросов
- "operation_id" — именование операций
- "pagination" — настройка пагинации
- "error handling" — обработка ошибок
