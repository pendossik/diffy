# 🧪 Структура тестов проекта Diffy

## 📁 Организация

```
test/
├── fixtures/                    # Переиспользуемые фикстуры по приложениям
│   ├── accounts_fixtures.py
│   └── category_fixtures.py
├── unit/                        # Быстрые юнит-тесты
│   ├── accounts/
│   │   ├── test_services.py     # ✅ 85 строк покрыто
│   │   └── test_views.py        # ✅ 86 строк покрыто
│   ├── categories/
│   │   ├── conftest.py
│   │   ├── test_services.py     # ✅ 178 строк покрыто
│   │   └── test_views.py        # ✅ 248 строк покрыто
│   ├── characteristic/
│   │   ├── conftest.py
│   │   ├── test_services.py     # ✅ 224 строк покрыто
│   │   └── test_views.py        # ✅ 334 строк покрыто
│   ├── comparisons/
│   │   ├── conftest.py
│   │   ├── test_services.py     # ✅ 182 строк покрыто
│   │   ├── test_views.py        # ✅ 160 строк покрыто
│   │   └── test_comparison_characteristics.py  # ✅ 74 строк покрыто
│   ├── products/
│   │   ├── conftest.py
│   │   ├── test_services.py     # ✅ 193 строк покрыто
│   │   └── test_views.py        # ✅ 261 строк покрыто
│   └── test_serializer_edge_cases.py  # ✅ 39 новых тестов
└── integration/                 # Медленные интеграционные тесты
    ├── test_accounts_integration.py
    └── test_categories_integration.py
```

## 🚀 Быстрый запуск

### Все тесты (кроме интеграционных)
```bash
pytest test/ -v
```

### Только юнит-тесты accounts
```bash
pytest test/unit/accounts/ -v
```

### Только конкретный компонент
```bash
# Только сервисы
pytest test/unit/accounts/test_services.py -v

# Только представления
pytest test/unit/accounts/test_views.py -v
```

### Интеграционные тесты
```bash
# Все интеграционные
pytest test/integration/ -v -m integration

# Конкретный файл
pytest test/integration/test_accounts_integration.py -v -m integration
```

### С покрытием кода
```bash
# Покрытие для accounts
pytest test/unit/accounts/ --cov=accounts --cov-report=term-missing

# HTML отчёт
pytest test/unit/accounts/ --cov=accounts --cov-report=html
# Откроется в: htmlcov/index.html
```

## 📊 Примеры команд

| Задача | Команда |
|--------|---------|
| **Быстрая проверка перед коммитом** | `pytest test/unit/accounts/test_services.py -v` |
| **Полная проверка accounts** | `pytest test/unit/accounts/ test/integration/test_accounts_integration.py -v` |
| **Проверка с покрытием** | `pytest test/unit/accounts/ --cov=accounts --cov-report=term-missing` |
| **Только интеграционные** | `pytest test/integration/ -m integration -v` |
| **Найти медленные тесты** | `pytest test/ --durations=10` |
| **Один конкретный тест** | `pytest test/unit/accounts/test_services.py::TestRegisterUser::test_register_success -v` |

## 🏷️ Маркеры

- `@pytest.mark.integration` — интеграционные тесты (медленные, с внешними сервисами)
- `@pytest.mark.django_db` — тесты с доступом к БД

## 📝 Правила

1. **Юнит-тесты** (`test/unit/`) — быстрые, изолированные, мокают внешние зависимости
2. **Интеграционные** (`test/integration/`) — проверяют взаимодействие компонентов
3. **Фикстуры** (`test/fixtures/`) — переиспользуемые данные и клиенты
4. **Именование** — `test_*.py`, классы `Test*`, методы `test_*`

## 📊 Текущее покрытие

```
TOTAL: 1817 statements → 96% покрытие (467 тестов прошли)
```

### Покрытие по файлам (с наименьшим):

| Файл | Покрытие | Пропущенные строки |
|------|----------|-------------------|
| `accounts/managers.py` | 95% | 32 |
| `products/serializers.py` | 92% | 100, 119, 145, 185-187, 190-191, 194-195 |
| `characteristic/serializers.py` | 96% | 123, 127, 133, 245, 249, 255, 259, 393, 407 |
| `categories/serializers.py` | 99% | 114 |

---

# 🔍 АУДИТ КОДА — Найденные проблемы и недостающие тесты

> **Дата аудита:** Апрель 2026
> **Аудитор:** Qwen Code
> **Объём:** 5 приложений (accounts, categories, products, characteristic, comparisons)

---

## ✅ FIXED — Исправленные критические баги

### ~~CR-1~~ ✅ FIXED: `User.__str__` — поле `username` добавлено

| | |
|---|---|
| **Статус** | ✅ **ИСПРАВЛЕНО** |
| **Файл** | `accounts/models.py` |
| **Что сделано** | Добавлено поле `username = models.CharField(max_length=150, unique=True)`. `__str__` возвращает `self.username`. |
| **Миграция** | `accounts/migrations/0002_user_username.py` — создана и применена |
| **Тесты** | `test/unit/accounts/test_models.py::TestUserStr::test_str_returns_username` ✅ PASSED<br>`test/unit/accounts/test_models.py::TestUserStr::test_str_with_special_characters` ✅ PASSED |
| **Регистрация** | `RegisterSerializer`, `AuthService.register_user`, `RegisterView` — все принимают `username` |

---

### ~~CR-2~~ ✅ FIXED: `FavoriteComparison.__str__` — `user.username` теперь существует

| | |
|---|---|
| **Статус** | ✅ **ИСПРАВЛЕНО** (как побочный эффект исправления CR-1) |
| **Файл** | `comparisons/models.py`, строка 20 |
| **Что сделано** | После добавления поля `username` в модель `User`, выражение `self.user.username` больше не вызывает `AttributeError`. |
| **Тесты** | `test/unit/comparisons/test_models.py::TestFavoriteComparisonStr::test_str_does_not_raise_error` ✅ PASSED<br>`test/unit/comparisons/test_models.py::TestFavoriteComparisonStr::test_str_returns_username_with_count` ✅ PASSED |

---

### ~~CR-3~~ ✅ FIXED: `products_hash unique=True` — ограничение на уровне пользователя

| | |
|---|---|
| **Статус** | ✅ **ИСПРАВЛЕНО** |
| **Файлы** | `comparisons/models.py`, `comparisons/services.py` |
| **Что сделано** | Убран `unique=True` у `products_hash`. Добавлен `unique_together = ('user', 'products_hash')` в Meta. Теперь разные пользователи могут создавать сравнения с одинаковыми наборами товаров. |
| **Логирование** | При попытке добавить дубликат для **того же** пользователя — warning в логе: `"Попытка добавить дубликат в избранное: пользователь {email}, товары: {ids}"` |
| **Миграция** | `comparisons/migrations/0002_alter_favoritecomparison_products_hash_and_more.py` |
| **Тесты** | `test_different_users_same_products_no_integrity_error` ✅ PASSED<br>`test_different_users_same_products_logs_warning` ✅ PASSED |

---

### ~~CR-4~~ ✅ FIXED: CASCADE удаление — заменено на PROTECT + валидация

| | |
|---|---|
| **Статус** | ✅ **ИСПРАВЛЕНО** |
| **Файлы** | `products/models.py`, `characteristic/models.py`, `categories/services.py` |
| **Что сделано** | `on_delete=CASCADE` → `on_delete=PROTECT` для `Category→Product` и `Category→CharacteristicGroup`. В сервис `delete_category` добавлена pre-delete валидация: если в категории есть товары или группы характеристик — удаление запрещено. |
| **Решение** | Запретить удаление категорий с продуктами. Продукты можно удалять даже при наличии характеристик — это не страшно в нашей системе. |
| **Логирование** | При попытке удалить категорию с продуктами: `"Попытка удалить категорию с продуктами: '{name}' (ID={id}), продуктов: {count}, пользователь: {email}"`. Аналогично для групп характеристик. |
| **Миграции** | `products/migrations/0003_alter_product_category.py`<br>`characteristic/migrations/0003_alter_characteristicgroup_category.py` |
| **Тесты** | `test_delete_category_with_products_raises_error` ✅ PASSED<br>`test_delete_category_with_char_groups_raises_error` ✅ PASSED<br>`test_delete_category_with_products_logs_warning` ✅ PASSED<br>`test_delete_empty_category_success` ✅ PASSED |

---

### ~~CR-5~~ ✅ FIXED: Токен активации — заменён на `default_token_generator`

| | |
|---|---|
| **Статус** | ✅ **ИСПРАВЛЕНО** |
| **Файлы** | `accounts/services.py`, `accounts/views.py`, `accounts/urls.py` |
| **Что сделано** | Вместо `signer.sign(user.id)` (подписанный ID в открытом виде) используется `default_token_generator.make_token(user)` + `urlsafe_base64_encode(user.pk)`. Токен содержит хеш на основе `SECRET_KEY`, pk, timestamp, login state — не раскрывает ID. |
| **Логирование** | При невалидном/истёкшем токене: `"Активация не удалась: невалидный или истёкший токен для пользователя {email}"`. При подборе токенов — логируются все неудачные попытки. |
| **Изменение API** | Эндпоинт активации теперь принимает `<uid>/<token>` вместо单一 `<token>`. URL: `/api/accounts/activate/{uid}/{token}/` |
| **Тесты** | `test_activate_success` ✅ PASSED<br>`test_activate_expired_token` ✅ PASSED<br>`test_activate_invalid_token` ✅ PASSED<br>`test_token_does_not_expose_user_id` ✅ PASSED |

---

## 🟠 HIGH — Высокий приоритет

### H-1: PUT и PATCH работают идентично

| | |
|---|---|
| **Файлы** | `categories/views.py:318-323`, `products/views.py:344-349` |
| **Проблема** | Оба метода вызывают `_handle_update()` с одним сериализатором. По REST-стандартам PUT требует ВСЕ поля (полная замена), PATCH — только указанные. Сейчас PATCH с одним полем работает, но PUT тоже — это нарушение контракта. |
| **Тест** | `test/unit/categories/test_views.py::TestCategoryUpdate::test_put_requires_all_fields` |

---

### H-2: IntegrityError при дублировании comparison между пользователями не обработан

| | |
|---|---|
| **Файл** | `comparisons/services.py`, строка 112 |
| **Проблема** | Связано с CR-3. Когда User B создаёт comparison с теми же products_hash, `IntegrityError` не перехватывается → HTTP 500 вместо 400/409. |
| **Тест** | `test/unit/comparisons/test_views.py::TestCreate::test_duplicate_hash_returns_500` |

---

### H-3: Нет rate limiting на эндпоинтах авторизации

| | |
|---|---|
| **Файлы** | `accounts/views.py`, `config/settings.py` |
| **Проблема** | Login, register, activate — без троттлинга. Брутфорс паролей, спам регистраций, исчерпание email-квот. |
| **Исправление** | Добавить DRF throttling: `throttle_classes = [UserRateThrottle]` |
| **Тест** | `test/unit/accounts/test_views.py::TestRateLimiting::test_login_throttled_after_many_attempts` |

---

### H-4: Уникальность имён CharacteristicGroup — case-sensitive (несогласованно с Category)

| | |
|---|---|
| **Файл** | `characteristic/services.py`, строка 89 |
| **Код** | `filter(category=category, name=name).exists()` |
| **Проблема** | Category использует `name_ru__iexact | name_en__iexact` (case-insensitive). CharacteristicGroup — точное совпадение. "Группа" и "группа" могут сосуществовать в одной категории. |
| **Исправление** | Использовать `name__iexact` или проверку по переводам. |
| **Тест** | `test/unit/characteristic/test_services.py::TestCreateGroup::test_duplicate_case_insensitive` |

---

### H-5: Email failure при регистрации оставляет пользователя навечно неактивным

| | |
|---|---|
| **Файл** | `accounts/services.py`, строки 72-78 |
| **Проблема** | Если `send_mail` падает, пользователь создан, `is_active=False`. Транзакция не откатывается. Нет механизма повторной отправки. Пользователь заблокирован навсегда. |
| **Исправление** | Добавить эндпоинт `POST /api/accounts/resend-activation/` |
| **Тест** | `test/unit/accounts/test_services.py::TestRegister::test_send_mail_failure_leaves_user_inactive` |

---

### H-6: ProductService.create_product не передаёт `name` в конструктор

| | |
|---|---|
| **Файл** | `products/services.py`, строки 120-132 |
| **Проблема** | `name` валидируется для уникальности, но не передаётся в `Product(...)`. Вместо этого вручную устанавливается `product.name` на основе текущей локали. Если `modeltranslation` изменит поведение или локаль неожиданная — `name` будет неправильным. |
| **Тест** | `test/unit/products/test_services.py::TestCreateProduct::test_name_set_for_current_locale` |

---

### H-7: Cross-language product collision detection может пропустить дубликаты

| | |
|---|---|
| **Файл** | `products/services.py`, строки 177-181 |
| **Проблема** | Проверка уникальности: `name_ru__iexact | name_en__iexact`. Но `check_name = name or product.name_ru`. Если `name` предоставлен на `en` локали, а проверяется против `name_ru` существующего продукта — конфликт может быть пропущен. |
| **Тест** | `test/unit/products/test_services.py::TestUpdateProduct::test_cross_language_name_collision` |

---

## 🟡 MEDIUM — Средний приоритет

### M-1: Нет лимита на количество товаров в сравнении (DoS-риск)

| | |
|---|---|
| **Файл** | `comparisons/serializers.py`, строка 63 |
| **Код** | `ListField(..., min_length=2)` — нет `max_length` |
| **Проблема** | Можно запросить сравнение 10,000 товаров → memory/CPU exhaustion. |
| **Исправление** | Добавить `max_length=10` в ListField. |
| **Тест** | `test/unit/comparisons/test_views.py::TestCompare::test_max_products_limit` |

---

### M-2: Сравнение товаров из разных категорий делает бизнес-бессмыслицу

| | |
|---|---|
| **Файл** | `comparisons/services.py`, строки 153-158 |
| **Проблема** | `compare_products_by_characteristics` позволяет сравнивать любые товары. Ноутбук vs телефон → разные группы характеристик → бессмысленный результат. |
| **Исправление** | Добавить валидацию: все товары должны быть из одной категории. |
| **Тест** | `test/unit/comparisons/test_services.py::TestCompare::test_different_categories_rejected` |

---

### M-3: Нет валидации negative/zero product_ids в ComparisonCharacteristicsView

| | |
|---|---|
| **Файл** | `comparisons/views.py`, строки 283-288 |
| **Код** | `product_ids = [int(x) for x in product_ids_param]` |
| **Проблема** | Query params парсятся вручную без валидации. `-1,0` пройдут. Сериализатор `FavoriteComparisonCreateSerializer` имеет `min_value=1`, но этот эндпоинт его не использует. |
| **Тест** | `test/unit/comparisons/test_views.py::TestCompare::test_negative_product_ids_rejected` |

---

### M-4: ProductUpdateSerializer.update молча игнорирует пустое имя

| | |
|---|---|
| **Файл** | `products/serializers.py`, строки 181-186 |
| **Код** | `if name: instance.name = name` |
| **Проблема** | PUT с `name=""` не обновляет имя, но и не возвращает ошибку. Нарушение семантики PUT (полная замена должна требовать валидные данные). |
| **Тест** | `test/unit/products/test_views.py::TestProductUpdate::test_put_empty_name_returns_error` |

---

### M-5: Нет теста на обновление category на несуществующую

| | |
|---|---|
| **Файл** | `products/services.py`, строки 189-193 |
| **Проблема** | `Category.objects.get(pk=category_id)` → `DoesNotExist` → ловится в сервисе как `ValueError` → view возвращает 400. Но нет теста, подтверждающего это. |
| **Тест** | `test/unit/products/test_views.py::TestProductUpdate::test_update_nonexistent_category_returns_400` |

---

### M-6: Race condition в CharacteristicGroupService.create_group

| | |
|---|---|
| **Файл** | `characteristic/services.py`, строка 89 |
| **Проблема** | В отличие от CategoryService и ProductService, characteristic-сервисы НЕ используют `select_for_update()` для проверки уникальности. Два одновременных запроса могут создать дубликаты. |
| **Тест** | `test/unit/characteristic/test_services.py::TestCreateGroup::test_race_condition_duplicate` |

---

### M-7: BACKEND_URL и FRONTEND_URL захардкожены

| | |
|---|---|
| **Файл** | `config/settings.py`, строки 193-194 |
| **Код** | `BACKEND_URL = "http://100.105.194.90"` |
| **Проблема** | IP-адрес захардкожен. Активационные письма всегда будут указывать на этот адрес. Для production это критично. |
| **Исправление** | Читать из `os.environ.get('BACKEND_URL', ...)` |

---

## 🟢 LOW — Низкий приоритет

### L-1: Дублирование `@transaction.atomic` в CategoryService

| | |
|---|---|
| **Файл** | `categories/services.py`, строки 82-84 и 94-102 |
| **Проблема** | Декоратор `@transaction.atomic` + внутренний `with transaction.atomic():` — избыточно. |

---

### L-2: Нет теста на `ProductService.get_products_by_ids` с пустым списком

| | |
|---|---|
| **Файл** | `products/services.py`, строки 204-213 |
| **Тест** | `test/unit/products/test_services.py::TestGetProductsByIds::test_empty_list_returns_none` |

---

## ⚠️ ТЕСТЫ ПРОВЕРЯЮТ НЕПРАВИЛЬНОЕ ПОВЕДЕНИЕ

### WRONG-1: Тест дубликатов принимает и 400, и 409

| | |
|---|---|
| **Файл** | `test/unit/characteristic/test_views.py`, строка 110-116 |
| **Код** | `assert response.status_code in [400, 409]` |
| **Проблема** | Тест проходит при ЛЮБОМ коде ответа. Не гарантирует консистентность API. |
| **Исправление** | Определить один правильный код (рекомендуется 409 Conflict для дубликатов) и assert-ить его. |

---

### WRONG-2: Тест сравнения одинаковых товаров использует fuzzy matching

| | |
|---|---|
| **Файл** | `test/unit/comparisons/test_comparison_characteristics.py`, строки 78-90 |
| **Код** | `'ошибка' in response.data.get('error', '').lower() or 'не найдены' in ...` |
| **Проблема** | Пройдёт практически для ЛЮБОГО error message. Должен проверять конкретную ошибку ("минимум 2"). |
| **Исправление** | `assert 'минимум 2' in response.data['error'].lower()` |

---

### WRONG-3: `test_create_group_without_translations` ожидает `name_en=None`

| | |
|---|---|
| **Файл** | `test/unit/characteristic/test_services.py`, строки 174-181 |
| **Проблема** | Тест документирует непоследовательное поведение: иногда `name_en` копируется из `name`, иногда остаётся `None`. |
| **Исправление** | Либо всегда копировать из `name`, либо явно документировать что `None` допустимо. |

---

## 📋 ПЛАН ДОБАВЛЕНИЯ ТЕСТОВ

### Must Add (CRITICAL/HIGH) — 12 сценариев

| # | Сценарий | Файл теста | Приоритет |
|---|----------|-----------|-----------|
| 1 | `str(User)` возвращает email, не падает | `test/unit/accounts/test_models.py` | 🔴 CR |
| 2 | `str(FavoriteComparison)` не падает | `test/unit/comparisons/test_models.py` | 🔴 CR |
| 3 | Разные пользователи могут создавать одинаковые сравнения | `test/unit/comparisons/test_services.py` | 🔴 CR |
| 4 | CASCADE удаление категории удаляет все продукты | `test/unit/categories/test_services.py` | 🔴 CR |
| 5 | Cross-language name collision detection | `test/unit/products/test_services.py` | 🟠 HIGH |
| 6 | PUT требует все поля, PATCH — нет | `test/unit/categories/test_views.py` | 🟠 HIGH |
| 7 | Failed email → пользователь навечно неактивен | `test/unit/accounts/test_services.py` | 🟠 HIGH |
| 8 | Case-insensitive duplicate для CharacteristicGroup | `test/unit/characteristic/test_services.py` | 🟠 HIGH |
| 9 | Race condition в create_group | `test/unit/characteristic/test_services.py` | 🟠 HIGH |
| 10 | Product name set correctly for current locale | `test/unit/products/test_services.py` | 🟠 HIGH |
| 11 | Rate limiting отсутствует на login | `test/unit/accounts/test_views.py` | 🟠 HIGH |
| 12 | Token activation не раскрывает user ID | `test/unit/accounts/test_services.py` | 🟠 HIGH |

### Should Add (MEDIUM) — 7 сценариев

| # | Сценарий | Файл теста | Приоритет |
|---|----------|-----------|-----------|
| 13 | Max products limit в comparison (DoS) | `test/unit/comparisons/test_views.py` | 🟡 MED |
| 14 | Comparison разных категорий rejected | `test/unit/comparisons/test_services.py` | 🟡 MED |
| 15 | Negative product_ids rejected | `test/unit/comparisons/test_views.py` | 🟡 MED |
| 16 | PUT empty name returns error | `test/unit/products/test_views.py` | 🟡 MED |
| 17 | Update category to nonexistent returns 400 | `test/unit/products/test_views.py` | 🟡 MED |
| 18 | Product update only img/category preserves name | `test/unit/products/test_views.py` | 🟡 MED |
| 19 | BACKEND_URL from environment variable | `test/unit/config/test_settings.py` | 🟡 MED |

### Nice to Have (LOW) — 4 сценария

| # | Сценарий | Файл теста | Приоритет |
|---|----------|-----------|-----------|
| 20 | `get_products_by_ids([])` returns empty | `test/unit/products/test_services.py` | 🟢 LOW |
| 21 | Very long search string | `test/unit/categories/test_services.py` | 🟢 LOW |
| 22 | Nested transaction overhead | `test/unit/categories/test_services.py` | 🟢 LOW |
| 23 | Logging message format consistency | Все сервисы | 🟢 LOW |

---

## 🔧 Исправления кода (не тесты)

Следующие исправления требуются в самом коде, а не в тестах:

| # | Что исправить | Файл | Строка |
|---|---------------|------|--------|
| 1 | `User.__str__` → `return self.email` | `accounts/models.py` | 47 |
| 2 | `FavoriteComparison.__str__` → `self.user.email` | `comparisons/models.py` | 20 |
| 3 | `products_hash unique_together = ('user', 'products_hash')` | `comparisons/models.py` | 14 |
| 4 | Добавить `max_length=10` в ListField | `comparisons/serializers.py` | 63 |
| 5 | `BACKEND_URL` из env variable | `config/settings.py` | 193 |
| 6 | Добавить rate limiting | `accounts/views.py` | все view |
| 7 | Case-insensitive проверка для CharacteristicGroup | `characteristic/services.py` | 89 |

---

*Последнее обновление: Апрель 2026*
