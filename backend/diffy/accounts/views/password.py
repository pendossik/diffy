from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from accounts.serializers.password import ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from accounts.services.password import PasswordService

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Смена пароля", tags=['Авторизация'], request=ChangePasswordSerializer,
        responses={200: inline_serializer(name='ChangePasswordSuccess', fields={'message': serializers.CharField()})})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.change_password(
                    request.user, 
                    serializer.validated_data['old_password'], 
                    serializer.validated_data['new_password']
                )
                return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"old_password": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Запрос на сброс пароля", tags=['Авторизация'], request=PasswordResetRequestSerializer,
        responses={200: inline_serializer(name='ResetRequestSuccess', fields={'message': serializers.CharField()})})
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.request_password_reset(serializer.validated_data['email'])
                return Response(
                    {"message": "Если email существует в нашей системе, на него была отправлена ссылка для сброса пароля."},
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Подтверждение сброса пароля", tags=['Авторизация'], request=PasswordResetConfirmSerializer,
        responses={200: inline_serializer(name='ResetConfirmSuccess', fields={'message': serializers.CharField()})})
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                PasswordService.confirm_password_reset(
                    serializer.validated_data['uidb64'],
                    serializer.validated_data['token'],
                    serializer.validated_data['new_password']
                )
                return Response({"message": "Пароль успешно сброшен. Теперь вы можете войти."}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)