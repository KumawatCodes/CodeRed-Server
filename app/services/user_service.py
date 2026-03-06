from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import date

from app.models.user import User
from app.schemas.user import UserProfileUpdate  # This import should work now


class UserService:
    """Service for user profile management"""

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_user_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        """Check if email already exists in database"""
        user = await UserService.get_user_by_email(db, email)
        return user is not None

    @staticmethod
    async def check_username_exists(db: AsyncSession, username: str) -> bool:
        """Check if username already exists"""
        user = await UserService.get_user_by_username(db, username)
        return user is not None

    @staticmethod
    async def complete_user_profile(
        db: AsyncSession,
        user_id: int,
        profile_data: UserProfileUpdate
    ) -> Optional[User]:
        """Complete user profile after registration"""
        try:
            # Get user
            result = await db.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Update profile fields
            if profile_data.username:
                user.username = profile_data.username
            if profile_data.first_name:
                user.first_name = profile_data.first_name
            if profile_data.last_name:
                user.last_name = profile_data.last_name
            if profile_data.date_of_birth:
                user.date_of_birth = profile_data.date_of_birth
            if profile_data.bio is not None:
                user.bio = profile_data.bio
            if profile_data.preferred_language:
                user.preferred_language = profile_data.preferred_language
            if profile_data.profile_picture:
                user.profile_picture = profile_data.profile_picture
            # Mark profile as complete
            user.profile_complete = True

            await db.commit()
            await db.refresh(user)
            return user

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: int) -> None:
        """Update user's last login timestamp"""
        from sqlalchemy.sql import func
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.last_login = func.now()
            await db.commit()

    @staticmethod
    async def get_users_paginated(
        db: AsyncSession,
        limit: int,
        cursor: int,
        current_user_id: int
    ):
        stmt = (
            select(User)
            .where(
                and_(
                    User.user_id > cursor,
                    User.user_id != current_user_id
                )
            )
            .order_by(User.user_id)
            .limit(limit)
        )

        result = await db.execute(stmt)
        users = result.scalars().all()

        next_cursor = users[-1].user_id if users else None
        return users, next_cursor