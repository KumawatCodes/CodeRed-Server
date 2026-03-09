from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime
from .test_cases import TestCasesSampleResponse

# Base Schema: Common fields for a submission
class SubmissionBase(BaseModel):
    """Common fields for a submission"""
    language_id: int
    source_code: str
    problem_id: Optional[int] = None
    match_id: Optional[int] = None

# Create Schema: Data from frontend to create a submission
class SubmissionCreate(BaseModel):
    """Data required to create a new submission"""
    user_id: int
    problem_id: int
    verdict: str
    language_id: int
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    submitted_at: datetime

class SubmissionUpdate(BaseModel):
    """Fields to update after judge0 processing"""
    token: Optional[str] = None
    verdict: Optional[str] = None
    status_id: Optional[int] = None
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None

class CodeRunRequest(BaseModel):
    source_code: str = Field(
        ...,
        min_length=5
    )
    language_id: int
    problem_id: int

class CodeSubmitRequest(BaseModel):
    source_code: str = Field(...,min_length=10)
    language_id: int
    problem_id: int


# Response Schema: Data send Back to frontend
class SubmissionResponse(SubmissionBase):
    """Full submission details sent back to the client"""
    submission_id: int
    user_id: int
    verdict: str
    status_id: Optional[int] = None
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None

    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None

    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None

    submitted_at: datetime
    judged_at: Optional[datetime] = None

    class Config:
        from_attributes = True  #(ALlow pydantic to read the data from the ORM models)

# Simple Response Schema: For lists

class SubmissionSimpleResponse(BaseModel):
    """A lightweight response for lists"""
    submission_id: int
    user_id: int
    problem_id: Optional[int] = None
    verdict: str
    language_id: int
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    submitted_at: datetime

    class Config:
        from_attributes = True