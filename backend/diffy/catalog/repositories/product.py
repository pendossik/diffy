from infrastructure.repositories.django_repository import DjangoRepository
from catalog.models import Product


class ProductRepository(DjangoRepository):
    model = Product
    select_related = ['category']
    default_ordering = ['category__name', 'name']