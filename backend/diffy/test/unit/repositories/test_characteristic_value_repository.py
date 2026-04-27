import pytest
from catalog.repositories import CharacteristicValueRepository
from infrastructure.exceptions import ObjectNotFoundError


class TestCharacteristicValueRepository:
    @pytest.mark.django_db
    def test_get_all_returns_values(self, characteristic_value):
        result = CharacteristicValueRepository().get_all()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['value'] == 'Intel i7'

    @pytest.mark.django_db
    def test_get_all_with_product_filter(self, characteristic_value):
        result = CharacteristicValueRepository().get_all(product_id=characteristic_value.product_id)
        assert len(result) == 1

    @pytest.mark.django_db
    def test_get_all_paginated(self, characteristic_value):
        result = CharacteristicValueRepository().get_all_paginated(page=1, page_size=10)
        assert result.total == 1

    @pytest.mark.django_db
    def test_get_by_id(self, characteristic_value):
        result = CharacteristicValueRepository().get_by_id(characteristic_value.id)
        assert result['value'] == 'Intel i7'

    @pytest.mark.django_db
    def test_get_by_id_not_found(self):
        with pytest.raises(ObjectNotFoundError):
            CharacteristicValueRepository().get_by_id(99999)

    @pytest.mark.django_db
    def test_create(self, product, characteristic_template):
        result = CharacteristicValueRepository().create(
            product_id=product.id,
            template_id=characteristic_template.id,
            value='16GB'
        )
        assert result['value'] == '16GB'

    @pytest.mark.django_db
    def test_update(self, characteristic_value):
        result = CharacteristicValueRepository().update(characteristic_value.id, value='AMD Ryzen 7')
        assert result['value'] == 'AMD Ryzen 7'

    @pytest.mark.django_db
    def test_delete(self, characteristic_value):
        result = CharacteristicValueRepository().delete(characteristic_value.id)
        assert result is True