from fastapi import APIRouter, Depends, HTTPException, status, Form,UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary.uploader

from app.database import get_db
from app.core.auth import get_current_user_id
from app.services.user_service import UserService
from app.services.auth_service import AuthService

from app.schemas.auth import AuthResponse

from app.schemas.auth import ProfileCompletionRequest, AuthResponse
from app.schemas.user import UserProfileUpdate

from app.schemas.user import UserProfileUpdate, UserResponse
from app.models.user import User
from app.config import settings

router = APIRouter()

@router.post("/complete-profile", response_model=AuthResponse)
async def complete_profile(
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    bio: str = Form(None),
    preferred_language: str = Form(...),
    profile_picture: UploadFile = File(None),
    user_id: User = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Complete user profile after registration"""
    # Check if username is available
    username_exists = await UserService.get_user_by_user_id(db, user_id)
    print(user_id)
    print(username)
    print(username_exists)
    if username_exists and username_exists.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    image_url =None
    print(profile_picture)
    if profile_picture:
        if profile_picture.content_type not in ["image/jpeg","image/png"]:
            raise HTTPException(
                status_code=400,
                detail="Only JPG and PNG images are allowed"
            )
        contents = await profile_picture.read()

        if len(contents) > 5* 1024 *1024:
            raise HTTPException(
                status_code=400,
                detail="Image size must be less than 5MB"
            )

        profile_picture.file.seek(0)

        upload_result = cloudinary.uploader.upload(profile_picture.file)
        image_url = upload_result["secure_url"]

    print(image_url)
    # Convert to UserProfileUpdate schema
    profile_update = UserProfileUpdate(
        username= username,
        first_name= first_name,
        last_name= last_name,
        date_of_birth= date_of_birth,
        bio= bio,
        preferred_language= preferred_language,
        profile_picture = image_url
    )

    # Complete profile
    updated_user = await UserService.complete_user_profile(
        db, user_id, profile_update
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete profile"
        )

    # Generate new tokens with updated user info
    tokens = AuthService.create_user_tokens(updated_user.user_id)

    # Send welcome email
    # await EmailService.send_welcome_email(updated_user.email, updated_user.username)

    return AuthResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        user_id=updated_user.user_id,
        profile_complete=True,
        message="Profile completed successfully!"
    )

@router.get("/me")
async def get_current_user_profile(
    user_id: int = Depends(get_current_user_id),
    response_model = UserResponse,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_user_by_user_id(db,user_id)
    return user