# Best Practices для REST API View классов

## Назначение

Стандарты качества, именование, обработка ошибок, валидация и логирование при создании REST API view классов.

## Классификация ошибок и уязвимостей

**ПЕРЕД НАПИСАНИЕМ КОДА** провести внутренний аудит на наличие следующих уязвимостей:

### 🔴 CRITICAL — Критические уязвимости (блокирующие)

**Требуют немедленного исправления, блокируют запуск в продакшн:**

1. **Отсутствие проверки аутентификации пользователя**
   - Проверка `user.is_authenticated` перед доступом к атрибутам
   - Защита от `None` и `AnonymousUser`
   - Использовать `getattr(user, 'attr', default)` для безопасного доступа

2. **Race condition при проверке уникальности**
   - Использовать `select_for_update()` для атомарной проверки
   - Оборачивать проверку + создание в `transaction.atomic()`
   - Пример:
   ```python
   with transaction.atomic():
       if Model.objects.select_for_update().filter(name__iexact=name).exists():
           raise ValueError("Дубликат")
       return Model.objects.create(name=name)
   ```

3. **Отсутствие валидации длины полей**
   - Проверять `len(value) <= max_length` перед сохранением
   - Валидировать пустые значения `if not value: raise ValueError(...)`
   - Дублировать валидацию в сервисе и сериализаторе

### 🟠 HIGH — Серьёзные нарушения

**Требуют исправления перед релизом:**

1. **Несоответствие полей модели и сервиса/сериализатора**
   - Проверить, что все поля существуют в модели
   - Для `django-modeltranslation` убедиться, что поля зарегистрированы
   - Добавить `max_length` в сериализаторы

2. **Некорректные HTTP коды ответов**
   - `409 Conflict` для конфликтов уникальности (не `400`)
   - `403 Forbidden` для недостатка прав
   - `404 Not Found` для несуществующих ресурсов
   - `401 Unauthorized` для неавторизованных запросов

3. **Утечка деталей валидации**
   - Не раскрывать внутренние детали ошибок клиенту
   - Возвращать `{'error': '...'}` вместо `{'details': {...}}`
   - Логировать детали на сервере, не в ответе

### 🟡 MEDIUM — Нарушения стандартов

**Исправляются в ближайшем спринте:**

1. **Непоследовательный формат ошибок**
   - Унифицировать: `{'error': 'сообщение'}` или `{'error': {...}, 'details': {...}}`
   - Для валидации: `{'error': 'Ошибка валидации', 'details': {...}}`

2. **Отсутствие заголовка Location при создании**
   - Добавлять `headers={'Location': reverse('detail', args=[pk])}`
   - Для `201 Created` обязательно указывать URL нового ресурса

3. **Отсутствие минимальной длины поиска**
   - Добавлять `min_length=2` в поисковые сериализаторы
   - Документировать в `help_text`

### 🟢 LOW — Рекомендации на будущее

**Оптимизации и улучшения:**

1. Soft delete вместо физического удаления
2. Кэширование списков ресурсов
3. Rate limiting для защиты от злоупотреблений
4. Структурированное логирование (JSON)

---

## Чек-лист перед отправкой кода

**Прежде чем считать задачу завершённой, проверить:**

- [ ] **CRITICAL:** Проверка `user.is_authenticated` в `_is_admin()`
- [ ] **CRITICAL:** `select_for_update()` для проверки уникальности
- [ ] **CRITICAL:** Валидация длины полей (`max_length`, `min_length`)
- [ ] **CRITICAL:** Валидация пустых значений
- [ ] **HIGH:** 409 Conflict для дубликатов
- [ ] **HIGH:** Нет утечки деталей валидации в ответе
- [ ] **HIGH:** Все поля модели существуют
- [ ] **MEDIUM:** Унифицированный формат ошибок
- [ ] **MEDIUM:** Location header при создании (201)
- [ ] **MEDIUM:** `min_length` для поисковых параметров
- [ ] **Swagger:** 409 указан в `responses` для create/update
- [ ] **Swagger:** Примеры ошибок в документации

---

## Стандарты кода

### Именование классов

```python
# ✅ Правильно — суффиксы по назначению
CategoryListCreateView      # Для списка и создания
CategoryDetailView          # Для деталей/обновления/удаления
UserListCreateView
OrderDetailView

# ❌ Неправильно — отдельные классы на метод
CategoryListView
CategoryCreateView
CategoryUpdateView
CategoryDeleteView
```

### Именование методов

```python
# ✅ Правильно — стандартные HTTP методы
def get(self, request, pk: int): ...
def post(self, request): ...
def put(self, request, pk: int): ...
def patch(self, request, pk: int): ...
def delete(self, request, pk: int): ...

# ✅ Правильно — внутренние методы с префиксом _
def _handle_update(self, request, pk: int): ...
def _filter_queryset(self, queryset): ...
def _check_permissions(self, user): ...

# ❌ Неправильно — нестандартные имена
def get_category(self, request): ...
def create_category(self, request): ...
```

### Именование operation_id

```python
# ✅ Правильно — формат: {resource}_{action}
operation_id='categories_list'
operation_id='categories_create'
operation_id='categories_retrieve'
operation_id='categories_update'
operation_id='categories_partial_update'
operation_id='categories_destroy'

# ❌ Неправильно — непоследовательный стиль
operation_id='getCategories'
operation_id='categoryCreate'
operation_id='list_categories'
```

## Обработка ошибок

### Возврат ошибок валидации

```python
def post(self, request):
    serializer = CategoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Логика создания
        pass
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Обработка исключений сервиса

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
            logger.warning(f"Попытка создания без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Стандартные коды ответов

```python
# 2xx — Успех
200  # OK — успешное получение/обновление
201  # Created — успешное создание
204  # No Content — успешное удаление (без тела ответа)

# 4xx — Ошибка клиента
400  # Bad Request — ошибка валидации/неверные данные
401  # Unauthorized — не авторизован
403  # Forbidden — недостаточно прав
404  # Not Found — ресурс не найден
409  # Conflict — конфликт (например, дубликат)

# 5xx — Ошибка сервера
500  # Internal Server Error — непредвиденная ошибка
```

### Формат ответов об ошибках

```python
# Для бизнес-ошибок
{'error': 'Категория с таким именем уже существует'}

# Для ошибок валидации
{
    'name': ['Это поле обязательно.'],
    'email': ['Введите корректный email.'],
}

# Для ошибок авторизации
{'detail': 'Учетные данные не предоставлены.'}

# С деталями
{
    'error': 'Неверный формат запроса',
    'details': {'field': ['ошибка']}
}
```

## Валидация данных

### Валидация query параметров

```python
def get(self, request):
    # Валидация поискового параметра
    search_serializer = CategorySearchSerializer(data=request.query_params)
    if not search_serializer.is_valid():
        return Response(
            {
                'error': 'Неверный формат поискового запроса',
                'details': search_serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    search = search_serializer.validated_data.get('search')
    # Дальнейшая логика
```

### Валидация в сериализаторе

```python
class CategoryCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    
    def validate_name(self, value):
        """Проверить уникальность имени."""
        value_clean = value.strip().capitalize()
        if Category.objects.filter(name__iexact=value_clean).exists():
            raise serializers.ValidationError("Категория с таким именем уже существует")
        return value_clean
    
    class Meta:
        model = Category
        fields = ('name',)
```

### Валидация path параметров

```python
def get(self, request, pk: int):
    try:
        category = CategoryService.get_category_detail(pk)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    # Дальнейшая логика
```

## Логирование

### Настройка логгера

```python
# В начале файла views.py
logger = logging.getLogger('categories')
```

### Уровни логирования

```python
# INFO — штатные операции
logger.info(f"Категория создана: '{category.name}' (пользователь: {request.user.email})")
logger.info(f"Категория обновлена: ID={pk} (пользователь: {request.user.email})")
logger.info(f"Категория удалена: ID={pk} (пользователь: {request.user.email})")

# WARNING — подозрительные действия
logger.warning(f"Попытка создания категории без прав: {request.user.email}")
logger.warning(f"Попытка изменения категории без прав: {request.user.email}")
logger.warning(f"Попытка удаления категории без прав: {request.user.email}")

# ERROR — ошибки
logger.error(f"Ошибка при создании категории: {str(e)}", exc_info=True)
logger.error(f"Ошибка при обновлении категории: {str(e)}", exc_info=True)
```

### Контекст в логах

```python
# ✅ Правильно — с контекстом
logger.info(f"Категория создана: '{category.name}' (пользователь: {request.user.email}, ID: {category.id})")

# ❌ Неправильно — без контекста
logger.info("Категория создана")
```

## Документирование

### Docstring для класса

```python
class CategoryListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком категорий.
    
    **GET** — получение списка категорий с поиском и пагинацией.
    **POST** — создание новой категории (только для администраторов).
    """
```

### Docstring для методов

```python
def get(self, request):
    """Получить список категорий с опциональным поиском."""
    ...

def post(self, request):
    """Создать новую категорию."""
    ...

def _handle_update(self, request, pk: int):
    """Внутренний метод для обработки PUT/PATCH запросов."""
    ...
```

### Описание в @extend_schema

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

## Безопасность

### Проверка прав доступа

```python
permission_classes = [IsAuthenticated]

# В сервисе:
if not CategoryService._is_admin(user):
    raise PermissionError("Только администраторы могут создавать категории")
```

### Валидация входных данных

```python
# Никогда не доверять входным данным
def post(self, request):
    serializer = CategoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Использовать только валидированные данные
        name = serializer.validated_data['name']
```

### Логирование без чувствительных данных

```python
# ✅ Правильно
logger.info(f"Категория создана: '{category.name}' (пользователь: {request.user.email})")

# ❌ Неправильно — логирование паролей/токенов
logger.info(f"Пользователь: {request.user.password}")
logger.info(f"Токен: {request.auth.token}")
```

## Производительность

### Оптимизация запросов

```python
# ✅ Правильно — select_related/prefetch_related
categories = Category.objects.select_related('related_field').all()

# ❌ Неправильно — N+1 запросов
for category in Category.objects.all():
    print(category.related_field.name)
```

### Пагинация обязательна

```python
# ✅ Правильно — с пагинацией
paginator = self.pagination_class()
paginated_categories = paginator.paginate_queryset(categories, request)
return paginator.get_paginated_response(serializer.data)

# ❌ Неправильно — без пагинации
return Response(CategorySerializer(categories, many=True).data)
```

### Кэширование

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='get')
class CategoryDetailView(APIView):
    def get(self, request, pk: int):
        ...
```

## Тестирование

### Минимальные тесты

```python
class CategoryAPITestCase(APITestCase):
    def test_list_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_category(self):
        data = {'name': 'Тестовая категория'}
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_category_detail(self):
        response = self.client.get(f'/api/categories/{category_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_category(self):
        data = {'name': 'Обновлённая категория'}
        response = self.client.put(f'/api/categories/{category_id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_category(self):
        response = self.client.delete(f'/api/categories/{category_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Поиск в файле

Искать в этом файле:
- "Именование классов" — стандарты имён view классов
- "operation_id" — именование операций
- "Обработка ошибок" — паттерны обработки исключений
- "Валидация" — валидация данных
- "Логирование" — стандарты логирования
- "Безопасность" — проверка прав и валидация
- "Производительность" — оптимизация запросов
- "Тестирование" — минимальные тесты
