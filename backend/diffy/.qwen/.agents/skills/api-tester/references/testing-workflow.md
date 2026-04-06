# Testing Workflow

## Назначение

Полное руководство по 7-шаговому процессу тестирования Django REST API приложений.

## Шаг 1: Ознакомление с приложением

### Файлы для изучения

```bash
<app>/
├── models.py       # Модели данных
├── services.py     # Бизнес-логика
├── views.py        # API views
├── serializers.py  # Сериализаторы
├── urls.py         # Маршруты
└── translation.py  # Настройки мультиязычности
```

### Что искать

**В models.py:**
- Названия моделей и полей
- Ограничения (max_length, unique, null/blank)
- Связи (ForeignKey, ManyToMany)
- modeltranslation поля

**В services.py:**
- Методы CRUD операций
- Проверки прав (`_is_admin`)
- Валидация данных
- Обработка исключений

**В views.py:**
- Классы views (ListCreateView, DetailView)
- Permissions
- Пагинация
- Поиск и фильтрация

**В serializers.py:**
- Валидаторы полей
- Обязательные/необязательные поля
- Уникальность

## Шаг 2: Изучение примеров тестов

### Базовые примеры

```bash
test/unit/categories/
├── conftest.py              # 8 фикстур
├── test_services.py         # 45 тестов
├── test_views.py            # 53 теста
└── README.md                # Отчёт
```

### Ключевые паттерны

**Фикстуры:**
```python
@pytest.fixture
def cleanup_categories():
    yield
    Category.objects.all().delete()

@pytest.fixture
def test_category(cleanup_categories):
    return Category.objects.create(
        name_ru='Тестовая категория',
        name_en='Test Category'
    )
```

**Тесты сервисов:**
```python
class TestIsAdmin:
    def test_none_user_returns_false(self):
        assert CategoryService._is_admin(None) is False
```

**Тесты views:**
```python
class TestAuthentication:
    def test_list_without_auth_returns_401(self, api_client):
        response = api_client.get('/api/categories/')
        assert response.status_code == 401
```

## Шаг 3: Создание структуры тестов

### Директория

```bash
test/unit/<app>/
├── __init__.py
├── conftest.py       # Локальные фикстуры
├── test_services.py  # Тесты сервисного слоя
├── test_views.py     # Тесты API views
└── README.md         # Отчёт о тестировании
```

### Импорты в conftest.py

Добавить в `test/conftest.py`:
```python
# Локальные фикстуры для unit-тестов <app>
from test.unit.<app>.conftest import (  # noqa: F401
    cleanup_<models>,
    test_<model>,
    many_<models>,
    searchable_<models>,
)
```

## Шаг 4: Написание фикстур

### Обязательные фикстуры

**Очистка:**
```python
@pytest.fixture
def cleanup_<models>():
    yield
    <Model>.objects.all().delete()
```

**Тестовые данные:**
```python
@pytest.fixture
def test_<model>(cleanup_<models>):
    return <Model>.objects.create(
        name_ru='Тестовый объект',
        name_en='Test Object'
    )

@pytest.fixture
def many_<models>(cleanup_<models>, test_<model>):
    return [
        <Model>.objects.create(name_ru=f'Объект {i}')
        for i in range(1, 26)
    ]

@pytest.fixture
def searchable_<models>(cleanup_<models>):
    return {
        'item1': <Model>.objects.create(name_ru='Ноутбук'),
        'item2': <Model>.objects.create(name_ru='Телефон'),
    }
```

**Специальные сценарии:**
```python
@pytest.fixture
def <models>_in_different_categories(cleanup_<models>, test_category, test_category2):
    return {
        'cat1_item': <Model>.objects.create(category=test_category),
        'cat2_item': <Model>.objects.create(category=test_category2),
    }
```

## Шаг 5: Написание тестов сервисов

### Структура test_services.py

```python
pytestmark = pytest.mark.django_db

# 🔴 CRITICAL: Тесты критических уязвимостей
class TestIsAdmin:
    """7 тестов"""

class TestCreate<Model>RaceCondition:
    """8-10 тестов"""

class TestUpdate<Model>RaceCondition:
    """6 тестов"""

# 🟠 HIGH: Функциональность
class TestGet<Models>List:
    """8 тестов"""

class TestGet<Model>Detail:
    """2-3 теста"""

class TestDelete<Model>:
    """3 теста"""

# 🟡 MEDIUM: Граничные случаи
class Test<Model>ServiceEdgeCases:
    """8-10 тестов"""

class Test<Model>ServiceLogging:
    """3 теста"""
```

### Обязательные тесты

**CRITICAL (21+ тестов):**
- `_is_admin()` с None, AnonymousUser, inactive_user
- Race condition при создании (select_for_update)
- Валидация длины (max_length)
- Валидация пустых значений
- Проверка прав (PermissionError)

**HIGH (13+ тестов):**
- Получение списка (пустой, сортировка)
- Поиск (по разным полям, case-insensitive)
- Фильтрация
- Получение деталей (существующий, несуществующий)
- Удаление (успех, права, несуществующий)

**MEDIUM (10+ тестов):**
- Спецсимволы, unicode, цифры
- Сохранение ID при обновлении
- Возврат bool при удалении
- Логирование операций

## Шаг 6: Написание тестов views

### Структура test_views.py

```python
pytestmark = pytest.mark.django_db

# 🔴 CRITICAL: Аутентификация и права
class TestAuthentication:
    """5 тестов (401 без auth)"""

class TestUserPermissions:
    """5 тестов (403 для не-админов)"""

# 🟠 HIGH: CRUD операции
class Test<Model>List:
    """6 тестов (пагинация, sorting)"""

class Test<Model>Search:
    """8 тестов (поиск, фильтрация)"""

class Test<Model>Create:
    """9 тестов (создание, валидация)"""

class Test<Model>Detail:
    """4 теста (детали)"""

class Test<Model>Update:
    """7 тестов (PUT, PATCH)"""

class Test<Model>Delete:
    """3 теста (удаление)"""

# 🟡 MEDIUM: Валидация и формат
class TestValidationEdgeCases:
    """5 тестов"""

class TestErrorResponseFormat:
    """3 теста"""
```

### Обязательные тесты

**Аутентификация (5 тестов):**
- GET список без auth → 401
- GET детали без auth → 401
- POST без auth → 401
- PUT без auth → 401
- DELETE без auth → 401

**Права доступа (5 тестов):**
- Обычный пользователь не может создавать (403)
- Обычный пользователь не может обновлять (403)
- Обычный пользователь не может удалять (403)
- Обычный пользователь может смотреть список (200)
- Обычный пользователь может смотреть детали (200)

**CRUD (30+ тестов):**
- Пагинация (page_size, page=2)
- Поиск (по разным полям, min_length)
- Создание (успех, с переводами, с img)
- Дубликаты (400/409)
- Валидация длины (400)
- Валидация пустоты (400)
- Location header (201)
- Обновление (PUT, PATCH)
- Удаление (успех, 404, idempotent)

## Шаг 7: Запуск тестов и отчёт

### Запуск тестов

```bash
# Все тесты приложения
python -m pytest test/unit/<app>/ -v

# Только сервисы
python -m pytest test/unit/<app>/test_services.py -v

# Только views
python -m pytest test/unit/<app>/test_views.py -v

# С покрытием
python -m pytest test/unit/<app>/ --cov=<app> --cov-report=html

# Один тест
python -m pytest test/unit/<app>/test_services.py::TestIsAdmin::test_admin_user_returns_true -v
```

### Заполнение README.md

**Статистика:**
```markdown
| Тип тестов | Файл | Тестов | Пройдено | Статус |
|------------|------|--------|----------|--------|
| Services   | test_services.py | 45 | 45 | ✅ |
| Views      | test_views.py    | 53 | 53 | ✅ |
| ИТОГО      |        | 98 | 98 | ✅ |
```

**Покрытие по классам:**
```markdown
| Класс тестов | Тестов | Описание |
|--------------|--------|----------|
| TestIsAdmin | 7 | Проверка прав администратора |
| ... | ... | ... |
```

**Отклонения:**
```markdown
## ⚠️ Выявленные отклонения

1. **Проблема** — описание
   **Файл** — где найдено
   **Влияние** — к чему приводит
   **Статус** — исправлено/задокументировано
```

## Чек-лист завершения

- [ ] Создана структура директорий
- [ ] Написаны фикстуры (очистка, данные, специальные)
- [ ] Импорты добавлены в test/conftest.py
- [ ] Написаны тесты сервисов (45+ тестов)
- [ ] Написаны тесты views (53+ тестов)
- [ ] Все тесты проходят (100% pass rate)
- [ ] Заполнен README.md
- [ ] Задокументированы отклонения

---

**Результат:** Комплексное покрытие тестами с документированием всех найденных отклонений.
