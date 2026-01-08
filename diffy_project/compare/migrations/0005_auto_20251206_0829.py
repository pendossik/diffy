from django.db import migrations

SMARTPHONE_GROUPS = [
    {
        "title": "Размеры",
        "fields": ["Ширина", "Высота", "Толщина", "Вес"],
    },
    {
        "title": "Корпус",
        "fields": ["Материал задней панели", "Материал граней", "Пыле-влагозащита"],
    },
    {
        "title": "Дисплей",
        "fields": [
            "Тип экрана",
            "Диагональ экрана",
            "Разрешение экрана",
            "Частота экрана",
            "Яркость экрана",
            "Плотность пикселей",
            "Соотношение сторон",
        ],
    },
    {
        "title": "Процессор",
        "fields": ["Модель процессора", "Количество ядер"],
    },
    {
        "title": "Батарея",
        "fields": ["Аккумулятор"],
    },
    {
        "title": "Основная камера",
        "fields": [
            "Количество камер",
            "Количество мегапикселей",
            "Виды задней камеры",
        ],
    },
    {
        "title": "Фронтальная камера",
        "fields": ["Фронтальная камера"],
    },
    {
        "title": "Операционная система",
        "fields": ["Операционная система"],
    },
    {
        "title": "Bluetooth",
        "fields": ["Bluetooth"],
    },
]


def create_groups(apps, schema_editor):
    Category = apps.get_model("compare", "Category")
    CharacteristicGroup = apps.get_model("compare", "CharacteristicGroup")
    CharacteristicTemplate = apps.get_model("compare", "CharacteristicTemplate")

    try:
        category = Category.objects.get(name="Смартфоны")
    except Category.DoesNotExist:
        print("Категория 'Смартфоны' не найдена!")
        return

    order_group = 0
    for group_data in SMARTPHONE_GROUPS:
        group = CharacteristicGroup.objects.create(
            category=category,
            name=group_data["title"],
            order=order_group
        )
        order_group += 1

        order_field = 0
        for field in group_data["fields"]:
            CharacteristicTemplate.objects.create(
                group=group,
                name=field,
                order=order_field
            )
            order_field += 1

class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0004_alter_characteristic_options_characteristictemplate_and_more'),
    ]

    operations = [
        migrations.RunPython(create_groups)
    ]
