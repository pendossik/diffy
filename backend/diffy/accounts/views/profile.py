from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from accounts.serializers.profile import ProfileSerializer, UserSerializer, ChangeUsernameSerializer
from accounts.services.profile import ProfileService

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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        data = ProfileService.get_user_profile(request.user)
        return Response(data, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Данные текущего пользователя",
        description="Возвращает профиль авторизованного пользователя",
        responses={200: UserSerializer},
        tags=['Авторизация']
    )
    def get(self, request):
        # Делегируем в сервис получение данных
        data = ProfileService.get_user_profile(request.user)
        return Response(data, status=status.HTTP_200_OK)


class ChangeUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Смена username",
        tags=['Авторизация'],
        request=ChangeUsernameSerializer,
        responses={
            200: inline_serializer(name='ChangeUsernameSuccess', fields={
                'message': serializers.CharField(), 
                'user': UserSerializer()
            })
        }
    )
    def post(self, request):
        serializer = ChangeUsernameSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Вся логика сохранения в сервисе
                user = ProfileService.change_username(
                    request.user, 
                    serializer.validated_data['new_username']
                )
                return Response({
                    "message": "Username успешно изменен.",
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"new_username": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Удаление аккаунта",
        description="Полностью удаляет профиль авторизованного пользователя из БД.",
        tags=['Авторизация'],
        responses={200: inline_serializer(name='DeleteSuccess', fields={'message': serializers.CharField()})}
    )
    def delete(self, request):
        ProfileService.delete_account(request.user)
        return Response({"message": "Аккаунт успешно удален."}, status=status.HTTP_200_OK)
