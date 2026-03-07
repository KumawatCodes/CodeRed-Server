from fastapi import APIRouter, HTTPException, Depends, status,File, Form, UploadFile,responses
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.new_services.upload_service import UploadServices
from app.new_services.user_service import UserService
from app.core.auth import get_current_user_id,AuthService
from app.schemas.auth import AuthResponse
from app.schemas.user import UserProfileUpdate
from app.core.exceptions import UsernameAlreadyTakenError,UserNotFoundError,InvalidImageTypeError,FileTooLargeError

router = APIRouter()

@router.post("/complete-profile",response_model=AuthResponse)
async def user_complete_profile(
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    bio: str = Form(None),
    preferred_language: str = Form(...),
    profile_picture: UploadFile = File(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    completeting user profile
    """

    try:
        image_url = None

        if profile_picture:
            image_url = await UploadServices.upload_profile_pic(profile_picture)
        
        profile_update = UserProfileUpdate(
            username= username,
            first_name= first_name,
            last_name= last_name,
            date_of_birth= date_of_birth,
            bio= bio,
            preferred_language= preferred_language,
            profile_picture = image_url
        )

        user = await UserService.complete_profile(db,user_id,profile_update)

        tokens = AuthService.create_user_tokens(user_id)

        return AuthResponse(
            access_token= tokens["access_token"],
            token_type= tokens["token_type"],
            user_id = user_id,
            profile_complete= True,
            message= "profile compelete successfully!"
        )
    
    except UserNotFoundError:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "username not found!"
        )
    
    except UsernameAlreadyTakenError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "username already exists!"
        )
    
    except FileTooLargeError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "file is too large!"
        )
    
    except InvalidImageTypeError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "image type is invalid!"
        )