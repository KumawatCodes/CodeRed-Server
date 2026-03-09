import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# -- App imports --
from app.models.submission import Submission
from app.models.test_cases import TestCases
from app.schemas.submission import CodeRunRequest, CodeSubmitRequest

# --------------------------
# Piston Configuration
# --------------------------
PISTON_API_URL = "http://20.247.28.65:2000/api/v2/execute"

# If your frontend still uses Judge0 language IDs,
# map them to Piston language names here.
LANGUAGE_MAP: Dict[int, str] = {
    71: "python",      # Python 3
    50: "c",           # C (GCC)
    54: "c++",         # C++ (GCC)
    62: "java",        # Java (OpenJDK)
    63: "javascript",  # Node.js
    # add more if needed
}


def get_piston_language(lang_id: int) -> str:
    """
    Converts frontend language_id to a Piston language string.
    Defaults to python if unknown.
    """
    return LANGUAGE_MAP.get(lang_id, "python")


# --------------------------
# Helper: Execute Single Test Case on Piston
# --------------------------
async def run_piston_job(
    client: httpx.AsyncClient,
    language: str,
    code: str,
    test_case: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """
    Runs a single test case against Piston and returns a normalized result dict.

    Returned dict fields:
        index, status, passed, input, expected, actual, stderr, time, memory, hidden
    """
    stdin_input: str = test_case.get("input", "") or ""
    expected_output: str = (test_case.get("output") or "").strip()
    is_hidden: bool = bool(test_case.get("hidden", False))

    payload = {
        "language": language,
        "version": "*",  # latest version
        "files": [{"content": code}],
        "stdin": stdin_input,
        # Piston run timeout is in milliseconds
        "run_timeout": 3000,  # 3 seconds
    }

    try:
        response = await client.post(PISTON_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        run_stage: Dict[str, Any] = data.get("run", {}) or {}
        compile_stage: Dict[str, Any] = data.get("compile", {}) or {}

        # --------------------------
        # 1. Compilation Error
        # --------------------------
        if compile_stage and compile_stage.get("code", 0) != 0:
            return {
                "index": index,
                "status": "Compilation Error",
                "passed": False,
                "input": stdin_input,
                "expected": expected_output,
                "actual": "",
                "stderr": compile_stage.get("stderr") or compile_stage.get("output", ""),
                "time": float(compile_stage.get("cpu_time") or 0) / 1000.0,
                "memory": int(compile_stage.get("memory") or 0),
                "hidden": is_hidden,
            }

        # --------------------------
        # 2. Runtime / Logic
        # --------------------------
        actual_output: str = (run_stage.get("stdout") or "").strip()
        stderr: str = run_stage.get("stderr") or ""
        exit_code: int = run_stage.get("code", 0)

        time_used = float(run_stage.get("cpu_time") or 0) / 1000.0  # ms → s
        memory_used = int(run_stage.get("memory") or 0)

        status = "Accepted"
        passed = True

        if exit_code != 0:
            status = "Runtime Error"
            passed = False
        elif actual_output != expected_output:
            status = "Wrong Answer"
            passed = False

        return {
            "index": index,
            "status": status,
            "passed": passed,
            "input": stdin_input,
            "expected": expected_output,
            "actual": actual_output,
            "stderr": stderr,
            "time": time_used,
            "memory": memory_used,
            "hidden": is_hidden,
        }

    except Exception as e:
        # System-level error (Piston unreachable, timeout, etc.)
        return {
            "index": index,
            "status": "System Error",
            "passed": False,
            "input": stdin_input,
            "expected": expected_output,
            "actual": "",
            "stderr": str(e),
            "time": 0.0,
            "memory": 0,
            "hidden": is_hidden,
        }


# --------------------------
# 1. RUN SERVICE (Public Only)
# --------------------------
async def run_code_service(db: Session, run_request: CodeRunRequest) -> Dict[str, Any]:
    """
    RUN endpoint:
      - Uses ONLY public test cases (hidden == False)
      - Executes them in parallel on Piston
      - Returns verdict + per-test-case results for frontend
    """
    print(f"[DEBUG] Starting run_code_service for problem {run_request.problem_id}")
    print(f"[DEBUG] Piston URL: {PISTON_API_URL}")
    print(f"Executing 'Run' (Piston) for Problem {run_request.problem_id}")

    # 1. Fetch Test Cases
    query = select(TestCases).where(TestCases.problem_id == run_request.problem_id)
    result = await db.execute(query)
    test_case_record: Optional[TestCases] = result.scalars().first()

    if not test_case_record or not test_case_record.test_cases:
        return {"error": "Test cases not found"}

    all_cases = test_case_record.test_cases
    if isinstance(all_cases, str):
        all_cases = json.loads(all_cases)

    # Filter public only
    public_cases = [tc for tc in all_cases if not tc.get("hidden", False)]
    if not public_cases:
        return {"error": "No public test cases found."}

    language_name = get_piston_language(run_request.language_id)

    print(f"[DEBUG] Found {len(public_cases)} public test cases")
    print(f"[DEBUG] Starting parallel execution...")
    # 2. Run all public cases in parallel
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            run_piston_job(
                client=client,
                language=language_name,
                code=run_request.source_code,
                test_case=case,
                index=i + 1,
            )
            for i, case in enumerate(public_cases)
        ]
        results = await asyncio.gather(*tasks)

    # 3. Aggregate results for frontend
    formatted_results: List[Dict[str, Any]] = []
    final_verdict = "Accepted"

    for res in results:
        status = res["status"]
        if not res["passed"]:
            # Verdict priority for RUN:
            # Compilation Error > Runtime Error > Wrong Answer > System Error
            if final_verdict == "Accepted":
                final_verdict = status
            elif final_verdict == "Wrong Answer" and status in (
                "Runtime Error",
                "Compilation Error",
            ):
                final_verdict = status
            elif final_verdict == "Runtime Error" and status == "Compilation Error":
                final_verdict = status

        formatted_results.append(
            {
                "test_case_index": res["index"],
                "status": status,
                "input": res["input"],
                "expected_output": res["expected"],
                "actual_output": res["actual"],
                "stderr": res["stderr"],
            }
        )

    # If some error but not classified above, fallback to generic
    if final_verdict == "Accepted" and any(not r["passed"] for r in results):
        final_verdict = "Wrong Answer"

    print(f"[DEBUG] Execution complete!")

    return {
        "verdict": final_verdict,
        "total_public_cases": len(public_cases),
        "results": formatted_results,
    }


# --------------------------
# 2. SUBMIT SERVICE (All Cases)
# --------------------------
async def submit_solution_service(
    db: Session, submission_in: CodeSubmitRequest, user_id: int
) -> Submission | Dict[str, Any]:
    """
    SUBMIT endpoint:
      - Uses ALL test cases (public + hidden)
      - Executes them in parallel on Piston
      - Stores a Submission row with final verdict & basic info
      - Returns the Submission instance
    """
    print(f"Executing 'Submit' (Piston) for Problem {submission_in.problem_id}")

    # 1. Fetch all test cases
    query = select(TestCases).where(TestCases.problem_id == submission_in.problem_id)
    result = await db.execute(query)
    test_case_record: Optional[TestCases] = result.scalars().first()

    if not test_case_record or not test_case_record.test_cases:
        return {"error": "Test cases not found"}

    all_cases = test_case_record.test_cases
    if isinstance(all_cases, str):
        all_cases = json.loads(all_cases)

    # 2. Create initial Submission record (Judging)
    new_submission = Submission(
        user_id=user_id,
        language_id=submission_in.language_id,
        source_code=submission_in.source_code,
        problem_id=submission_in.problem_id,
        verdict="Judging",
        total_test_cases=len(all_cases),
        test_cases_passed=0,
    )
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)

    # 3. Execute ALL test cases in parallel
    language_name = get_piston_language(submission_in.language_id)

    async with httpx.AsyncClient(timeout=20.0) as client:
        tasks = [
            run_piston_job(
                client=client,
                language=language_name,
                code=submission_in.source_code,
                test_case=case,
                index=i + 1,
            )
            for i, case in enumerate(all_cases)
        ]
        results = await asyncio.gather(*tasks)

    # 4. Determine final verdict & error message
    final_verdict = "Accepted"
    error_message: Optional[str] = None
    passed_count = 0
    max_time = 0.0
    max_memory = 0

    # Priority: Compilation Error > Runtime Error > Wrong Answer > System Error > Accepted
    def verdict_priority(status: str) -> int:
        order = {
            "Compilation Error": 4,
            "Runtime Error": 3,
            "Wrong Answer": 2,
            "System Error": 1,
            "Accepted": 0,
        }
        return order.get(status, 0)

    worst_result: Optional[Dict[str, Any]] = None

    for i, res in enumerate(results):
        # track time/memory
        max_time = max(max_time, float(res.get("time") or 0.0))
        max_memory = max(max_memory, int(res.get("memory") or 0))

        if res["passed"]:
            passed_count += 1
            continue

        # Compare priority and keep "worst" failure
        if worst_result is None or verdict_priority(res["status"]) > verdict_priority(
            worst_result["status"]
        ):
            worst_result = res

    if worst_result is None:
        # All passed
        final_verdict = "Accepted"
    else:
        status = worst_result["status"]
        final_verdict = status
        is_hidden = bool(worst_result.get("hidden", False))

        if is_hidden:
            error_message = f"{status} on Hidden Test Case"
        else:
            if status == "Compilation Error":
                error_message = worst_result.get("stderr") or "Compilation Error"
            elif status == "Wrong Answer":
                error_message = (
                    f"Test Case {worst_result['index']} Failed. "
                    f"Expected '{worst_result.get('expected')}', "
                    f"but got '{worst_result.get('actual')}'."
                )
            elif status == "Runtime Error":
                error_message = worst_result.get("stderr") or "Runtime Error"
            else:
                error_message = status

    # 5. Update submission in DB
    new_submission.verdict = final_verdict
    new_submission.stderr = error_message
    new_submission.test_cases_passed = passed_count

    # These fields may or may not exist in your model; if they do, we set them.
    if hasattr(new_submission, "execution_time"):
        new_submission.execution_time = max_time
    if hasattr(new_submission, "memory_used"):
        new_submission.memory_used = max_memory

    await db.commit()
    await db.refresh(new_submission)
    return new_submission
