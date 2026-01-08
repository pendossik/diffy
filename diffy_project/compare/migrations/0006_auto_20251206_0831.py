from django.db import migrations


def migrate_characteristics(apps, schema_editor):
    OldCharacteristic = apps.get_model("compare", "Characteristic")
    CharacteristicTemplate = apps.get_model("compare", "CharacteristicTemplate")
    CharacteristicValue = apps.get_model("compare", "CharacteristicValue")

    templates = {t.name: t for t in CharacteristicTemplate.objects.all()}

    for old in OldCharacteristic.objects.all():
        template = templates.get(old.name)
        if not template:
            # характеристика не входит в список шаблонов
            continue

        CharacteristicValue.objects.create(
            product_id=old.product_id,
            template=template,
            value=old.value
        )


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0005_auto_20251206_0829'),
    ]

    operations = [
        migrations.RunPython(migrate_characteristics),
    ]
