# Fixtures Guide

## Назначение

Руководство по созданию фикстур для тестирования Django REST API приложений.

## Типы фикстур

### 1. Фикстуры очистки

**Назначение:** Автоматическая очистка БД после тестов.

```python
@pytest.fixture
def cleanup_<models>():
    """
    Фикстура для очистки <models> после теста.
    
    Использование:
        def test_something(cleanup_<models>):
            # Тест создаёт <models>
            # После теста все <models> будут удалены
    """
    yield
    <Model>.objects.all().delete()
```

**Особенности:**
- Использует `yield` для отложенной очистки
- Очищает ВСЕ объекты модели после теста
- Не требует явного вызова в тестах

---

### 2. Фикстуры одиночных объектов

**Назначение:** Создание одного тестового объекта.

```python
@pytest.fixture
def test_<model>(cleanup_<models>):
    """
    Создать один тестовый <model>.
    
    Возвращает: <Model>
    Автоматически очищается после теста.
    """
    return <Model>.objects.create(
        name_ru='Тестовый объект',
        name_en='Test Object',
        # другие поля...
    )
```

**Особенности:**
- Зависит от `cleanup_<models>` для авто-очистки
- Возвращает объект для использования в тестах
- Стандартные данные для предсказуемости

---

### 3. Фикстуры множественных объектов

**Назначение:** Создание набора объектов для тестирования пагинации.

```python
@pytest.fixture
def many_<models>(cleanup_<models>, test_<model>):
    """
    Создать 25 <models> для тестирования пагинации.
    
    Возвращает: list[<Model>]
    Автоматически очищается после теста.
    """
    <models>_data = [
        (f'Объект {i:02d}', f'Object {i:02d}')
        for i in range(1, 26)
    ]
    
    <models> = [
        <Model>.objects.create(name_ru=ru, name_en=en)
        for ru, en in <models>_data
    ]
    
    return <models>
```

**Особенности:**
- Создаёт 25 объектов (page_size=20, страница 2 = 5 объектов)
- Возвращает список для доступа по индексу
- Используется для тестов пагинации

---

### 4. Фикстуры для поиска

**Назначение:** Создание объектов с разными названиями для тестирования поиска.

```python
@pytest.fixture
def searchable_<models>(cleanup_<models>):
    """
    Создать <models> для тестирования поиска.
    
    Возвращает: dict с <models> по ключам
    Автоматически очищается после теста.
    """
    <models> = {
        'laptop': <Model>.objects.create(
            name_ru='Ноутбук Dell XPS 15',
            name_en='Dell XPS 15 Laptop',
        ),
        'phone': <Model>.objects.create(
            name_ru='Смартфон iPhone 15',
            name_en='iPhone 15 Smartphone',
        ),
        'tablet': <Model>.objects.create(
            name_ru='Планшет iPad Pro',
            name_en='iPad Pro Tablet',
        ),
        'headphones': <Model>.objects.create(
            name_ru='Наушники Sony WH-1000XM5',
            name_en='Sony WH-1000XM5 Headphones',
        ),
        'watch': <Model>.objects.create(
            name_ru='Умные часы Apple Watch',
            name_en='Apple Watch Smartwatch',
        ),
    }
    
    return <models>
```

**Особенности:**
- Возвращает dict для доступа по ключу
- Разные названия для тестирования поиска
- Покрытие русских и английских названий

---

### 5. Фикстуры для фильтрации

**Назначение:** Создание объектов в разных категориях для тестирования фильтрации.

```python
@pytest.fixture
def <models>_in_different_categories(cleanup_<models>, cleanup_categories, test_category, test_category2):
    """
    Создать <models> в разных категориях для тестирования фильтрации.
    
    Возвращает: dict с <models>
    Автоматически очищается после теста.
    """
    <models> = {
        'cat1_<model>1': <Model>.objects.create(
            name_ru='Товар 1 в категории 1',
            name_en='Product 1 in Category 1',
            category=test_category,
        ),
        'cat1_<model>2': <Model>.objects.create(
            name_ru='Товар 2 в категории 1',
            name_en='Product 2 in Category 1',
            category=test_category,
        ),
        'cat2_<model>1': <Model>.objects.create(
            name_ru='Товар 1 в категории 2',
            name_en='Product 1 in Category 2',
            category=test_category2,
        ),
    }
    
    return <models>
```

**Особенности:**
- Зависит от фикстур категорий
- Объекты в разных категориях
- Для тестов фильтрации по FK

---

### 6. Фикстуры для связанных моделей

**Назначение:** Создание связанных объектов.

```python
@pytest.fixture
def test_category(cleanup_categories):
    """
    Создать одну тестовую категорию для товаров.
    
    Возвращает: Category
    Автоматически очищается после теста.
    """
    return Category.objects.create(
        name_ru='Тестовая категория',
        name_en='Test Category'
    )

@pytest.fixture
def test_category2(cleanup_categories):
    """
    Создать вторую тестовую категорию для товаров.
    
    Возвращает: Category
    Автоматически очищается после теста.
    """
    return Category.objects.create(
        name_ru='Вторая категория',
        name_en='Second Category'
    )
```

**Особенности:**
- Создаёт связанные объекты (категории для товаров)
- Используется другими фикстурами
- Авто-очистка через `cleanup_categories`

---

## Импортирование в общие фикстуры

### Добавление в test/conftest.py

```python
# Локальные фикстуры для unit-тестов <app>
from test.unit.<app>.conftest import (  # noqa: F401
    cleanup_<models>,
    cleanup_categories,
    test_<model>,
    test_category,
    test_category2,
    many_<models>,
    searchable_<models>,
    <models>_in_different_categories,
)
```

**Важно:**
- Использовать `# noqa: F401` для игнорирования предупреждений
- Импортировать ВСЕ локальные фикстуры
- Не редактировать другие части файла

---

## Примеры для разных моделей

### Для Category

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

@pytest.fixture
def many_categories(cleanup_categories):
    categories_data = [
        (f'Категория {i:02d}', f'Category {i:02d}')
        for i in range(1, 26)
    ]
    return [
        Category.objects.create(name_ru=ru, name_en=en)
        for ru, en in categories_data
    ]

@pytest.fixture
def searchable_categories(cleanup_categories):
    return {
        'electronics': Category.objects.create(
            name_ru='Электроника',
            name_en='Electronics'
        ),
        'phones': Category.objects.create(
            name_ru='Телефоны',
            name_en='Phones'
        ),
        # ...
    }
```

### Для Product

```python
@pytest.fixture
def cleanup_products():
    yield
    Product.objects.all().delete()

@pytest.fixture
def test_product(cleanup_products, test_category):
    return Product.objects.create(
        name_ru='Тестовый товар',
        name_en='Test Product',
        category=test_category,
        img='products/test.jpg'
    )

@pytest.fixture
def many_products(cleanup_products, test_category):
    products_data = [
        (f'Товар {i:02d}', f'Product {i:02d}')
        for i in range(1, 26)
    ]
    return [
        Product.objects.create(
            name_ru=ru,
            name_en=en,
            category=test_category,
            img=f'products/product-{i:02d}.jpg'
        )
        for i, (ru, en) in enumerate(products_data, 1)
    ]
```

### Для User (если кастомная)

```python
@pytest.fixture
def cleanup_users():
    yield
    User.objects.all().delete()

@pytest.fixture
def test_user(cleanup_users):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        role='user',
        is_active=True
    )

@pytest.fixture
def admin(cleanup_users):
    return User.objects.create_user(
        email='admin@example.com',
        password='TestPass123!',
        role='admin',
        is_staff=True,
        is_active=True
    )
```

---

## Лучшие практики

### 1. Всегда использовать очистку

```python
# ✅ Правильно
@pytest.fixture
def test_<model>(cleanup_<models>):
    return <Model>.objects.create(...)

# ❌ Неправильно
@pytest.fixture
def test_<model>():
    return <Model>.objects.create(...)  # Нет очистки!
```

### 2. Возвращать объекты, а не создавать в тестах

```python
# ✅ Правильно
def test_something(test_<model>):
    assert test_<model>.id is not None

# ❌ Неправильно
def test_something():
    <model> = <Model>.objects.create(...)  # Дублирование кода
```

### 3. Использовать предсказуемые данные

```python
# ✅ Правильно
name_ru='Тестовый объект'  # Предсказуемо

# ❌ Неправильно
name_ru=f'Объект {uuid.uuid4()}'  # Случайно
```

### 4. Группировать связанные фикстуры

```python
# ✅ Правильно
@pytest.fixture
def products_in_different_categories(cleanup_products, test_category, test_category2):
    ...

# ❌ Неправильно
# Создавать категории в каждом тесте
```

### 5. Документировать фикстуры

```python
@pytest.fixture
def test_<model>(cleanup_<models>):
    """
    Создать один тестовый <model>.
    
    Возвращает: <Model>
    Автоматически очищается после теста.
    """
    ...
```

---

## Чек-лист создания фикстур

- [ ] Создана фикстура очистки (`cleanup_<models>`)
- [ ] Создана фикстура одиночного объекта (`test_<model>`)
- [ ] Создана фикстура множественных объектов (`many_<models>`)
- [ ] Создана фикстура для поиска (`searchable_<models>`)
- [ ] Созданы фикстуры для связанных моделей (`test_category`, etc.)
- [ ] Создана фикстура для фильтрации (`<models>_in_different_categories`)
- [ ] Все фикстуры импортированы в `test/conftest.py`
- [ ] Все фикстуры имеют docstring
- [ ] Все фикстуры используют очистку

---

**Результат:** Надёжная система фикстур для изолированного тестирования.
