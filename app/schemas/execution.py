from pydantic import BaseModel

class ExecutionResult(BaseModel):
    index: int
    status: str
    passed: bool
    std_input: str
    std_output: str
    actual_output: str
    stderr: str
    exec_time: float
    mem_time: int
    is_hidden: bool

class RunCodeResponse(BaseModel):
    verdict: str
    total_public_cases: int
    results: list[ExecutionResult]
    
    class Config:
        from_attributes = True