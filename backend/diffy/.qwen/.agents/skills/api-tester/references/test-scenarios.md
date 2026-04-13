# Test Scenarios

## Назначение

Библиотека тестовых сценариев для комплексного покрытия Django REST API приложений.

## 🔴 CRITICAL сценарии (обязательно)

### 1. Проверка `_is_admin()` — 7 тестов

**Цель:** Убедиться в корректной проверке прав администратора.

```python
class TestIsAdmin:
    # Позитивные
    def test_admin_user_returns_true(self, admin)
    def test_superuser_returns_true(self, superuser)
    
    # Негативные
    def test_regular_user_returns_false(self, user)
    def test_inactive_user_returns_false(self, inactive_user)
    
    # Критические (защита от уязвимостей)
    def test_none_user_returns_false(self)
    def test_anonymous_user_returns_false(self)
    def test_user_without_role_attribute(self, user_factory)
```

**Что проверяем:**
- Защита от `None`
- Защита от `AnonymousUser`
- Защита от неактивных пользователей
- Корректная проверка по `role`, `is_staff`, `is_superuser`

---

### 2. Race condition при создании — 8-10 тестов

**Цель:** Проверить атомарность проверки уникальности и создания.

```python
class TestCreate<Model>RaceCondition:
    # Позитивные
    def test_create_unique_name_success(self, admin, test_<model>)
    def test_create_same_name_different_category_success(self, admin, test_category, test_category2)
    
    # Негативные
    def test_create_duplicate_name_raises_error(self, admin, test_<model>)
    def test_create_duplicate_case_insensitive(self, admin, test_<model>)
    def test_create_name_too_long_raises_error(self, admin)
    def test_create_empty_name_raises_error(self, admin)
    def test_create_whitespace_only_name_raises_error(self, admin)
    def test_create_non_admin_raises_permission_error(self, user)
    def test_create_with_nonexistent_category_raises_error(self, admin)
    
    # Трансформация данных
    def test_create_strips_name(self, admin)
```

**Что проверяем:**
- `select_for_update()` в транзакции
- Уникальность в рамках категории/глобально
- Валидация `max_length`
- Валидация пустых значений
- Проверка прав (PermissionError)
- Проверка существующего FK

---

### 3. Race condition при обновлении — 6 тестов

**Цель:** Проверить атомарность проверки уникальности и обновления.

```python
class TestUpdate<Model>RaceCondition:
    # Позитивные
    def test_update_same_name_success(self, admin, test_<model>)
    
    # Негативные
    def test_update_to_duplicate_name_raises_error(self, admin, test_<model>)
    def test_update_name_too_long_raises_error(self, admin, test_<model>)
    def test_update_empty_name_raises_error(self, admin, test_<model>)
    def test_update_non_admin_raises_permission_error(self, user, test_<model>)
    def test_update_nonexistent_<model>_raises_error(self, admin)
```

**Что проверяем:**
- `select_for_update()` в транзакции
- Уникальность с исключением текущего объекта
- Валидация `max_length`
- Валидация пустых значений

---

## 🟠 HIGH сценарии (обязательно)

### 4. Получение списка — 8 тестов

```python
class TestGet<Models>List:
    def test_get_list_empty(self)
    def test_get_list_returns_all_sorted(self, many_<models>)
    def test_filter_by_category(self, products_in_different_categories, test_category)
    def test_search_by_name_ru(self, searchable_<models>)
    def test_search_by_name_en(self, searchable_<models>)
    def test_search_case_insensitive(self, searchable_<models>)
    def test_search_empty_string_returns_all(self, searchable_<models>)
    def test_search_with_category_filter(self, searchable_<models>, test_category)
```

**Что проверяем:**
- Пустой список
- Сортировка по имени
- Фильтрация по FK
- Поиск по мультиязычным полям
- Регистронезависимость
- Комбинация поиск + фильтр

---

### 5. Получение деталей — 2-3 теста

```python
class TestGet<Model>Detail:
    def test_get_detail_success(self, test_<model>)
    def test_get_detail_with_category(self, test_<model>)  # select_related
    def test_get_detail_nonexistent_id_raises_error(self)
```

**Что проверяем:**
- Корректное получение по ID
- Оптимизация запросов (select_related)
- Обработка несуществующего ID

---

### 6. Удаление — 3 теста

```python
class TestDelete<Model>:
    def test_delete_success(self, admin, test_<model>)
    def test_delete_non_admin_raises_permission_error(self, user, test_<model>)
    def test_delete_nonexistent_<model>_raises_error(self, admin)
```

**Что проверяем:**
- Успешное удаление
- Проверка прав
- Обработка несуществующего объекта

---

## 🟡 MEDIUM сценарии (рекомендуется)

### 7. Граничные случаи — 8-10 тестов

```python
class Test<Model>ServiceEdgeCases:
    def test_create_with_special_characters(self, admin, test_<model>)
    def test_create_with_numbers(self, admin, test_<model>)
    def test_create_with_unicode(self, admin, test_<model>)
    def test_update_preserves_id(self, admin, test_<model>)
    def test_delete_returns_bool(self, admin, test_<model>)
    def test_create_<model>_exists_in_db(self, admin, test_<model>)
    def test_get_<models>_list_is_queryset(self)
    def test_update_with_same_name_success(self, admin, test_<model>)
    def test_create_multiple_<models>_transaction(self, admin, test_<model>)
    def test_update_<field>_field(self, admin, test_<model>)
```

**Что проверяем:**
- Спецсимволы, unicode, цифры
- Сохранение ID при обновлении
- Тип возврата (bool)
- Существование в БД
- Тип возврата (QuerySet)
- Транзакционность

---

### 8. Логирование — 3 теста

```python
class Test<Model>ServiceLogging:
    def test_create_logs_info_message(self, admin, test_<model>, caplog)
    def test_update_logs_info_message(self, admin, test_<model>, caplog)
    def test_delete_logs_info_message(self, admin, test_<model>, caplog)
```

**Что проверяем:**
- Наличие логов для всех операций
- Корректный уровень (INFO)
- Содержание сообщения

---

## 🔴 CRITICAL сценарии для Views

### 9. Аутентификация — 5 тестов

```python
class TestAuthentication:
    def test_list_without_auth_returns_401(self, api_client, test_<model>)
    def test_detail_without_auth_returns_401(self, api_client, test_<model>)
    def test_create_without_auth_returns_401(self, api_client)
    def test_update_without_auth_returns_401(self, api_client, test_<model>)
    def test_delete_without_auth_returns_401(self, api_client, test_<model>)
```

**Что проверяем:**
- Все эндпоинты требуют auth
- Возврат 401 Unauthorized

---

### 10. Права доступа — 5 тестов

```python
class TestUserPermissions:
    def test_user_cannot_create_<model>(self, jwt_user_client, test_<model>)
    def test_user_cannot_update_<model>(self, jwt_user_client, test_<model>)
    def test_user_cannot_delete_<model>(self, jwt_user_client, test_<model>)
    def test_user_can_list_<models>(self, jwt_user_client, many_<models>)
    def test_user_can_get_<model>_detail(self, jwt_user_client, test_<model>)
```

**Что проверяем:**
- Обычный пользователь не может создавать (403)
- Обычный пользователь не может обновлять (403)
- Обычный пользователь не может удалять (403)
- Обычный пользователь может читать (200)

---

## 🟠 HIGH сценарии для Views

### 11. Список с пагинацией — 6 тестов

```python
class Test<Model>List:
    def test_list_empty_returns_success(self, jwt_admin_client)
    def test_list_returns_paginated_results(self, jwt_admin_client, many_<models>)
    def test_list_pagination_page_2(self, jwt_admin_client, many_<models>)
    def test_list_custom_page_size(self, jwt_admin_client, many_<models>)
    def test_list_sorted_by_name(self, jwt_admin_client, many_<models>)
    def test_list_includes_translation_fields(self, jwt_admin_client, test_<model>)
```

**Что проверяем:**
- Пустой список (200)
- Пагинация (count, results, next, previous)
- Вторая страница
- Кастомный page_size
- Сортировка
- Мультиязычные поля в ответе

---

### 12. Поиск — 8 тестов

```python
class Test<Model>Search:
    def test_search_by_name_ru(self, jwt_admin_client, searchable_<models>)
    def test_search_by_name_en(self, jwt_admin_client, searchable_<models>)
    def test_search_case_insensitive(self, jwt_admin_client, searchable_<models>)
    def test_search_partial_match(self, jwt_admin_client, searchable_<models>)
    def test_search_empty_returns_all(self, jwt_admin_client, searchable_<models>)
    def test_search_single_char_returns_400(self, jwt_admin_client, searchable_<models>)  # min_length=2
    def test_search_filter_by_category(self, jwt_admin_client, products_in_different_categories, test_category)
    def test_search_with_category_filter(self, jwt_admin_client, products_in_different_categories, test_category)
```

**Что проверяем:**
- Поиск по русским названиям
- Поиск по английским названиям
- Регистронезависимость
- Частичное совпадение
- Пустой поиск
- min_length=2 для поиска
- Фильтр по категории
- Комбинация поиск + фильтр

---

### 13. Создание — 9 тестов

```python
class Test<Model>Create:
    def test_admin_create_success(self, jwt_admin_client, test_<model>, cleanup)
    def test_admin_create_with_translations(self, jwt_admin_client, test_<model>, cleanup)
    def test_admin_create_with_img(self, jwt_admin_client, test_<model>, cleanup)
    def test_admin_create_duplicate_returns_400(self, jwt_admin_client, test_<model>)
    def test_admin_create_duplicate_different_category_success(self, jwt_admin_client, test_category, test_category2)
    def test_admin_create_name_too_long_returns_400(self, jwt_admin_client, test_<model>)
    def test_admin_create_empty_name_returns_400(self, jwt_admin_client, test_<model>)
    def test_admin_create_nonexistent_category_returns_400(self, jwt_admin_client)
    def test_create_returns_location_header(self, jwt_admin_client, test_<model>, cleanup)
```

**Что проверяем:**
- Успешное создание (201)
- Создание с переводами
- Создание с изображением
- Дубликат имени (400/409)
- Дубликат в другой категории
- Валидация длины
- Валидация пустоты
- Несуществующая категория
- Location header

---

### 14. Детали — 4 теста

```python
class Test<Model>Detail:
    def test_get_detail_success(self, jwt_admin_client, test_<model>)
    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client)
    def test_get_detail_includes_category_info(self, jwt_admin_client, test_<model>)
    def test_get_detail_includes_translations(self, jwt_admin_client, test_<model>)
```

**Что проверяем:**
- Успешное получение (200)
- Несуществующий объект (404)
- category_info в ответе
- name_ru/name_en в ответе

---

### 15. Обновление — 7 тестов

```python
class Test<Model>Update:
    def test_admin_put_full_update_success(self, jwt_admin_client, test_<model>)
    def test_admin_patch_partial_update_name_only(self, jwt_admin_client, test_<model>)
    def test_admin_patch_partial_update_img_only(self, jwt_admin_client, test_<model>)
    def test_admin_patch_partial_update_<field>_only(self, jwt_admin_client, test_<model>, test_<model>2)
    def test_admin_update_duplicate_name_returns_400(self, jwt_admin_client, test_<model>)
    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client)
    def test_admin_update_name_too_long_returns_400(self, jwt_admin_client, test_<model>)
    def test_admin_update_empty_name_returns_400(self, jwt_admin_client, test_<model>)
```

**Что проверяем:**
- Полное обновление (PUT, 200)
- Частичное обновление (PATCH) только name
- Частичное обновление только img
- Частичное обновление только FK
- Дубликат имени (400/409)
- Несуществующий объект (404)
- Валидация длины
- Валидация пустоты

---

### 16. Удаление — 3 теста

```python
class Test<Model>Delete:
    def test_admin_delete_success(self, jwt_admin_client, test_<model>)
    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client)
    def test_delete_idempotent(self, jwt_admin_client, test_<model>)
```

**Что проверяем:**
- Успешное удаление (200)
- Несуществующий объект (404)
- Повторное удаление (404)

---

## 🟡 MEDIUM сценарии для Views

### 17. Валидация — 5 тестов

```python
class TestValidationEdgeCases:
    def test_create_with_special_characters(self, jwt_admin_client, test_<model>, cleanup)
    def test_create_with_numbers(self, jwt_admin_client, test_<model>, cleanup)
    def test_update_same_name_success(self, jwt_admin_client, test_<model>)
    def test_create_whitespace_only_returns_400(self, jwt_admin_client, test_<model>)
    def test_update_whitespace_only_returns_400(self, jwt_admin_client, test_<model>)
```

---

### 18. Формат ошибок — 3 теста

```python
class TestErrorResponseFormat:
    def test_error_response_has_error_key(self, jwt_user_client, test_<model>)
    def test_validation_error_has_details(self, jwt_admin_client, test_<model>)
    def test_401_error_format(self, api_client, test_<model>)
```

**Что проверяем:**
- Ключ `error` в ответе
- Ключ `details` для валидации
- Формат 401 (`detail` от DRF)

---

## Адаптация под приложение

### Замена плейсхолдеров

```
<Model>         → Product, Category, User (единственное число)
<Models>        → Products, Categories, Users (множественное число)
<model>         → product, category, user (lowercase)
<models>        → products, categories, users (lowercase plural)
<field>         → img, category, status (конкретное поле)
```

### Добавление специфичных тестов

Если приложение имеет уникальную логику:

```python
class Test<Model>SpecificLogic:
    def test_<specific_scenario_1>(self, ...)
    def test_<specific_scenario_2>(self, ...)
```

---

**Итого:** 18 классов тестов, 100+ тестов для полного покрытия.
