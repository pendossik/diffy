from infrastructure.repositories.django_repository import DjangoRepository
from catalog.models import Category


class CategoryRepository(DjangoRepository):
    model = Category