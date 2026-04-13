# Swagger Документация с drf-spectacular

## Назначение

Полное руководство по документированию API с использованием drf-spectacular для генерации OpenAPI/Swagger схем.

## ⚠️ Важное правило: именование path параметров

**Используй только `id` вместо `pk` в документации OpenApiParameter!**

### Почему это важно:

Django автоматически создаёт параметр из URL паттерна. Если в `urls.py` указано:
```python
path('<int:id>/', ...)  # Django создаст параметр 'id'
```

А в документации ты укажешь:
```python
OpenApiParameter(name='pk', ...)  # ← БУДЕТ ДУБЛИРОВАНИЕ!
```

**Результат:** В Swagger UI будут два параметра — `id` и `pk`, что путает пользователей.

### ✅ Правильно:

```python
# urls.py
path('<int:id>/', CategoryDetailView.as_view(), name='category-detail')

# views.py
@extend_schema_view(
    get=extend_schema(
        ...
        parameters=[
            OpenApiParameter(
                name='id',  # ← Совпадает с URL паттерном
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=42)],
            ),
        ],
    ),
)
```

### ❌ Неправильно:

```python
# urls.py
path('<int:id>/', CategoryDetailView.as_view(), name='category-detail')

# views.py
@extend_schema_view(
    get=extend_schema(
        ...
        parameters=[
            OpenApiParameter(
                name='pk',  # ← БУДЕТ ДУБЛИРОВАНИЕ с 'id'!
                ...
            ),
        ],
    ),
)
```

**Запомни:** `pk` и `id` — это одно и то же. Используй `id` в документации для соответствия с URL паттерном.

## Базовое использование

### Импорт компонентов

```python
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
```

### @extend_schema_view vs @extend_schema

**@extend_schema_view** — для class-based views с несколькими методами:

```python
@extend_schema_view(
    get=extend_schema(...),
    post=extend_schema(...),
    put=extend_schema(...),
    patch=extend_schema(...),
    delete=extend_schema(...),
)
class CategoryView(APIView):
    ...
```

**@extend_schema** — для function-based views или отдельных методов:

```python
@extend_schema(
    tags=['Категории'],
    summary='Получение списка',
    responses={200: CategorySerializer(many=True)},
)
@api_view(['GET'])
def category_list(request):
    ...
```

## OpenApiTypes

Типы данных для параметров:

```python
from drf_spectacular.types import OpenApiTypes

OpenApiTypes.STR      # string
OpenApiTypes.INT      # integer
OpenApiTypes.NUMBER   # number (float)
OpenApiTypes.BOOL     # boolean
OpenApiTypes.DATETIME # date-time
OpenApiTypes.DATE     # date
OpenApiTypes.UUID     # uuid
OpenApiTypes.URI      # uri
OpenApiTypes.EMAIL    # email
OpenApiTypes.OBJECT   # object
OpenApiTypes.ANY      # any
```

## OpenApiParameter

### Расположение параметров

```python
OpenApiParameter(
    name='search',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,  # Query параметры (?search=...)
)

OpenApiParameter(
    name='pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,  # Path параметры (/api/{pk}/)
)

OpenApiParameter(
    name='Authorization',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,  # Заголовки
)
```

### Примеры параметров

```python
# Query параметр с примерами
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
)

# Path параметр
OpenApiParameter(
    name='pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Уникальный идентификатор категории',
    examples=[OpenApiExample('ID категории', value=42)],
)

# Pagination параметры
OpenApiParameter(
    name='page',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Номер страницы (по умолчанию: 1)',
    required=False,
    examples=[OpenApiExample('Первая страница', value=1)]
)

OpenApiParameter(
    name='page_size',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Элементов на странице (20–100, по умолчанию: 20)',
    required=False,
    examples=[
        OpenApiExample('По умолчанию', value=20),
        OpenApiExample('Максимум', value=100),
    ]
)
```

## OpenApiExample

### Примеры для запросов

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
]
```

### Примеры для ответов

```python
examples=[
    OpenApiExample(
        'Успешное создание',
        value={
            'id': 42,
            'name': 'Веб-разработка',
            'name_ru': 'Веб-разработка',
            'name_en': 'Web Development'
        },
        # request_only=False или не указывать (по умолчанию)
    ),
    OpenApiExample(
        'Ошибка валидации',
        value={'error': 'Категория с таким именем уже существует'},
        response_only=True,  # Только для ответа
    ),
]
```

## Схемы ответов

### Простые ответы

```python
responses={
    200: CategoryDetailSerializer,
    201: CategoryDetailSerializer,
    204: None,  # No content
}
```

### Ответы со списком

```python
responses={
    200: CategoryListSerializer(many=True),
}
```

### Ответы с ошибками

```python
responses={
    200: CategoryDetailSerializer,
    400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
    401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
    403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Недостаточно прав'}}},
    404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
}
```

### Ответ с несколькими схемами

```python
responses={
    200: {
        'type': 'object',
        'properties': {
            'count': {'type': 'integer', 'example': 100},
            'next': {'type': 'string', 'example': '/api/categories/?page=2'},
            'previous': {'type': 'string', 'example': None},
            'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/CategoryList'}}
        }
    },
}
```

## Полные примеры для методов

### GET список

```python
get=extend_schema(
    tags=['Категории'],
    summary='Получение списка категорий',
    description=(
        'Пагинированный список всех категорий с поддержкой поиска.\n\n'
        '**Возвращает:**\n'
        '- `id` — уникальный идентификатор\n'
        '- `name` — название на текущем языке\n'
        '- `name_ru` — название на русском\n'
        '- `name_en` — название на английском\n\n'
        '**Доступ:** всем авторизованным пользователям.'
    ),
    parameters=[
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
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Номер страницы',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Элементов на странице (20–100)',
            required=False,
        ),
    ],
    responses={
        200: CategoryListSerializer(many=True),
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
    },
    operation_id='categories_list',
)
```

### POST создание

```python
post=extend_schema(
    tags=['Категории'],
    summary='Создание новой категории',
    description=(
        'Создать новую категорию с указанным названием.\n\n'
        '**Требования:**\n'
        '- Только для администраторов\n'
        '- Название должно быть уникальным\n\n'
        '**Пример запроса:**\n'
        '```\n'
        'POST /api/categories/\n'
        '{\n'
        '  "name": "Веб-разработка"\n'
        '}\n'
        '```'
    ),
    request=CategoryCreateSerializer,
    responses={
        201: CategoryDetailSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Базовое создание',
            value={'name': 'Веб-разработка'},
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
)
```

### GET детали

```python
get=extend_schema(
    tags=['Категории'],
    summary='Получение детальной информации о категории',
    description='Получить полную информацию о категории по её идентификатору.',
    parameters=[
        OpenApiParameter(
            name='id',  # ← Используем 'id' вместо 'pk' для соответствия с URL
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Уникальный идентификатор категории',
            examples=[OpenApiExample('ID категории', value=42)],
        ),
    ],
    responses={
        200: CategoryDetailSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    operation_id='categories_retrieve',
)
```

### PUT полное обновление

```python
put=extend_schema(
    tags=['Категории'],
    summary='Полное обновление категории',
    description='Полностью обновить данные категории (все поля обязательны).',
    request=CategoryUpdateSerializer,
    parameters=[
        OpenApiParameter(
            name='id',  # ← Используем 'id' вместо 'pk'
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Уникальный идентификатор категории',
            examples=[OpenApiExample('ID категории', value=42)],
        ),
    ],
    responses={
        200: CategoryDetailSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
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
)
```

### PATCH частичное обновление

```python
patch=extend_schema(
    tags=['Категории'],
    summary='Частичное обновление категории',
    description='Частично обновить данные категории (только указанные поля).',
    request=CategoryUpdateSerializer,
    parameters=[
        OpenApiParameter(
            name='id',  # ← Используем 'id' вместо 'pk'
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Уникальный идентификатор категории',
            examples=[OpenApiExample('ID категории', value=42)],
        ),
    ],
    responses={
        200: CategoryDetailSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    examples=[
        OpenApiExample(
            'Частичное обновление (только английский перевод)',
            value={'name_en': 'Mobile Apps'},
            request_only=True,
        ),
    ],
    operation_id='categories_partial_update',
)
```

### DELETE удаление

```python
delete=extend_schema(
    tags=['Категории'],
    summary='Удаление категории',
    description='Безвозвратно удалить категорию по идентификатору.',
    parameters=[
        OpenApiParameter(
            name='id',  # ← Используем 'id' вместо 'pk'
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Уникальный идентификатор категории',
            examples=[OpenApiExample('ID категории', value=42)],
        ),
    ],
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    operation_id='categories_destroy',
)
```

## Поиск в файле

Искать в этом файле:
- "OpenApiParameter" — параметры запроса
- "OpenApiExample" — примеры
- "OpenApiTypes" — типы данных
- "responses" — схемы ответов
- "GET список" — документирование GET списка
- "POST создание" — документирование POST
- "GET детали" — документирование GET деталей
- "PUT обновление" — документирование PUT
- "PATCH частичное" — документирование PATCH
- "DELETE удаление" — документирование DELETE
- "operation_id" — именование операций
