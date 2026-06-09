from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema, inline_serializer

from ..serializers.auth_serializers import EmailTokenObtainPairSerializer
from ..services.auth_service import AuthService


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Выход (Blacklist токена)",
        tags=['Авторизация'],
        request=inline_serializer(
            name='LogoutRequest',
            fields={'refresh': serializers.CharField()}
        ),
        responses={204: None}
    )
    def post(self, request):
        try:
            AuthService.blacklist_refresh_token(request.data['refresh'])
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
