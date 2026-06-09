from rest_framework_simplejwt.tokens import RefreshToken


class AuthService:
    @staticmethod
    def blacklist_refresh_token(refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        token.blacklist()
