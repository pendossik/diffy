from rest_framework.exceptions import NotFound

from catalog.models import Product


class ComparisonService:
    @staticmethod
    def compare_products(product_ids: list) -> list:
        products = (
            Product.objects.filter(id__in=product_ids)
            .select_related("category")
            .prefetch_related("characteristic_values__template__group")
        )

        if not products.exists():
            raise NotFound("Товары не найдены")

        result = []
        for product in products:
            groups_map = {}
            for val in product.characteristic_values.all():
                group_name = val.template.group.name
                if group_name not in groups_map:
                    groups_map[group_name] = []

                groups_map[group_name].append({
                    "id": val.id,
                    "name": val.template.name,
                    "value": val.value
                })

            chars_groups = [
                {"name": g_name, "characteristics": chars}
                for g_name, chars in groups_map.items()
            ]

            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category.name,
                "img": product.img,
                "characteristics_groups": chars_groups
            })

        return result
