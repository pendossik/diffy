from accounts.models.user import User
from django.utils.crypto import get_random_string
import logging

logger = logging.getLogger('accounts')

class AdminService:
    @staticmethod
    def toggle_user_block(admin_user: User, target_user_id: int) -> dict:
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            raise ValueError("Пользователь не найден.")

        if target_user.is_superuser:
            raise ValueError("Невозможно заблокировать суперпользователя.")
        if target_user == admin_user:
            raise ValueError("Вы не можете заблокировать сами себя.")

        target_user.is_active = not target_user.is_active
        target_user.save()
        
        status_text = "разблокирован" if target_user.is_active else "заблокирован"
        logger.info(f"Админ {admin_user.email} {status_text} пользователя {target_user.email}.")
        
        return {
            "message": f"Пользователь {target_user.email} был {status_text}.",
            "is_active": target_user.is_active
        }

    @staticmethod
    def force_password_reset(admin_user: User, target_user_id: int, new_password: str = None) -> dict:
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            raise ValueError("Пользователь не найден.")

        if target_user.is_superuser and not admin_user.is_superuser:
            raise ValueError("У вас нет прав менять пароль суперпользователю.")

        if not new_password:
            new_password = get_random_string(length=12)

        target_user.set_password(new_password)
        target_user.save()
        logger.info(f"Админ {admin_user.email} принудительно сменил пароль для {target_user.email}.")

        return {
            "message": f"Пароль для {target_user.email} успешно изменен.",
            "new_password": new_password
        }