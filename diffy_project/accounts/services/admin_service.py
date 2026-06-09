from django.contrib.auth.models import User

from rest_framework.exceptions import ValidationError, NotFound


class AdminService:
    @staticmethod
    def toggle_user_block(user_id: int, admin_user: User) -> dict:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound({"error": "Пользователь не найден."})

        if target_user.is_superuser:
            raise ValidationError({"error": "Невозможно заблокировать суперпользователя."})

        if target_user == admin_user:
            raise ValidationError({"error": "Вы не можете заблокировать сами себя."})

        target_user.is_active = not target_user.is_active
        target_user.save()

        status_text = "разблокирован" if target_user.is_active else "заблокирован"
        return {
            "message": f"Пользователь {target_user.email} был {status_text}.",
            "is_active": target_user.is_active,
        }
