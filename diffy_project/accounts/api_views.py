from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer


class RegisterAPIView(APIView):
    # этот API не требует входа в систему
    permission_classes = [AllowAny]

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

