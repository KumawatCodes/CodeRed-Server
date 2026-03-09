from sqlalchemy import select, update,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepo:

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """
        repo for getting the user by its id
        Args:
            db (AsyncSession): database sessiong
            user_id (int): id of user
        Returns:
            user info
        """
        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """
        repo for getting the user by its email
        Args:
            db (AsyncSession): database sessiong
            email (str): email of user
        Returns:
            user info
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        """
        repo for getting the user by its username
        Args:
            db (AsyncSession): database sessiong
            username (str): username of user
        Returns:
            user info
        """
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: int):
        """
        repo for updating the user's last login time
        Args:
            db (AsyncSession): database sessiong
            user_id (int): id of user
        Returns:
            user info
        """
        stmt = update(User).where(User.user_id == user_id).values(last_login= func.now())
        await db.execute(stmt)
    