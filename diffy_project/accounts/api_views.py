from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status#, permission
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        tags=['Авторизация'],
        request=RegisterSerializer,
        responses={201: UserSerializer}
        # responses={201: inline_serializer(
        #     name='RegisterResponse',
        #     fields={
        #         'message': serializers.CharField(),
        #         'user': UserSerializer(),
        #         'tokens': inline_serializer(name='Tokens', fields={
        #             'access': serializers.CharField(),
        #             'refresh': serializers.CharField(),
        #         })
        #     }
        # )}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message':'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
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
    
# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)
#         if user:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({'token' : token.key})
#         return Response({'error' : 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    

#для авторизации по почте, вместо username

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

