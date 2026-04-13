# Reporting Guide

## Назначение

Руководство по документированию результатов тестирования в README.md.

## Структура отчёта

### 1. Заголовок и статус

```markdown
# Отчёт о тестировании приложения <App>

**Дата:** 2026-03-30
**Статус:** ✅ Все тесты пройдены / ⚠️ Найдены отклонения
**Приложение:** `<app>` (Django REST Framework)
```

---

### 2. Общая статистика

```markdown
## 📊 Общая статистика

| Тип тестов | Файл | Тестов | Пройдено | Статус |
|------------|------|--------|----------|--------|
| **Unit: Services** | `test_services.py` | 45 | 45 (100%) | ✅ |
| **Unit: Views** | `test_views.py` | 53 | 53 (100%) | ✅ |
| **ИТОГО** | | **98** | **98 (100%)** | ✅ |

**Время выполнения:** ~35 секунд (все тесты)
```

---

### 3. Структура тестов

```markdown
## 📁 Структура тестов

```
test/unit/<app>/
├── conftest.py              # Локальные фикстуры
├── test_services.py         # Тесты сервисного слоя (45 тестов)
├── test_views.py            # Тесты API views (53 теста)
└── README.md                # Этот файл
```
```

---

### 4. Покрытие по классам тестов

#### Services

```markdown
## Часть 1: Тесты сервисов (test_services.py)

### Покрытие по классам тестов

| Класс тестов | Тестов | Описание |
|--------------|--------|----------|
| `TestIsAdmin` | 7 | Проверка прав администратора |
| `TestCreate<Model>RaceCondition` | 8-10 | Создание, race condition |
| `TestUpdate<Model>RaceCondition` | 6 | Обновление |
| `TestGet<Models>List` | 8 | Получение списка, поиск |
| `TestGet<Model>Detail` | 2-3 | Получение деталей |
| `TestDelete<Model>` | 3 | Удаление |
| `Test<Model>ServiceEdgeCases` | 8-10 | Граничные случаи |
| `Test<Model>ServiceLogging` | 3 | Логирование |
```

#### Views

```markdown
## Часть 2: Тесты Views (test_views.py)

### Покрытие по классам тестов

| Класс тестов | Тестов | Описание |
|--------------|--------|----------|
| `TestAuthentication` | 5 | Проверка аутентификации |
| `TestUserPermissions` | 5 | Проверка прав доступа |
| `Test<Model>List` | 6 | Список, пагинация |
| `Test<Model>Search` | 8 | Поиск, фильтрация |
| `Test<Model>Create` | 9 | Создание, валидация |
| `Test<Model>Detail` | 4 | Детали |
| `Test<Model>Update` | 7 | Обновление (PUT, PATCH) |
| `Test<Model>Delete` | 3 | Удаление |
| `TestValidationEdgeCases` | 5 | Граничные случаи |
| `TestErrorResponseFormat` | 3 | Формат ошибок |
```

---

### 5. Детализация по уровням критичности

#### CRITICAL

```markdown
## 🔴 CRITICAL: Проверка критических уязвимостей (21 тест)

### Метод `_is_admin()` (7 тестов)
- ✅ `test_admin_user_returns_true` — admin проходит проверку
- ✅ `test_superuser_returns_true` — superuser проходит проверку
- ✅ `test_regular_user_returns_false` — обычный пользователь не проходит
- ✅ `test_inactive_user_returns_false` — неактивный пользователь не проходит
- ✅ `test_none_user_returns_false` — `None` не проходит (защита от CRITICAL #1)
- ✅ `test_anonymous_user_returns_false` — AnonymousUser не проходит
- ✅ `test_user_without_role_attribute` — пользователь без role не проходит

### Метод `create_<model>()` (8-10 тестов)
- ✅ `test_create_unique_name_success` — создание с уникальным именем
- ✅ `test_create_duplicate_name_raises_error` — дубликат отклоняется (CRITICAL #2)
- ✅ `test_create_duplicate_case_insensitive` — дубликат другого регистра отклоняется
- ✅ `test_create_name_too_long_raises_error` — имя >max_length отклоняется (CRITICAL #3)
- ✅ `test_create_empty_name_raises_error` — пустое имя отклоняется (CRITICAL #4)
- ✅ `test_create_whitespace_only_name_raises_error` — имя с пробелами отклоняется
- ✅ `test_create_strips_name` — имя очищается от пробелов
- ✅ `test_create_non_admin_raises_permission_error` — не-админ не может создавать
```

#### HIGH

```markdown
## 🟠 HIGH: Функциональность сервисов (13 тестов)

### Метод `get_<models>_list()` (8 тестов)
- ✅ `test_get_list_empty` — пустой список
- ✅ `test_get_list_returns_all_sorted` — все объекты отсортированы
- ✅ `test_search_by_name_ru` — поиск по русскому названию
- ✅ `test_search_by_name_en` — поиск по английскому названию
- ✅ `test_search_case_insensitive` — поиск регистронезависимый
- ✅ `test_search_empty_string_returns_all` — пустой поиск возвращает всё
- ✅ `test_search_whitespace_only_returns_all` — поиск с пробелами возвращает всё
- ✅ `test_search_with_category_filter` — поиск с фильтрацией по категории

### Метод `get_<model>_detail()` (2-3 теста)
- ✅ `test_get_detail_success` — получение по ID
- ✅ `test_get_detail_with_category` — объект с категорией (select_related)
- ✅ `test_get_detail_nonexistent_id_raises_error` — несуществующий ID

### Метод `delete_<model>()` (3 теста)
- ✅ `test_delete_success` — успешное удаление
- ✅ `test_delete_non_admin_raises_permission_error` — не-админ не может удалять
- ✅ `test_delete_nonexistent_<model>_raises_error` — удаление несуществующего
```

#### MEDIUM

```markdown
## 🟡 MEDIUM: Граничные случаи и логирование (11 тестов)

### Граничные случаи (8 тестов)
- ✅ `test_create_with_special_characters` — спецсимволы в имени
- ✅ `test_create_with_numbers` — цифры в имени
- ✅ `test_update_preserves_id` — ID сохраняется при обновлении
- ✅ `test_delete_returns_bool` — удаление возвращает bool
- ✅ `test_create_<model>_exists_in_db` — объект в БД
- ✅ `test_get_<models>_list_is_queryset` — возвращается QuerySet
- ✅ `test_update_with_same_name_success` — обновление тем же именем
- ✅ `test_create_multiple_<models>_transaction` — создание нескольких

### Логирование (3 теста)
- ✅ `test_create_logs_info_message` — лог создания
- ✅ `test_update_logs_info_message` — лог обновления
- ✅ `test_delete_logs_info_message` — лог удаления
```

---

### 6. Выявленные отклонения

```markdown
## ⚠️ Выявленные отклонения от стандартов

**Все отклонения исправлены в ходе тестирования.**

### Исправлено:

1. **`min_length=2` для поиска** — добавлено в `<Model>SearchSerializer`
2. **`<Model>UpdateSerializer` требует обязательные поля** — все поля сделаны необязательными (`required=False`) для поддержки PATCH запросов

**Теперь PATCH запросы работают корректно:**
```bash
# Обновление только изображения
PATCH /api/<models>/42/
{"img": "products/new-image.jpg"}

# Обновление только имени
PATCH /api/<models>/42/
{"name": "Новое имя"}

# Обновление только категории
PATCH /api/<models>/42/
{"category": 2}
```
```

---

### 7. Используемые фикстуры

```markdown
## 🔧 Используемые фикстуры

### Глобальные фикстуры (test/conftest.py)
| Фикстура | Описание |
|----------|----------|
| `api_client` | APIClient без авторизации |
| `user_factory` | Фабрика пользователей |
| `user` | Обычный пользователь (role='user') |
| `admin` | Администратор (role='admin') |
| `superuser` | Суперпользователь |
| `active_user` | Активный пользователь |
| `inactive_user` | Неактивный пользователь |
| `jwt_user_client` | APIClient с JWT обычного пользователя |
| `jwt_admin_client` | APIClient с JWT администратора |

### Локальные фикстуры (test/unit/<app>/conftest.py)
| Фикстура | Описание |
|----------|----------|
| `cleanup_<models>` | Автоматическая очистка <models> после теста |
| `test_<model>` | Один тестовый объект |
| `many_<models>` | 25 объектов для тестирования пагинации |
| `searchable_<models>` | Объекты с разными названиями для поиска |
| `<models>_in_different_categories` | Объекты в разных категориях для фильтрации |
```

---

### 8. Запуск тестов

```markdown
## 🚀 Запуск тестов

```bash
# Запустить все тесты <app>
python -m pytest test/unit/<app>/ -v

# Запустить только тесты сервисов
python -m pytest test/unit/<app>/test_services.py -v

# Запустить только тесты views
python -m pytest test/unit/<app>/test_views.py -v

# Запустить с покрытием кода
python -m pytest test/unit/<app>/ --cov=<app> --cov-report=html

# Запустить конкретный класс тестов
python -m pytest test/unit/<app>/test_services.py::TestIsAdmin -v

# Запустить один тест
python -m pytest test/unit/<app>/test_services.py::TestIsAdmin::test_admin_user_returns_true -v
```
```

---

### 9. Критерии приёмки

```markdown
## 📋 Критерии приёмки

### Все CRITICAL уязвимости покрыты:
- ✅ Проверка `user.is_authenticated` в `_is_admin()`
- ✅ `select_for_update()` для защиты от race condition
- ✅ Валидация длины имени (max_length)
- ✅ Валидация пустых значений
- ✅ Аутентификация на всех эндпоинтах (401)
- ✅ Проверка прав доступа (403 для не-админов)

### Все HIGH функциональности покрыты:
- ✅ CRUD операции (Create, Read, Update, Delete)
- ✅ Пагинация (page, page_size)
- ✅ Поиск (search по name_ru/name_en)
- ✅ Фильтрация по категории
- ✅ Мультиязычность (name_ru, name_en)
- ✅ Валидация дубликатов
- ✅ Location header при создании

### Все MEDIUM стандарты покрыты:
- ✅ Граничные случаи валидации
- ✅ Формат ответов об ошибках
- ✅ Логирование операций
- ✅ min_length=2 для поиска
```

---

### 10. Сравнение с другими приложениями

```markdown
## 📊 Сравнение с Categories

| Метрика | Categories | <App> |
|---------|------------|-------|
| **Всего тестов** | 98 | ? |
| **Services тестов** | 45 | ? |
| **Views тестов** | 53 | ? |
| **CRITICAL покрыто** | 21 | ? |
| **HIGH покрыто** | 13 | ? |
| **MEDIUM покрыто** | 11 | ? |
| **Отклонений** | 0 | ? |
```

---

### 11. Примечания

```markdown
## 📝 Примечания

1. **Все тесты изолированы** — каждый тест работает со свежей БД
2. **pytest.mark.django_db** — маркер для доступа к БД
3. **django-modeltranslation** — поля `name_ru`/`name_en` создаются динамически
4. **Фикстуры с очисткой** — `cleanup_<models>` автоматически удаляет данные после теста
5. **JWT авторизация** — тесты используют `jwt_admin_client` и `jwt_user_client`
```

---

### 12. Итоговый статус

```markdown
---

**Тестирование проведено успешно!** Все ? тестов пройдены (100% pass rate).

**Покрытие функционала:**
- ✅ Сервисный слой (? тестов)
- ✅ API Views (? тестов)
- ✅ Аутентификация и авторизация
- ✅ CRUD операции
- ✅ Пагинация и поиск
- ✅ Фильтрация по категории
- ✅ Валидация данных
- ✅ Обработка ошибок
- ✅ PATCH запросы (частичное обновление)

**Исправленные отклонения:**
- ✅ `min_length=2` для поиска добавлено
- ✅ `<Model>UpdateSerializer` все поля необязательные для PATCH
```

---

## Шаблон для копирования

Полный шаблон README.md доступен в `test/unit/categories/README.md`.

---

## Чек-лист заполнения отчёта

- [ ] Заголовок и статус
- [ ] Общая статистика (таблица)
- [ ] Структура тестов
- [ ] Покрытие по классам (Services)
- [ ] Покрытие по классам (Views)
- [ ] Детализация CRITICAL/HIGH/MEDIUM
- [ ] Выявленные отклонения
- [ ] Используемые фикстуры
- [ ] Запуск тестов
- [ ] Критерии приёмки
- [ ] Сравнение с другими приложениями
- [ ] Примечания
- [ ] Итоговый статус

---

**Результат:** Полный отчёт о тестировании с документированием всех найденных отклонений.
