# accounts/views.py
"""API-представления приложения accounts."""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging
from .services import AuthService
from .serializers import (
    RegisterSerializer, LoginSerializer, 
    ActivateSerializer, ProfileSerializer, 
    LogoutRequestSerializer
)

logger = logging.getLogger('accounts')


@extend_schema(
    tags=['Аутентификация'],
    summary='Регистрация нового пользователя',
    description='Создать новый аккаунт пользователя. Отправляет письмо с активацией. '
                'Аккаунт неактивен до подтверждения.',
    request=RegisterSerializer,
    responses={
        201: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    },
    examples=[
        OpenApiExample(
            'Корректная регистрация',
            value={'email': 'user@example.com', 'username': 'john_doe', 'password': 'strongpass123'},
            request_only=True
        )
    ]
)
class RegisterView(APIView):
    """Эндпоинт регистрации пользователя."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                AuthService.register_user(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    username=serializer.validated_data['username']
                )
                logger.info(f"Запрос на регистрацию обработан для {serializer.validated_data['email']}")
                return Response(
                    {"message": "Регистрация успешна. Проверьте почту для активации."}, 
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                logger.warning(f"Ошибка регистрации: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Аутентификация'],
    summary='Активация аккаунта',
    description='Активировать аккаунт по токену из письма. Токен действует 24 часа.',
    parameters=[
        OpenApiParameter(
            name='uid',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='URL-safe base64-encoded ID пользователя',
            required=True
        ),
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Токен активации от default_token_generator',
            required=True
        )
    ],
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
class ActivateView(APIView):
    """Эндпоинт активации аккаунта."""
    permission_classes = [AllowAny]

    def post(self, request, uid: str, token: str):
        try:
            AuthService.activate_account(uid, token)
            return Response(
                {"message": "Аккаунт успешно активирован. Теперь можно войти."},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Аутентификация'],
    summary='Вход пользователя',
    description='Аутентификация по email/паролю с получением пары JWT-токенов.',
    request=LoginSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string'},
                'access': {'type': 'string'},
            }
        },
        401: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    },
)
class LoginView(APIView):
    """Эндпоинт аутентификации пользователя."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tokens = AuthService.authenticate_user(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                return Response(tokens, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Аутентификация'],
    summary='Выход пользователя',
    description='Добавить refresh-токен в чёрный список для завершения сессии. '
                'Требуется валидный refresh-токен.',
    request=LogoutRequestSerializer,
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
class LogoutView(APIView):
    """Эндпоинт выхода пользователя (добавление токена в чёрный список)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = LogoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors.get('refresh', ['Неверный формат'])[0]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Требуется refresh-токен"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            success = AuthService.logout_user(refresh_token)
            if success:
                return Response({"message": "Выход выполнен успешно"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Токен не найден или уже недействителен"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            logger.error(f"Ошибка логаута: {str(e)}")
            return Response(
                    {"error": "Внутренняя ошибка сервера"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Пользователи'],
    summary='Получение профиля пользователя',
    description='Получить информацию профиля аутентифицированного пользователя.',
    responses={
        200: ProfileSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}
    }
)
class ProfileView(APIView):
    """Эндпоинт профиля пользователя."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        data = AuthService.get_user_profile(user)
        return Response(data, status=status.HTTP_200_OK)