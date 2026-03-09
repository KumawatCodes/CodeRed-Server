from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate,CodeSubmitRequest
class SubmissionRepo:

    @staticmethod
    async def create_submission(db: AsyncSession, submission_request: CodeSubmitRequest,user_id: int) -> Submission:
        """
        repo for getting the user by its id
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
            problem_id= submission_request.problem_id
        )
