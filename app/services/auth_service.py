from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Tuple, Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta


class AuthService:
    """Authentication service handling user registration and login"""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> Tuple[Optional[User], Optional[str]]:
        """Create a new user with validation"""
        try:
            # Check if user already exists
            existing_user = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_user.scalar_one_or_none():
                return None, "Email already registered"

            # Create new user with proper hashing
            hashed_password = get_password_hash(user_data.password)

            user = User(
                username=user_data.username,  # Can be None initially
                email=user_data.email,
                password_hash=hashed_password,
                first_name=user_data.first_name,  # Can be None
                last_name=user_data.last_name,    # Can be None
                date_of_birth=user_data.date_of_birth,  # Can be None
                bio=user_data.bio,  # Can be None
                preferred_language=user_data.preferred_language,  # Can be None
                profile_complete=False  # Profile not complete initially
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return user, None

        except ValueError as e:
            # Password validation errors
            return None, str(e)
        except Exception as e:
            await db.rollback()
            return None, f"Registration failed: {str(e)}"

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if not user or not verify_password(password, user.password_hash):
                return None

            return user

        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    @staticmethod
    def create_user_tokens(user_id: int) -> dict:
        """Create JWT tokens for authenticated user"""
        
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=30),

        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()
