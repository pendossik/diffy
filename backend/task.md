# Техническое задание: Разделение монолита на микросервисы

## 1. Текущее состояние

### 1.1 Архитектура монолита

Django-проект `diffy/backend/diffy/` содержит 5 приложений в одном репозитории с общей БД (PostgreSQL):

| Приложение | Путь | Назначение |
|---|---|---|
| `accounts` | `diffy/accounts/` | Аутентификация, регистрация, JWT-токены, профили |
| `categories` | `diffy/categories/` | CRUD категорий (многоязычность: ru/en) |
| `products` | `diffy/products/` | CRUD товаров, привязка к категориям |
| `characteristic` | `diffy/characteristic/` | Группы/шаблоны/значения характеристик товаров |
| `comparisons` | `diffy/comparisons/` | Избранные сравнения товаров |

Все приложения используют единую БД `diffy_db`, общий `settings.py`, единый `manage.py`, единый `urls.py`.

### 1.2 Зависимости от accounts

**Каждое** бизнес-приложение импортирует `from accounts.models import User`:

| Приложение | Файл | Тип зависимости |
|---|---|---|
| `comparisons` | `models.py` | `ForeignKey(User)` — `FavoriteComparison.user` |
| `comparisons` | `services.py` | Type hint `User`, проверка владельца сравнения |
| `categories` | `services.py` | Type hint `User`, `_is_admin()` проверка прав |
| `products` | `services.py` | Type hint `User`, `_is_admin()` проверка прав |
| `characteristic` | `services.py` | Type hint `User`, `_is_admin()` проверка прав |
| `characteristic` | `management/commands/seed_characteristics.py` | Получение суперпользователя для seed-данных |
| `products` | `management/commands/seed_products.py` | Получение суперпользователя для seed-данных |

**Глобальные настройки** (`config/settings.py`):
- `AUTH_USER_MODEL = 'accounts.User'`
- `SIMPLE_JWT` — вся конфигурация JWT (алгоритм, время жизни, blacklist)
- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` → `JWTAuthentication`
- `SPECTACULAR_SETTINGS.ENUM_NAME_OVERRIDES` → `'UserRoleEnum': 'accounts.models.User.ROLE_CHOICES'`

### 1.3 Текущие эндпоинты accounts

| Метод | URL | Permission | Описание |
|---|---|---|---|
| `POST` | `/api/accounts/register/` | AllowAny | Регистрация (email, username, password) |
| `POST` | `/api/accounts/activate/<uid>/<token>/` | AllowAny | Активация аккаунта |
| `POST` | `/api/accounts/login/` | AllowAny | Вход, получение JWT-пары |
| `POST` | `/api/accounts/logout/` | IsAuthenticated | Blacklist refresh-токена |
| `GET` | `/api/accounts/profile/` | IsAuthenticated | Профиль текущего пользователя |

### 1.4 Обнаруженные проблемы

1. **Пустой `admin.py`** — модель User не зарегистрирована в Django admin
2. **`create_super_user` management-команда** не передаёт `username` → конфликт `unique=True`
3. **`BACKEND_URL`/`FRONTEND_URL`** захардкожены в `settings.py` вместо `os.getenv()`
4. **Миграция `0002_user_username`** с `default='default_user'` на уникальном поле — сломается при >1 пользователе

---

## 2. Целевая архитектура

### 2.1 Общая схема

```
diffy/backend/
├── auth-service/              ← вынесенный accounts
│   ├── auth_app/              ← Django-приложение (бывший accounts)
│   ├── config/                ← настройки auth-service
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── diffy-app/                 ← оставшийся монолит бизнес-логики
│   ├── categories/
│   ├── products/
│   ├── characteristic/
│   ├── comparisons/
│   ├── config/                ← настройки diffy-app
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── shared/                    ← общий пакет (типы, утилиты, SDK)
│   ├── jwt_auth.py            ← валидация JWT-токенов
│   ├── user_client.py         ← HTTP-клиент к auth-service
│   └── constants.py           ← ROLE_CHOICES, общие константы
│
├── docker-compose.yml         ← оркестрация всех сервисов
├── nginx/
│   └── nginx.conf             ← API Gateway
└── task.md
```

### 2.2 Схема взаимодействия

```
                    ┌─────────────┐
Frontend ──────────▶│   Nginx     │  API Gateway
  (JWT in header)   │  (Gateway)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │   Auth   │ │  Diffy   │ │   DB     │
       │ Service  │ │   App    │ │PostgreSQL│
       │ :8001    │ │  :8002   │ │  :5432   │
       └────┬─────┘ └────┬─────┘ └──────────┘
            │            │
            │  HTTP      │  Прямое подключение
            │  /verify   │  к СВОЕЙ БД
            │  /userinfo │
            └────────────┘
```

### 2.3 Стратегия разделения БД

**Каждый сервис владеет своей БД.** Прямой доступ к чужой БД запрещён.

| Сервис | БД | Владеет таблицами |
|---|---|---|
| `auth-service` | `auth_db` | `accounts_user` (все поля), `auth_group`, `auth_permission`, `token_blacklist_*` |
| `diffy-app` | `diffy_db` | `categories_category`, `products_product`, `characteristic_*`, `comparisons_favoritecomparison`, M2M-таблицы |

**Проблема ForeignKey:** `comparisons.FavoriteComparison.user → User` — физический FK сломается при разделении БД.

**Решение:** В `diffy-app` заменить `ForeignKey(User)` на `IntegerField(user_id)` с логической ссылкой. Валидация существования пользователя — через HTTP-запрос к `auth-service`.

---

## 3. Миграция accounts → auth-service

### 3.1 Что перенести

| Файл | Действие | Примечание |
|---|---|---|
| `accounts/models.py` | **Полный перенос** | User, UserManager |
| `accounts/managers.py` | **Полный перенос** | create_user, create_superuser |
| `accounts/services.py` | **Полный перенос** | AuthService (register, activate, authenticate, logout, profile) |
| `accounts/views.py` | **Полный перенос** | Все APIView + новые (см. п. 3.3) |
| `accounts/serializers.py` | **Полный перенос** | Все сериализаторы + новые |
| `accounts/urls.py` | **Полный перенос** | + новые маршруты |
| `accounts/admin.py` | **Полный перенос** | Написать полноценный ModelAdmin |
| `accounts/apps.py` | **Полный перенос** | Обновить name |
| `accounts/migrations/` | **Полный перенос** | Все существующие миграции |
| `config/settings.py` (JWT-часть) | **Перенос в auth-service/config/** | `SIMPLE_JWT`, `AUTH_USER_MODEL`, `EMAIL_*` |
| `config/settings.py` (LOGGING accounts) | **Перенос в auth-service** | Логгер `auth_app` |

### 3.2 Новые эндпоинты auth-service

Все под префиксом `/api/accounts/`:

| Метод | URL | Permission | Описание |
|---|---|---|---|
| `POST` | `/api/accounts/register/` | AllowAny | Регистрация (email, username, password) |
| `POST` | `/api/accounts/activate/<uid>/<token>/` | AllowAny | Активация аккаунта |
| `POST` | `/api/accounts/login/` | AllowAny | Вход, JWT-пара |
| `POST` | `/api/accounts/logout/` | IsAuthenticated | Blacklist refresh |
| `GET` | `/api/accounts/profile/` | IsAuthenticated | Профиль текущего |
| `PATCH` | `/api/accounts/username_change/` | IsAuthenticated | Смена username |
| `PATCH` | `/api/accounts/password_change/` | IsAuthenticated | Смена пароля (требует старый пароль) |
| `POST` | `/api/accounts/password_reset/` | AllowAny | Запрос сброса пароля (email → письмо) |
| `POST` | `/api/accounts/password_reset/confirm/<uid>/<token>/` | AllowAny | Подтверждение сброса пароля |
| `DELETE` | `/api/accounts/profile_delete/` | IsAuthenticated | Удаление аккаунта (деактивация + очистка токенов) |
| `POST` | `/api/accounts/admin/users/<int:user_id>/block/` | IsAdminOnly | Заблокировать/разблокировать пользователя |
| `POST` | `/api/accounts/admin/users/<int:user_id>/force_password_reset/` | IsAdminOnly | Принудительный сброс пароля пользователя |
| `GET` | `/api/accounts/admin/users/` | IsAdminOnly | Список всех пользователей (фильтры, пагинация) |
| `GET` | `/api/accounts/admin/users/<int:user_id>/` | IsAdminOnly | Детальная информация о пользователе |
| `PATCH` | `/api/accounts/admin/users/<int:user_id>/role/` | IsAdminOnly | Смена роли пользователя |
| `POST` | `/api/accounts/token/verify/` | AllowAny | Проверка валидности access-токена (для других сервисов) |
| `GET` | `/api/accounts/token/userinfo/` | AllowAny (по токену) | Вернуть данные пользователя по JWT (для других сервисов) |

### 3.3 Новые сервис-методы

Добавить в `AuthService` (файл `services.py`):

| Метод | Описание | Исключения |
|---|---|---|
| `change_username(user: User, new_username: str) -> User` | Смена username текущего пользователя | `ValueError("Username уже занят")` |
| `change_password(user: User, old_password: str, new_password: str) -> bool` | Смена пароля с проверкой старого | `ValueError("Неверный старый пароль")`, `ValueError("Пароль не соответствует требованиям")` |
| `request_password_reset(email: str) -> bool` | Запрос сброса пароля → письмо со ссылкой | Всегда `True` (не раскрывает наличие email) |
| `confirm_password_reset(uid: str, token: str, new_password: str) -> User` | Сброс пароля по токену | `ValueError("Невалидный токен")` |
| `delete_account(user: User) -> bool` | Деактивация + blacklist всех токенов | — |
| `admin_block_user(admin: User, user_id: int, is_blocked: bool) -> User` | Блокировка/разблокировка | `ValueError("Пользователь не найден")` |
| `admin_force_password_reset(admin: User, user_id: int) -> str` | Принудительный сброс → генерация токена | `ValueError("Пользователь не найден")` |
| `admin_list_users(admin: User, search: str, role: str, page: int) -> dict` | Список пользователей с пагинацией | `PermissionError` |
| `admin_change_role(admin: User, user_id: int, role: str) -> User` | Смена роли администратором | `ValueError("Невалидная роль")` |
| `verify_token(token: str) -> dict` | Проверка access-токена (для межсервисного общения) | `ValueError("Токен невалиден")` |
| `get_user_by_token(token: str) -> dict` | Вернуть данные пользователя по токену | `ValueError("Токен невалиден")` |

---

## 4. Изменения в diffy-app (бизнес-приложения)

### 4.1 Убрать прямые импорты User

**Было:**
```python
from accounts.models import User

def _is_admin(user: User) -> bool:
    return user.role in ('admin', 'superuser')
```

**Стало:**
```python
from shared.user_client import UserClient

def _is_admin(user_data: dict) -> bool:
    return user_data.get('role') in ('admin', 'superuser')
```

### 4.2 Замена ForeignKey в comparisons

**Было:**
```python
class FavoriteComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, ...)
```

**Стало:**
```python
class FavoriteComparison(models.Model):
    user_id = models.IntegerField(
        verbose_name="ID пользователя (auth-service)",
        db_index=True,
    )
    # Логическая ссылка. Валидация — через HTTP к auth-service.
```

### 4.3 Межсервисное взаимодействие

`diffy-app` будет обращаться к `auth-service` через HTTP-клиент:

```python
# shared/user_client.py
class UserClient:
    """HTTP-клиент к auth-service для получения данных о пользователях."""

    def __init__(self, base_url: str, secret_key: str):
        self.base_url = base_url
        self.secret_key = secret_key

    def verify_token(self, token: str) -> dict:
        """Проверить JWT-токен. Возвращает {'user_id', 'email', 'role', 'is_active'}."""

    def get_user_info(self, user_id: int) -> dict:
        """Получить информацию о пользователе. Возвращает dict или None."""

    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором."""
```

### 4.4 Аутентификация в diffy-app

JWT-токены проверяются **локально** (без HTTP-запроса к auth-service), т.к. оба сервиса знают `SECRET_KEY` и алгоритм `HS256`:

- `rest_framework_simplejwt.authentication.JWTAuthentication` расшифровывает токен локально
- Для проверки `is_active` / `role` / существования пользователя — запрос к `UserClient`
- Кэшировать результат проверки на 5 минут (Redis или in-memory)

---

## 5. Кастомная аутентификация и permission-классы

### 5.1 SharedJWTAuthentication (для diffy-app)

Класс, который:
1. Расшифровывает JWT локально (известен `SECRET_KEY`)
2. Извлекает `user_id` из payload
3. **Не создаёт** объект User (нет модели User в diffy-app)
4. Передаёт `user_id`, `email`, `role` в `request.user` как `SimpleNamespace` или dataclass

```python
@dataclass
class RemoteUser:
    id: int
    email: str
    role: str
    is_active: bool
```

### 5.2 IsAdminPermission (для diffy-app)

Permission-класс, который проверяет `request.user.role in ('admin', 'superuser')`.

### 5.3 IsOwnerOrAdmin (для comparisons)

Permission-класс: сравнивает `comparison.user_id` с `request.user.id` ИЛИ `request.user.role` в ('admin', 'superuser').

---

## 6. Правила разработки для обоих сервисов

### 6.1 Общие правила

- **Документировать API** через `@extend_schema`, `@extend_schema_field` — полная OpenAPI-спецификация
- **Бизнес-логика** — только в классах `*Service` (файл `services.py`), не во views
- **Error responses** — единый формат: `{"error": "Человекочитаемое сообщение"}`
- **HTTP-статусы** — различать: `400` (валидация), `401` (неавторизован), `403` (нет прав), `404` (не найдено), `409` (конфликт), `422` (межсервисная ошибка), `500` (внутренняя)
- **Docstrings** — Google style для всех методов сервисов
- **Транзакции** — `@transaction.atomic` на методы сервисов, изменяющие данные
- **Логирование** — все ошибки логируются с `logger.error()`, важные операции с `logger.info()`. `propagate: False` в LOGGING

### 6.2 Правила межсервисного взаимодействия

- **Таймаут** HTTP-запросов: 5 секунд
- **Retry** при ошибке: 3 попытки с exponential backoff (1s, 2s, 4s)
- **Circuit breaker** — если auth-service недоступен > 10 секунд, diffy-app переходит в degraded mode (разрешает read-операции, блокирует write)
- **Все межсервисные запросы** — через `shared/user_client.py`, не напрямую через `requests`
- **SECRET_KEY** — одинаковый у обоих сервисов (для локальной верификации JWT)

### 6.3 Правила работы с БД

- **Сервис владеет только своей БД.** Прямые запросы к чужой БД запрещены
- **Миграции** — каждый сервис запускает `manage.py migrate` независимо
- **ForeignKeys** — между сервисами заменяются на `IntegerField` + логическая ссылка
- **CASCADE** — между сервисами реализуется через events/webhooks (в будущем), сейчас — через API-валидацию

### 6.4 Тестирование

- Юнит-тесты сервисов — `test/unit/<app>/test_services.py`
- Юнит-тесты views — `test/unit/<app>/test_views.py`
- Интеграционные тесты — `test/integration/`
- **Моки** для `UserClient` при тестировании diffy-app
- **Покрытие** — не менее 80% для сервис-слоя

---

## 7. Потенциальные проблемы и решения

| # | Проблема | Влияние | Решение |
|---|---|---|---|
| 1 | **Потеря консистентности FK** — `comparisons.user_id` может ссылаться на несуществующего пользователя | Мёртвые записи в избранном | Периодическая очистка (cron) или lazy-валидация при чтении |
| 2 | **Latency** — каждый запрос к diffy-app требует проверки пользователя | Увеличение времени ответа на 5-50ms | Локальная верификация JWT (без HTTP), кэширование user_info |
| 3 | **Auth-service недоступен** — diffy-app не может проверить права | Блокировка write-операций | Circuit breaker + degraded mode (read-only) |
| 4 | **Рассинхрон SECRET_KEY** — JWT нельзя будет проверить | Полная потеря аутентификации | Общий secrets manager или одинаковый .env |
| 5 | **Токен blacklist** — хранится в БД auth-service, diffy-app не может проверить | Возможность использовать заблокированный токен | Diffy-app проверяет только signature + expiry; blacklist — задача auth-service. При logout — отзыв на уровне auth-service |
| 6 | **Миграция существующих данных** — нужно перенести данные из единой БД в две | Риск потери данных | Поэтапная миграция: dual-write → чтение из новой БД → удаление старых данных |
| 7 | **Админ-эндпоинты** — нужны права admin/superuser | Несанкционированный доступ | Permission-класс `IsAdminOnly` на уровне auth-service; для diffy-app — проверка через `UserClient.is_admin()` |
| 8 | **Тесты accounts** — завязаны на модель User в той же БД | Тесты не будут работать в изоляции | Перенести `test/unit/accounts/` в `auth-service/test/`; в diffy-app тесты мокают `UserClient` |

---

## 8. План миграции

### Этап 1: Подготовка (без разделения)
- [ ] Добавить новые эндпоинты в accounts (username_change, password_change, password_reset, profile_delete, admin-эндпоинты)
- [ ] Написать тесты для новых эндпоинтов
- [ ] Заполнить `accounts/admin.py` полноценным ModelAdmin
- [ ] Создать `shared/` пакет с `UserClient` (пока моковый)
- [ ] Заменить `ForeignKey(User)` → `IntegerField(user_id)` в `comparisons/models.py` + миграция
- [ ] Заменить прямые `from accounts.models import User` на `UserClient` во всех бизнес-приложениях

### Этап 2: Выделение auth-service
- [ ] Создать `auth-service/` с собственным `manage.py`, `config/settings.py`, `requirements.txt`
- [ ] Перенести `accounts/` → `auth-service/auth_app/`
- [ ] Настроить отдельную БД `auth_db` для auth-service
- [ ] Настроить JWT с общим `SECRET_KEY`
- [ ] Перенести миграции accounts
- [ ] Написать `Dockerfile` для auth-service

### Этап 3: Выделение diffy-app
- [ ] Создать `diffy-app/` с бизнес-приложениями (categories, products, characteristic, comparisons)
- [ ] Настроить отдельную БД `diffy_db`
- [ ] Убрать `AUTH_USER_MODEL`, заменить на `RemoteUser`
- [ ] Настроить `SharedJWTAuthentication`
- [ ] Написать `Dockerfile` для diffy-app

### Этап 4: Оркестрация
- [ ] Написать `docker-compose.yml` с обоими сервисами + nginx как API Gateway
- [ ] Настроить nginx: `/api/accounts/*` → auth-service, остальные → diffy-app
- [ ] Настроить health-checks
- [ ] Интеграционные тесты между сервисами

### Этап 5: Перенос тестов
- [ ] Перенести `test/unit/accounts/` → `auth-service/test/`
- [ ] В diffy-app создать моки `UserClient` для всех тестов
- [ ] Обновить CI/CD для запуска тестов обоих сервисов

---

## 9. Перенос тестов из test/unit/accounts

Следующие файлы переносятся в `auth-service/test/`:

| Файл | Куда | Что изменить |
|---|---|---|
| `test/unit/accounts/test_models.py` | `auth-service/test/unit/auth_app/test_models.py` | Без изменений |
| `test/unit/accounts/test_services.py` | `auth-service/test/unit/auth_app/test_services.py` | Добавить тесты для новых методов (change_username, change_password, password_reset, delete_account, admin_*) |
| `test/unit/accounts/test_views.py` | `auth-service/test/unit/auth_app/test_views.py` | Добавить тесты для новых эндпоинтов |
| `test/fixtures/accounts_fixtures.py` | `auth-service/test/fixtures/auth_fixtures.py` | Переименовать, добавить фикстуры для новых эндпоинтов |
| `test/integration/test_accounts_integration.py` | `auth-service/test/integration/test_auth_integration.py` | Обновить URL-ы |

**Тесты, которые нужно написать заново:**
- `test_change_username_success` / `test_change_username_duplicate`
- `test_change_password_success` / `test_change_password_wrong_old`
- `test_password_reset_request_sends_email`
- `test_password_reset_confirm_success`
- `test_delete_account_deactivates_and_blacklists_tokens`
- `test_admin_block_user` / `test_admin_unblock_user`
- `test_admin_force_password_reset`
- `test_admin_list_users_pagination`
- `test_admin_change_role`
- `test_token_verify_valid` / `test_token_verify_invalid`
- `test_token_userinfo_returns_user_data`

---

## 10. Спецификация новых API (примеры ответов)

### 10.1 Смена username

```
PATCH /api/accounts/username_change/
Authorization: Bearer <access_token>
{"new_username": "new_name"}

→ 200 {"message": "Username успешно изменён"}
→ 400 {"error": "Username уже занят"}
→ 400 {"error": "Username не должен превышать 150 символов"}
→ 401 {"detail": "Не предоставлены учётные данные"}
```

### 10.2 Смена пароля

```
PATCH /api/accounts/password_change/
Authorization: Bearer <access_token>
{"old_password": "old_pass", "new_password": "new_pass"}

→ 200 {"message": "Пароль успешно изменён"}
→ 400 {"error": "Неверный старый пароль"}
→ 400 {"error": "Пароль не соответствует требованиям безопасности"}
→ 401 {"detail": "Не предоставлены учётные данные"}
```

### 10.3 Сброс пароля (запрос)

```
POST /api/accounts/password_reset/
{"email": "user@example.com"}

→ 200 {"message": "Если аккаунт с таким email существует, письмо отправлено"}
(Всегда 200 — не раскрывает наличие email)
```

### 10.4 Сброс пароля (подтверждение)

```
POST /api/accounts/password_reset/confirm/<uid>/<token>/
{"new_password": "new_pass"}

→ 200 {"message": "Пароль успешно сброшен"}
→ 400 {"error": "Невалидный или истёкший токен"}
```

### 10.5 Удаление аккаунта

```
DELETE /api/accounts/profile_delete/
Authorization: Bearer <access_token>

→ 200 {"message": "Аккаунт удалён"}
→ 401 {"detail": "Не предоставлены учётные данные"}
```

### 10.6 Админ: блокировка пользователя

```
POST /api/accounts/admin/users/<user_id>/block/
Authorization: Bearer <admin_access_token>
{"is_blocked": true}

→ 200 {"message": "Пользователь заблокирован", "user": {"id": 1, "email": "...", "is_active": false}}
→ 403 {"error": "Недостаточно прав"}
→ 404 {"error": "Пользователь не найден"}
```

### 10.7 Межсервисный: проверка токена

```
POST /api/accounts/token/verify/
{"token": "<access_token>"}

→ 200 {"valid": true, "user_id": 1, "email": "...", "role": "user", "is_active": true}
→ 200 {"valid": false}
```

### 10.8 Межсервисный: информация о пользователе

```
GET /api/accounts/token/userinfo/
Authorization: Bearer <access_token>

→ 200 {"user_id": 1, "email": "...", "username": "...", "role": "user", "is_active": true}
→ 401 {"error": "Невалидный токен"}
```
