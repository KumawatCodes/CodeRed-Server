from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.submission import CodeRunRequest,CodeSubmitRequest, SubmissionResponse
from app.schemas.execution import RunCodeResponse
from app.core.exceptions import NoLanguageFound, FailedPistonExecution, UserNotFoundError
from app.core.auth import get_current_user_id
from app.new_services.user_service import UserService
from app.new_services.execution_service import CodeExecutionService 

router = APIRouter()

@router.post("/run",response_model=RunCodeResponse)
async def run_code(
    run_request: CodeRunRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    run code for non-hidden test cases
    Args:
        db: asyncsession,
        run_request:
        code,problem_id,language_id
    Returns:
        RunCodeResponse:
            verdict,
            totat_public_cases,
            results: list[ExecutionResult]
    """
    try:
        user = await UserService.get_user_by_id(db,user_id)

        result = await CodeExecutionService.run_code_service(
            db,run_request
        )

        return result
    except UserNotFoundError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "user not found"
        )
    except NoLanguageFound:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "language doesnt exists"
        )
    except FailedPistonExecution:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Piston execution failed"
        )


@router.post("/submit",response_model=SubmissionResponse)
async def run_code(
    submit_request: CodeSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    submit code for non-hidden  and hidden test cases
    Args:
        db: asyncsession,
        run_request:
        code,problem_id,language_id
    Returns:
        RunCodeResponse:
            verdict,
            totat_public_cases,
            results: list[ExecutionResult]
    """
    try:
        user = await UserService.get_user_by_id(db,user_id)

        result = await CodeExecutionService.submit_code_service(
            db,submit_request,user_id
        )

        return result
    except UserNotFoundError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "user not found"
        )
    except NoLanguageFound:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "language doesnt exists"
        )
    except FailedPistonExecution:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Piston execution failed"
        )