import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import get_password_hash, create_access_token, verify_password
from app.models import User
from app.repositories.user_repo import UserRepo
from app.core.exceptions import UserEmailAlreadyExists,TokenNotCreated, UserEmailNotFound, WrongPassword
from app.repositories.auth_repo import AuthRepo
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

        logger.info("registering new user data",extra={
            "email ": register_data.email,
            "password:": "********" 
        })

        user = await UserRepo.get_user_by_email(db,register_data.email)

        if user:
            logger.warning("user alreaduy exists")
            raise UserEmailAlreadyExists()

        logger.info("creating new user")
        hashed_password = get_password_hash(register_data.password)

        new_user= await AuthRepo.register_user(
            db,register_data.email,hashed_password
        )
        return new_user

    @staticmethod
    async def login_user(db: AsyncSession, login_data: LoginRequest) -> User:
        """
        login user in db with login data\n
        Args:
            login_data = email + password
        Returns:
            User data
        """

        logger.info("logging user",extra={
            "email: ": login_data.email,
            "password:": "********" 
        })
        
        user = await UserRepo.get_user_by_email(db,login_data.email)

        if user is None:
            logger.warning("user does not exists")
            raise UserEmailNotFound()
        
        logger.info("cross verifying password")
        
        correct_password = verify_password(login_data.password,user.password_hash)

        if not correct_password:
            logger.warning("incorrect password")
            raise WrongPassword()
        
        await UserRepo.update_last_login(db,user.user_id) # updating last login time
        return user

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

        


