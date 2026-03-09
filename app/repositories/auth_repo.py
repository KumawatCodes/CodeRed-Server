from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.auth import RegisterRequest

class AuthRepo:

    @staticmethod 
    async def register_user(db: AsyncSession,email: str, password_hash: str)->User:
        """
        create new user in db with register data
        Args:
            register_data = email + password
        Returns:
            User data
        """

        new_user = User(
            email = email,
            password_hash = password_hash
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user