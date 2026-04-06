"""Глобальные фикстуры и настройки pytest для всего проекта."""
import pytest
import sys
from pathlib import Path
from rest_framework.test import APIClient

# Добавляем корень проекта в sys.path для надёжного импорта фикстур
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически предоставлять доступ к БД для всех тестов."""
    pass


# =============================================================================
# 🔗 Явный импорт фикстур (обход проблемы с pytest_plugins на Windows)
# =============================================================================

# Импортируем фикстуры явно — это гарантирует их регистрацию
from test.fixtures.accounts_fixtures import (  # noqa: F401
    api_client,
    user_factory,
    user,
    admin,
    superuser,
    active_user,
    inactive_user,
    jwt_user_client,
    jwt_admin_client,
    mock_send_mail,
    mock_signer,
    mock_validate_password,
    auth_tokens,
)

from test.fixtures.category_fixtures import (  # noqa: F401
    category,
    categories_batch,
    duplicate_category,
)

# Локальные фикстуры для unit-тестов categories
from test.unit.categories.conftest import (  # noqa: F401
    cleanup_categories,
    many_categories,
    searchable_categories,
)

# Локальные фикстуры для unit-тестов products
from test.unit.products.conftest import (  # noqa: F401
    cleanup_products,
    test_category,
    test_category2,
    test_product,
    many_products,
    searchable_products,
    products_in_different_categories,
)

# Локальные фикстуры для unit-тестов characteristic
from test.unit.characteristic.conftest import (  # noqa: F401
    char_category,
    group,
    template,
    char_product,
    char_value,
)

# Локальные фикстуры для unit-тестов comparisons
from test.unit.comparisons.conftest import (  # noqa: F401
    comparisons_category,
    comparison_products,
    favorite_comparison,
    user_favorite_comparison,
)