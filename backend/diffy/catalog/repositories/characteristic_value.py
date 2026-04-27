from infrastructure.repositories.django_repository import DjangoRepository
from catalog.models import CharacteristicValue


class CharacteristicValueRepository(DjangoRepository):
    model = CharacteristicValue
    select_related = ['product', 'template__group']
    default_ordering = ['template__group__order', 'template__order']