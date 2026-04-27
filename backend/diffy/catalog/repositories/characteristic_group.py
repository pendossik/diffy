from infrastructure.repositories.django_repository import DjangoRepository
from catalog.models import CharacteristicGroup


class CharacteristicGroupRepository(DjangoRepository):
    model = CharacteristicGroup
    select_related = ['category']
    default_ordering = ['order', 'name']