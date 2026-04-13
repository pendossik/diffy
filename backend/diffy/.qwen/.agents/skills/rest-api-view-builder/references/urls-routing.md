# URLs Routing для REST API

## Назначение

Руководство по настройке маршрутизации в Django urls.py для REST API с соблюдением RESTful стандартов.

## Базовая структура urls.py

```python
from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView

urlpatterns = [
    # GET (список с поиском) / POST (создание)
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    # GET (детали) / PUT (обновление) / PATCH (частичное) / DELETE (удаление)
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
```

## RESTful маршруты

### Правильные RESTful паттерны

```python
# Список ресурсов + создание
path('', ResourceListCreateView.as_view(), name='resource-list-create'),

# Детали ресурса + обновление + удаление
path('<int:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
```

### HTTP методы для маршрутов

| Метод | Маршрут | Действие | View метод |
|-------|---------|----------|------------|
| GET | `/api/categories/` | Список категорий | `get()` |
| POST | `/api/categories/` | Создание категории | `post()` |
| GET | `/api/categories/{pk}/` | Детали категории | `get()` |
| PUT | `/api/categories/{pk}/` | Полное обновление | `put()` |
| PATCH | `/api/categories/{pk}/` | Частичное обновление | `patch()` |
| DELETE | `/api/categories/{pk}/` | Удаление категории | `delete()` |

### Неправильные паттерны (избегать)

```python
# ❌ НЕ использовать RPC-стиль вместо REST
path('create/', CategoryCreateView.as_view(), name='category-create'),
path('<int:category_id>/update/', CategoryUpdateView.as_view(), name='category-update'),
path('<int:category_id>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
path('list/', CategoryListView.as_view(), name='category-list'),
```

## Именование паттернов

### Стандартные имена

```python
name='category-list-create'      # Для списка/создания
name='category-detail'           # Для деталей/обновления/удаления
```

### Префиксы для namespaces

```python
# В главном urls.py
app_name = 'categories'

# Или в главном urls.py проекта
path('api/categories/', include('categories.urls', namespace='categories')),
```

## Path параметры

### Использование pk

```python
# ✅ Правильно — использовать pk
path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

# В view классе:
def get(self, request, pk: int):
    category = CategoryService.get_category_detail(pk)
```

### Кастомные имена параметров

```python
# Если нужно конкретное имя
path('<int:category_id>/', CategoryDetailView.as_view(), name='category-detail'),

# В view классе:
def get(self, request, category_id: int):
    category = CategoryService.get_category_detail(category_id)
```

### UUID параметры

```python
path('<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
path('<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
path('<str:code>/', CategoryDetailView.as_view(), name='category-detail'),
```

## Вложенные ресурсы

### Один уровень вложенности

```python
# Категории и их элементы
urlpatterns = [
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('<int:pk>/items/', CategoryItemListView.as_view(), name='category-item-list'),
]
```

### Два уровня вложенности

```python
urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:category_pk>/items/', ItemListCreateView.as_view(), name='item-list'),
    path('categories/<int:category_pk>/items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
]
```

## Подключение в главном urls.py

### Префикс API

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/categories/', include('categories.urls')),
    path('api/users/', include('users.urls')),
    path('api/orders/', include('orders.urls')),
]
```

### С namespace

```python
# project/urls.py
urlpatterns = [
    path('api/categories/', include('categories.urls', namespace='categories')),
    path('api/users/', include('users.urls', namespace='users')),
]

# В views для reverse:
reverse('categories:category-detail', kwargs={'pk': 42})
```

## Полные примеры

### Пример 1: Простой ресурс

```python
# categories/urls.py
from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView

urlpatterns = [
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
```

### Пример 2: Ресурс с вложенными элементами

```python
# categories/urls.py
from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    CategoryItemListCreateView,
    CategoryItemDetailView,
)

urlpatterns = [
    # Категории
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Элементы категории
    path('<int:category_pk>/items/', CategoryItemListCreateView.as_view(), name='category-item-list'),
    path('<int:category_pk>/items/<int:pk>/', CategoryItemDetailView.as_view(), name='category-item-detail'),
]
```

### Пример 3: Несколько ресурсов

```python
# users/urls.py
from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    UserProjectsListView,
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/projects/', UserProjectsListView.as_view(), name='user-projects'),
]
```

## Валидация параметров

### В view классе

```python
def get(self, request, pk: int):
    try:
        category = CategoryService.get_category_detail(pk)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)
```

### С несколькими параметрами

```python
def get(self, request, category_pk: int, pk: int):
    try:
        item = CategoryItemService.get_item_detail(category_pk, pk)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategoryItemDetailSerializer(item)
    return Response(serializer.data)
```

## Поиск в файле

Искать в этом файле:
- "RESTful маршруты" — правильные паттерны маршрутизации
- "HTTP методы" — таблица методов и маршрутов
- "pk" — использование pk параметра
- "Вложенные ресурсы" — маршруты для вложенных структур
- "namespace" — именование с namespace
- "UUID параметры" — альтернативные типы параметров
