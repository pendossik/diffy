from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, inline_serializer

from ..serializers.user_serializers import RegisterSerializer, UserSerializer, ActivationSerializer, ChangeUsernameSerializer
from ..services.user_service import UserService


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        tags=['Авторизация'],
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description="Поля: username, email, password"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                UserService.register_user(serializer.validated_data)
                return Response({'message': 'Success! Check email.'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Ошибка при отправке письма. Регистрация не завершена.',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Активация аккаунта",
        tags=['Авторизация'],
        request=ActivationSerializer,
        responses={
            200: inline_serializer(name='ActivationSuccess', fields={'message': serializers.CharField()}),
            400: inline_serializer(name='ActivationError', fields={'error': serializers.CharField()})
        }
    )
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                UserService.activate_account(
                    serializer.validated_data['uidb64'],
                    serializer.validated_data['token'],
                )
                return Response({"message": "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Данные текущего пользователя",
        description="Возвращает профиль авторизованного пользователя",
        responses={200: UserSerializer},
        tags=['Авторизация']
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangeUsernameAPIView(APIView):
    """
    Эндпоинт для смены имени пользователя (username).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Смена username",
        tags=['Авторизация'],
        request=ChangeUsernameSerializer,
        responses={200: inline_serializer(name='ChangeUsernameSuccess', fields={'message': serializers.CharField(), 'user': UserSerializer()})}
    )
    def post(self, request):
        serializer = ChangeUsernameSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService.change_username(
                request.user,
                serializer.validated_data['new_username'],
            )
            return Response({
                "message": "Username успешно изменен.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountAPIView(APIView):
    """
    Эндпоинт для полного удаления своего аккаунта.
    Пароль не требуется, защита от мисскликов реализована на фронтенде.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Удаление аккаунта",
        description="Полностью удаляет профиль авторизованного пользователя из БД.",
        tags=['Авторизация'],
        responses={
            200: inline_serializer(name='DeleteSuccess', fields={'message': serializers.CharField()})
        }
    )
    def delete(self, request):
        UserService.delete_account(request.user)
        return Response(
            {"message": "Аккаунт успешно удален."},
            status=status.HTTP_200_OK
        )
