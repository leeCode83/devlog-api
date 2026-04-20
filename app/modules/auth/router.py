from fastapi import APIRouter, Depends, HTTPException

from app.database.models import (
    AuthResponse,
    ErrorResponse,
    SuccessResponse,
    UserResponse,
    SignUpRequest,
    SignInRequest,
)
from app.dependencies import Client, CurrentUserToken
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    client: Client,
) -> AuthService:
    repo = AuthRepository(client)
    return AuthService(repo)


@router.post(
    "/signup",
    response_model=AuthResponse,
    responses={409: {"model": ErrorResponse}},
)
def signup(
    request: SignUpRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.register_user(request.email, request.password)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post(
    "/signin",
    response_model=AuthResponse,
    responses={401: {"model": ErrorResponse}},
)
def signin(
    request: SignInRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login_user(request.email, request.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/signout",
    response_model=SuccessResponse,
    responses={401: {"model": ErrorResponse}},
)
def signout(
    token: CurrentUserToken,
    service: AuthService = Depends(get_auth_service),
):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        service.logout_user(token)
        return SuccessResponse(data={"message": "Successfully signed out"})
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}},
)
def get_me(
    token: CurrentUserToken,
    service: AuthService = Depends(get_auth_service),
):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        return service.get_current_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))