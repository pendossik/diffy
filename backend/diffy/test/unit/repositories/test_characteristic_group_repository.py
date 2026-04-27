import pytest
from catalog.repositories import CharacteristicGroupRepository
from catalog.models import CharacteristicGroup
from infrastructure.exceptions import ObjectNotFoundError


class TestCharacteristicGroupRepository:
    @pytest.mark.django_db
    def test_get_all_returns_groups(self, characteristic_group):
        result = CharacteristicGroupRepository().get_all()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'Specs'

    @pytest.mark.django_db
    def test_get_all_with_category_filter(self, characteristic_group):
        result = CharacteristicGroupRepository().get_all(category_id=characteristic_group.category_id)
        assert len(result) == 1

    @pytest.mark.django_db
    def test_get_all_paginated(self, characteristic_group):
        result = CharacteristicGroupRepository().get_all_paginated(page=1, page_size=10)
        assert result.total == 1

    @pytest.mark.django_db
    def test_get_by_id(self, characteristic_group):
        result = CharacteristicGroupRepository().get_by_id(characteristic_group.id)
        assert result['name'] == 'Specs'

    @pytest.mark.django_db
    def test_get_by_id_not_found(self):
        with pytest.raises(ObjectNotFoundError):
            CharacteristicGroupRepository().get_by_id(99999)

    @pytest.mark.django_db
    def test_create(self, category):
        result = CharacteristicGroupRepository().create(name='New Group', category_id=category.id)
        assert result['name'] == 'New Group'

    @pytest.mark.django_db
    def test_update(self, characteristic_group):
        result = CharacteristicGroupRepository().update(characteristic_group.id, name='Updated Group')
        assert result['name'] == 'Updated Group'

    @pytest.mark.django_db
    def test_delete(self, characteristic_group):
        result = CharacteristicGroupRepository().delete(characteristic_group.id)
        assert result is True