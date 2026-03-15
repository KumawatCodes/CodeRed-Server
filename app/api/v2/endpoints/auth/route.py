from fastapi import APIRouter ,HTTPException, Depends, Response,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import RegisterRequest, AuthResponse, LoginRequest
from app.core.exceptions import (
    UserEmailAlreadyExists, 
    TokenNotCreated,
    UserEmailNotFound,
    WrongPassword)
from app.new_services.auth_service import AuthService


router = APIRouter()

@router.post("/register_user",response_model=AuthResponse)
async def register_user(
    register_data: RegisterRequest,
    response: Response,
    db: AsyncSession= Depends(get_db),
):
    """
    register new user wiht email and password
    Args:
        email: email of user
        password: password of user
    Return:
        response+ + token
    """
    try:
        # creating new user
        new_user = await AuthService.register_user(db,register_data)
        # getting token
        tokens = AuthService.create_user_tokens(new_user.user_id)

        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60*60*24
        )
        return AuthResponse(
            access_token= tokens["access_token"],
            token_type= tokens["token_type"],
            user_id = new_user.user_id,
            profile_complete=False,
            message= "new user registered successfully."
        )
    
    except UserEmailAlreadyExists:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "email already exists!"
        )
    
    except TokenNotCreated:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "token has not been generated!"
        )


@router.post("/login",response_model=AuthResponse)
async def login_user(
    login_data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    login user with email and password
    Args:
        email: email of user
        password: password of user
    Return:
        response + token
    """
    try:
        user = await AuthService.login_user(db,login_data)

        tokens = AuthService.create_user_tokens(user.user_id)

        response.set_cookie(
            key= "access_token",
            value= tokens["access_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60*60*24
        )
        return AuthResponse(
            access_token= tokens["access_token"],
            token_type= tokens["token_type"],
            user_id = user.user_id,
            profile_complete=user.profile_complete,
            message= "user logined successfully."
        )
    except UserEmailNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "user doesn't exists"
        )
    
    except WrongPassword:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="wrong password"
        )

        

        