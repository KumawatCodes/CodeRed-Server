from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate,CodeSubmitRequest,SubmissionResponse
class SubmissionRepo:

    @staticmethod
    async def create_submission(db: AsyncSession, submission_request: CodeSubmitRequest,user_id: int) -> Submission:
        """
        repo for creating new submission
        Args:
            db (AsyncSession): database sessiong
            submission data(SubmissionCreate): submission request
            user_id (int): id of user
        Returns:
            submission info
        """

        new_submission= Submission(
            user_id=user_id,
            verdict= "Judging",
            source_code= submission_request.source_code,
            language_id=  submission_request.language_id,
            problem_id= submission_request.problem_id,
            match_id= submission_request.match_id
        )
        db.add(new_submission)
        await db.commit()
        await db.refresh(new_submission)
        return new_submission

    @staticmethod
    async def update_submission(db: AsyncSession, submission_id:int, updated_submission: SubmissionResponse):
        """
        repo for updating submission
        Args:
            db (AsyncSession): database sessiong
            submission_id(int)
            verdict: str
        Returns:
            submission info
        """

        stmt= update(Submission).where(Submission.submission_id == submission_id).values(
            verdict=updated_submission.verdict,
            error_message = updated_submission.stderr,
            test_cases_passed= updated_submission.test_cases_passed,
            total_test_cases= updated_submission.total_test_cases,
            execution_time = updated_submission.execution_time,
            memory_used = updated_submission.memory_used,
            time_complexity = updated_submission.time_complexity,
            space_complexity = updated_submission.space_complexity,
            )
        await db.execute(stmt)
    
    @staticmethod
    async def get_submission(db: AsyncSession, submission_id:int) -> Submission:
        """
        repo for getting the user by its id
        Args:
            db (AsyncSession): database sessiong
            submission_id(int)
        Returns:
            submission info
        """

        stmt= select(Submission).where(Submission.submission_id == submission_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_submission_by_match_id(db: AsyncSession, user_id: int, match_id: str) -> Submission:
        """
        repo for getting the user by its id
        Args:
            db (AsyncSession): database sessiong
            submission_id(int)
        Returns:
            submission info
        """

        stmt= select(Submission).where(Submission.user_id == user_id and Submission.match_id == match_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()