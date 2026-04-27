"""Views приложения catalog."""
from catalog.views.category import CategoryView, CategoryDetailView
from catalog.views.product import ProductView, ProductDetailView
from catalog.views.characteristic_group import CharacteristicGroupView, CharacteristicGroupDetailView
from catalog.views.characteristic_template import CharacteristicTemplateView, CharacteristicTemplateDetailView
from catalog.views.characteristic_value import CharacteristicValueView, CharacteristicValueDetailView

__all__ = [
    'CategoryView',
    'CategoryDetailView',
    'ProductView',
    'ProductDetailView',
    'CharacteristicGroupView',
    'CharacteristicGroupDetailView',
    'CharacteristicTemplateView',
    'CharacteristicTemplateDetailView',
    'CharacteristicValueView',
    'CharacteristicValueDetailView',
]