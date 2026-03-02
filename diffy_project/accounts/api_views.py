from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status#, permission
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.utils import OpenApiParameter

from rest_framework import serializers


# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]

#     @extend_schema(
#         summary="Регистрация нового пользователя",
#         tags=['Авторизация'],
#         request=RegisterSerializer,
#         responses={201: UserSerializer}
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
            
#             return Response({
#                 'message':'User registered successfully',
#                 'user': UserSerializer(user).data,
#                 'tokens': {
#                     'refresh': str(refresh),
#                     'access': str(refresh.access_token),
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        tags=['Авторизация'],
        request=RegisterSerializer, # Убедись, что это именно класс
        responses={201: UserSerializer},

        description="Поля: username, email, password"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Открываем транзакцию: если внутри блока случится ошибка, 
                # база данных откатится к состоянию "до создания пользователя"
                with transaction.atomic():
                    user = serializer.save()
                    
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    activation_link = f"http://127.0.0.1:8000/api/accounts/activate/{uid}/{token}/"
                    
                    # Пытаемся отправить письмо
                    send_mail(
                        'Подтверждение регистрации',
                        f'Для активации: {activation_link}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False, # Оставляем False, чтобы сработал except
                    )
                
                return Response({'message': 'Success! Check email.'}, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Сюда попадем, если упал send_mail
                # Благодаря transaction.atomic() пользователь в базе НЕ создастся
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
        parameters=[
            OpenApiParameter(name='uidb64', type=str, location=OpenApiParameter.PATH, description="Encoded user ID"),
            OpenApiParameter(name='token', type=str, location=OpenApiParameter.PATH, description="Activation token"),
        ],
        responses={200: inline_serializer(name='Success', fields={'message': serializers.CharField()})}
    )
    def get(self, request, uidb64, token):
        try:
            # Декодируем ID пользователя
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Проверяем токен
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


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
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)

        except KeyError:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

