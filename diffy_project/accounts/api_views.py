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
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser


from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.utils import OpenApiParameter

from rest_framework import serializers

# Для управления паролями
from django.contrib.auth.password_validation import validate_password
from .serializers import ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

from .serializers import ChangeUsernameSerializer

from .serializers import ActivationSerializer
from .serializers import AdminForcePasswordResetSerializer


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

                    activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

                    
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
        request=ActivationSerializer,  # Теперь ждем данные в теле запроса (JSON)
        responses={
            200: inline_serializer(name='ActivationSuccess', fields={'message': serializers.CharField()}),
            400: inline_serializer(name='ActivationError', fields={'error': serializers.CharField()})
        }
    )
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        
        if serializer.is_valid():
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']
            
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
                return Response({"message": "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Неверный или просроченный токен"}, status=status.HTTP_400_BAD_REQUEST)
                
        # Если фронтенд прислал неполные данные
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


# ДЛЯ СМЕНЫ И ВОССТАНОВЛЕНИЯ ПАРОЛЯ
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
            user = request.user
            # Проверяем старый пароль
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Неверный текущий пароль."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Устанавливаем новый пароль
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
            
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
            email = serializer.validated_data['email']
            # Ищем пользователя. Используем .first(), чтобы не упасть, если их почему-то несколько
            user = User.objects.filter(email=email).first()
            
            # В целях безопасности всегда возвращаем 200 OK, даже если email не найден,
            # чтобы злоумышленники не могли перебирать email-ы (Email Enumeration).
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # ССЫЛКА НА ФРОНТЕНД! Фронтенд должен отловить её и показать форму ввода нового пароля
                reset_link = f"{settings.FRONTEND_URL}/password_reset/{uid}/{token}/"
                
                try:
                    send_mail(
                        'Сброс пароля',
                        f'Вы запросили сброс пароля. Для установки нового пароля перейдите по ссылке: {reset_link}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
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
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Пароль успешно сброшен. Теперь вы можете войти."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Ссылка недействительна или устарела."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
            user = request.user
            
            # Просто меняем username и сохраняем
            user.username = serializer.validated_data['new_username']
            user.save()
            
            # Возвращаем успешный ответ с обновленными данными пользователя
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
        # request=... убрали, так как тело запроса пустое
        responses={
            200: inline_serializer(name='DeleteSuccess', fields={'message': serializers.CharField()})
        }
    )
    def delete(self, request):
        # request.user берется из JWT токена
        user = request.user
        
        # Полностью удаляем пользователя из БД (каскадно удалятся и его связи)
        user.delete()
        
        return Response(
            {"message": "Аккаунт успешно удален."}, 
            status=status.HTTP_200_OK
        )


class AdminBlockUserAPIView(APIView):
    """
    Эндпоинт для блокировки/разблокировки пользователя администратором.
    """
    # Доступ только для персонала (is_staff=True)
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
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Защита: нельзя заблокировать суперпользователя или самого себя
        if target_user.is_superuser:
            return Response({"error": "Невозможно заблокировать суперпользователя."}, status=status.HTTP_400_BAD_REQUEST)
        if target_user == request.user:
            return Response({"error": "Вы не можете заблокировать сами себя."}, status=status.HTTP_400_BAD_REQUEST)

        # Переключаем статус (если был активен - блокируем, если был заблокирован - разблокируем)
        target_user.is_active = not target_user.is_active
        target_user.save()

        status_text = "разблокирован" if target_user.is_active else "заблокирован"
        return Response(
            {
                "message": f"Пользователь {target_user.email} был {status_text}.",
                "is_active": target_user.is_active
            }, 
            status=status.HTTP_200_OK
        )


class AdminForcePasswordResetAPIView(APIView):
    """
    Эндпоинт для принудительной смены пароля пользователя администратором.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Принудительная смена пароля (Админ)",
        description="Меняет пароль пользователю. Возвращает новый пароль в ответе, чтобы админ мог передать его юзеру.",
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
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

            if target_user.is_superuser and not request.user.is_superuser:
                return Response({"error": "У вас нет прав менять пароль суперпользователю."}, status=status.HTTP_403_FORBIDDEN)

            # Берем пароль из запроса, либо генерируем надежный случайный длиной 12 символов
            new_password = serializer.validated_data.get('new_password')
            if not new_password:
                new_password = get_random_string(length=12)

            # Устанавливаем новый пароль
            target_user.set_password(new_password)
            target_user.save()

            # Здесь можно было бы добавить отправку письма пользователю
            # send_mail(...)

            return Response(
                {
                    "message": f"Пароль для {target_user.email} успешно изменен.",
                    "new_password": new_password # Возвращаем пароль админу!
                }, 
                status=status.HTTP_200_OK
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)