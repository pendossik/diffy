import pytest
from catalog.repositories import CharacteristicTemplateRepository
from infrastructure.exceptions import ObjectNotFoundError


class TestCharacteristicTemplateRepository:
    @pytest.mark.django_db
    def test_get_all_returns_templates(self, characteristic_template):
        result = CharacteristicTemplateRepository().get_all()
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.django_db
    def test_get_all_with_group_filter(self, characteristic_template):
        result = CharacteristicTemplateRepository().get_all(group_id=characteristic_template.group_id)
        assert len(result) == 1

    @pytest.mark.django_db
    def test_get_all_paginated(self, characteristic_template):
        result = CharacteristicTemplateRepository().get_all_paginated(page=1, page_size=10)
        assert result.total == 1

    @pytest.mark.django_db
    def test_get_by_id(self, characteristic_template):
        result = CharacteristicTemplateRepository().get_by_id(characteristic_template.id)
        assert result['name'] == 'CPU'

    @pytest.mark.django_db
    def test_get_by_id_not_found(self):
        with pytest.raises(ObjectNotFoundError):
            CharacteristicTemplateRepository().get_by_id(99999)

    @pytest.mark.django_db
    def test_create(self, characteristic_group):
        result = CharacteristicTemplateRepository().create(
            name='RAM',
            group_id=characteristic_group.id
        )
        assert result['name'] == 'RAM'

    @pytest.mark.django_db
    def test_update(self, characteristic_template):
        result = CharacteristicTemplateRepository().update(characteristic_template.id, name='Updated')
        assert result['name'] == 'Updated'

    @pytest.mark.django_db
    def test_delete(self, characteristic_template):
        result = CharacteristicTemplateRepository().delete(characteristic_template.id)
        assert result is True