from accounts.models.user import User
import logging

logger = logging.getLogger('accounts')

class ProfileService:

    @staticmethod
    def get_user_profile(user: User) -> dict:
        """
        Получить данные профиля пользователя для отображения.
        
        Аргументы:
            user: Аутентифицированный экземпляр User
            
        Возвращает:
            dict: Сериализованная информация профиля
        """
        return {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined
        }

    @staticmethod
    def change_username(user: User, new_username: str) -> User:
            if User.objects.filter(username=new_username).exists():
                raise ValueError("Пользователь с таким username уже существует.")
            user.username = new_username
            user.save()
            logger.info(f"Пользователь {user.email} сменил username на {new_username}.")
            return user

    @staticmethod
    def delete_account(user: User) -> None:
        email = user.email
        user.delete()
        logger.info(f"Аккаунт {email} был удален пользователем.")
