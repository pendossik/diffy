from rest_framework import serializers


class SetLanguageSerializer(serializers.Serializer):
    lang = serializers.ChoiceField(
        choices=['ru', 'en'],
        default='en',
        help_text="Код языка ('ru' или 'en')"
    )
