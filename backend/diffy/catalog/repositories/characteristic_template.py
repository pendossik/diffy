from infrastructure.repositories.django_repository import DjangoRepository
from catalog.models import CharacteristicTemplate


class CharacteristicTemplateRepository(DjangoRepository):
    model = CharacteristicTemplate
    select_related = ['group']
    default_ordering = ['order', 'name']