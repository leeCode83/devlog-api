from supabase import Client

from app.database.models.auth import AuthResponse
from app.database.models.user import UserResponse
from app.modules.auth.repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository):
        self._repo = repo

    def register_user(self, email: str, password: str) -> AuthResponse:
        response = self._repo.sign_up(email, password)
        session = response.session
        user = response.user
        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
        )

    def login_user(self, email: str, password: str) -> AuthResponse:
        response = self._repo.sign_in(email, password)
        session = response.session
        user = response.user
        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
        )

    def logout_user(self, token: str) -> bool:
        self._repo.sign_out(token)
        return True

    def get_current_user(self, token: str) -> UserResponse:
        return self._repo.get_user(token)