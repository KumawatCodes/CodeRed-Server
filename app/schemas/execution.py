from pydantic import BaseModel

class ExecutionResult(BaseModel):
    index: int
    status: str
    passed: bool
    input: str
    expected: str
    actual: str
    stderr: str
    time: float
    memory: int
    hidden: bool

class RunCodeResponse(BaseModel):
    verdict: str
    total_public_cases: int
    results: list[ExecutionResult]
    
    class Config:
        from_attributes = True