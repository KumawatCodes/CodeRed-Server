import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RegisterRequest
from app.core.security import get_password_hash, create_access_token
from app.models import User
from app.repositories.user_repo import UserRepo
from app.core.exceptions import UserEmailAlreadyExists,TokenNotCreated
from datetime import timedelta
logger = logging.getLogger(__name__)
class AuthService:
    """ authentication services"""

    @staticmethod
    async def register_user(db: AsyncSession,register_data:RegisterRequest)->User:
        """
        create new user in db with register data
        Args:
            register_data = email + password
        Returns:
            User data
        """

        logger.info("fetching register data of user",extra={
            "email ": register_data.email,
            "password:": "********" 
        })

        user = await UserRepo.get_user_by_email(db,register_data.email)

        if user:
            logger.warning("user alreaduy exists")
            raise UserEmailAlreadyExists()

        logger.info("creating new user")
        hashed_password = get_password_hash(register_data.password)

        new_user_data = User(
            email = register_data.email,
            password_hash = hashed_password,
        )
        db.add(new_user_data)
        await db.commit()
        await db.refresh(new_user_data)

        new_user = await UserRepo.get_user_by_email(db,new_user_data.email)
        return new_user

    @staticmethod
    def create_user_tokens(user_id: int) ->dict:
        """
        create JWT tokens for authentication
        Args:
            user_id (int): id of user
        Returns:
            {
                access_token,
                token_type,
                user_id
            }
        """
        logging.info("creating token for user")
        access_token = create_access_token(
            data={"sub":str(user_id)},
            expires_delta=timedelta(minutes=30)
        )
        
        if access_token is None:
            logging.warning("token is not created")
            raise TokenNotCreated()
        
        return {
            "access_token":access_token,
            "token_type": "bearer",
            "user_id": user_id
        }

        


