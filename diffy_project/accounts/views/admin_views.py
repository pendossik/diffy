from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import NotFound, ValidationError

from drf_spectacular.utils import extend_schema, inline_serializer

from ..services.admin_service import AdminService


class AdminBlockUserAPIView(APIView):
    """
    Эндпоинт для блокировки/разблокировки пользователя администратором.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Блокировка пользователя (Админ)",
        description="Переключает статус is_active у пользователя. Нельзя заблокировать суперюзера.",
        tags=['Администрирование'],
        responses={
            200: inline_serializer(name='AdminBlockSuccess', fields={'message': serializers.CharField(), 'is_active': serializers.BooleanField()}),
            400: inline_serializer(name='AdminBlockError', fields={'error': serializers.CharField()}),
            404: inline_serializer(name='AdminBlockNotFound', fields={'error': serializers.CharField()})
        }
    )
    def post(self, request, user_id):
        try:
            result = AdminService.toggle_user_block(user_id, request.user)
            return Response(result, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response(e.detail, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
