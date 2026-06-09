from django.utils.translation import activate
from django.conf import settings


class LanguageService:
    @staticmethod
    def resolve_language(lang: str) -> str:
        supported_languages = [code for code, _ in settings.LANGUAGES]
        if lang not in supported_languages:
            return settings.LANGUAGE_CODE
        return lang

    @staticmethod
    def activate_language(lang: str) -> None:
        activate(lang)
