import logging
from sqlalchemy.ext.asyncio import AsyncSession
# import repositories
from app.repositories.user_repo import UserRepo
from app.core.exceptions import UserNotFoundError,UsernameAlreadyTakenError
from app.models.user import User
from app.schemas.user import UserProfileUpdate
logger = logging.getLogger(__name__)

class UserService:
    """ Service for user"""

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        """
        get user by email
        Args:
            db (AsyncSession) = database session
            email (str) = email of user
        Returns:
            User = user info 
        """
        logger.info("fetching user info", extra={
            "email": email
        })

        user = await UserRepo.get_user_by_email(db,email)

        if user is None:
            logger.warning("user doesn't exists")
            raise UserNotFoundError()

        logger.info("successfully fetched user info",extra={
            "information":user
        })
        return user

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) ->User:
        """
        get user by username
        Args:
            db (AsyncSession) = database session
            username (str) = username of user
        Returns:
            User = user info 
        """
        logger.info("fetching user info",extra={
            "username":username
        })

        user = await UserRepo.get_user_by_username(db,username)
        if user is None:
            logger.warning("user doesn't exists")
            raise UserNotFoundError()
        
        logger.info("successfully fetched user info",extra={
            "information":user
        })
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """
        get user by user_id
        Args:
            db (AsyncSession) = database session
            user_id (int) = id of user
        Returns:
            User = user info 
        """
        logger.info("fetching user info",extra={
            "user_id": user_id
        })

        user = await UserRepo.get_user_by_id(db,user_id)
        
        if user is None:
            logger.warning("user doesn't exists")
            raise UserNotFoundError()
        
        logger.info("successfully fetched user info",extra={
            "information":user
        })
        return user

    @staticmethod 
    async def complete_profile(db: AsyncSession, user_id: int,profile_data: UserProfileUpdate) -> User:
        """
        completing user profile
        Args:
            db (AsyncSession) = database session
            user_id (int) = id of user
            profile_data  = user updated data
        Returns:
            User = user info 
        """

        logger.info("updating user profile",extra={
            "user_id": user_id
        })
        
        if profile_data.username:
            existing = await UserRepo.get_user_by_username(db,profile_data.username)
            if existing and existing.user_id != user_id:
                raise UsernameAlreadyTakenError()

        user = await UserRepo.get_user_by_id(db,user_id)

        if not user:
            raise UserNotFoundError()
        
        updates = profile_data.model_dump(exclude_unset=True)

        for field,values in updates.items():
            setattr(user,field,values)
        
        user.profile_complete= True
        await db.commit()
        await db.refresh(user)
        return user

    
        
        
