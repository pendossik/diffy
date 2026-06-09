from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from drf_spectacular.utils import extend_schema, inline_serializer

from ..serializers.password_serializers import (
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    AdminForcePasswordResetSerializer,
)
from ..services.password_service import PasswordService


class ChangePasswordAPIView(APIView):
    """
    Эндпоинт для смены пароля авторизованным пользователем
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Смена пароля",
        tags=['Авторизация'],
        request=ChangePasswordSerializer,
        responses={200: inline_serializer(name='ChangePasswordSuccess', fields={'message': serializers.CharField()})}
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.change_password(
                    request.user,
                    serializer.validated_data['old_password'],
                    serializer.validated_data['new_password'],
                )
                return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    """
    Эндпоинт для запроса сброса пароля (отправка письма)
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Запрос на сброс пароля",
        description="Отправляет ссылку для сброса на email, если он существует в базе.",
        tags=['Авторизация'],
        request=PasswordResetRequestSerializer,
        responses={200: inline_serializer(name='ResetRequestSuccess', fields={'message': serializers.CharField()})}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.request_password_reset(serializer.validated_data['email'])
            except Exception as e:
                return Response({'error': 'Ошибка отправки письма', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(
                {"message": "Если email существует в нашей системе, на него была отправлена ссылка для сброса пароля."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    """
    Эндпоинт для непосредственной установки нового пароля по токену
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Подтверждение сброса пароля",
        description="Принимает uid, token из ссылки и новый пароль.",
        tags=['Авторизация'],
        request=PasswordResetConfirmSerializer,
        responses={200: inline_serializer(name='ResetConfirmSuccess', fields={'message': serializers.CharField()})}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.confirm_password_reset(
                    serializer.validated_data['uidb64'],
                    serializer.validated_data['token'],
                    serializer.validated_data['new_password'],
                )
                return Response({"message": "Пароль успешно сброшен. Теперь вы можете войти."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminForcePasswordResetAPIView(APIView):
    """
    Эндпоинт для принудительной смены пароля пользователя администратором.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Принудительная смена пароля (Админ)",
        description="Меняет пароль пользователю. Возвращает новый пароль в ответе, чтобы админ мог передать его юзеру. Пустое тело без пароля пока не передавать!",
        tags=['Администрирование'],
        request=AdminForcePasswordResetSerializer,
        responses={
            200: inline_serializer(name='AdminPasswordResetSuccess', fields={
                'message': serializers.CharField(),
                'new_password': serializers.CharField()
            }),
            400: inline_serializer(name='AdminPasswordError', fields={'error': serializers.CharField()}),
            404: inline_serializer(name='AdminPasswordNotFound', fields={'error': serializers.CharField()})
        }
    )
    def post(self, request, user_id):
        serializer = AdminForcePasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            try:
                result = PasswordService.admin_force_password_reset(
                    user_id,
                    request.user,
                    serializer.validated_data.get('new_password'),
                )
                return Response(result, status=status.HTTP_200_OK)
            except NotFound as e:
                return Response(e.detail, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied as e:
                return Response(e.detail, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
