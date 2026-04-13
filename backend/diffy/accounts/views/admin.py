from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from accounts.services.admin import AdminService
from accounts.serializers.admin import AdminForcePasswordResetSerializer

class AdminBlockUserView(APIView):
    permission_classes = [IsAdminUser] 

    @extend_schema(summary="Блокировка пользователя (Админ)", tags=['Администрирование'],
        responses={200: inline_serializer(name='AdminBlockSuccess', fields={'message': serializers.CharField(), 'is_active': serializers.BooleanField()})})
    def post(self, request, user_id):
        try:
            result = AdminService.toggle_user_block(request.user, user_id)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminForcePasswordResetView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(summary="Принудительная смена пароля (Админ)", tags=['Администрирование'], request=AdminForcePasswordResetSerializer)
    def post(self, request, user_id):
        serializer = AdminForcePasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = AdminService.force_password_reset(
                    request.user, 
                    user_id, 
                    serializer.validated_data.get('new_password')
                )
                return Response(result, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)