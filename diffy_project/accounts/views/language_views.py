from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..serializers.language_serializers import SetLanguageSerializer
from ..services.language_service import LanguageService


class SetLanguageView(APIView):
    """
    Эндпоинт для установки выбранного языка в cookies.
    Ожидает POST-запрос с телом: {"lang": "en"} или {"lang": "ru"}
    """
    permission_classes = [AllowAny]
    serializer_class = SetLanguageSerializer

    def post(self, request):
        serializer = SetLanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lang = LanguageService.resolve_language(
            request.data.get('lang', settings.LANGUAGE_CODE)
        )
        LanguageService.activate_language(lang)

        response = Response({
            "detail": "Language preferences updated.",
            "current_lang": lang
        })

        response.set_cookie(
            key=settings.LANGUAGE_COOKIE_NAME,
            value=lang,
            max_age=365 * 24 * 60 * 60,         # Время жизни куки в секундах (1 год)
            httponly=False,                     # Фронтенд на React должен иметь доступ к этой куке
            samesite='Lax',                     # Рекомендуемая политика безопасности для кук
            secure=False                        # Установите True в продакшене при работе по HTTPS
        )

        return response
