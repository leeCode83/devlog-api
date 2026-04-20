from supabase import Client

from app.database.models.user import UserResponse


class AuthRepository:
    def __init__(self, client: Client):
        self._client = client

    def sign_up(self, email: str, password: str) -> dict:
        response = self._client.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )
        return response

    def sign_in(self, email: str, password: str) -> dict:
        response = self._client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        return response

    def sign_out(self, token: str) -> None:
        self._client.auth.sign_out(token)

    def get_user(self, token: str) -> UserResponse:
        response = self._client.auth.get_user(token)
        user = response.user
        return UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
        )