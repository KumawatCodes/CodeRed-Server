from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
# Import Schemas
from app.schemas.submission import CodeRunRequest,CodeSubmitRequest, SubmissionResponse
from app.schemas.user import UserResponse

# Import service
from app.services import submission_service

# Import dependencies 
from app.core.auth import get_current_user_id
from app.database import get_db

router = APIRouter()

# For Run
@router.post(
    "/run",
    summary="Run code with sample input (does not save)"
)
async def run_code(
    run_request: CodeRunRequest,
    db: Session = Depends(get_db)
):
    result = await submission_service.run_code_service(db,run_request)
    if "error" in result:
        raise HTTPException(status_code=500,detail=result)
    return result

# For Submit
@router.post(
    "/submit",
    response_model= SubmissionResponse,
    summary="Create a new code submission"
)
async def submit_code(
    submission_in: CodeSubmitRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> Any:
    """
    Receives code from frontend,send to submission service to be
    executed by Judge0 and returns final result

    - submission_in: The code, language ID, and stdin from the user.
    - current_user: The user data, injected by the auth dependency.
    """

    result = await submission_service.submit_solution_service(
        db=db,
        submission_in=submission_in,
        user_id=user_id
    )

    # Check if the service returned an error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500,detail=result["error"])
    
    # All good!
    return result


@router.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT NOW()"))
    return {"database_time": str(result.scalar_one())}