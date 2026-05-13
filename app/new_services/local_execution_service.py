import asyncio
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.new_services.test_cases import TestCaseService
from app.schemas.test_cases import TestCaseItem
from app.schemas.submission import (
    CodeRunRequest, CodeSubmitRequest,
    SubmissionResponse, FinalWinnerRequest, FinalWinnerResponse
)
from app.schemas.execution import ExecutionResult, RunCodeResponse
from app.core.exceptions import NoLanguageFound, FailedPistonExecution
from app.repositories.submission_repo import SubmissionRepo
from app.new_services.code_analyze import CodeAnalyzeService

logger = logging.getLogger(__name__)

LANGUAGE_CONFIG = {
    71: {"image": "python:3.11-slim",             "compile": None,
         "run": "python3 /code/solution.py"},
    63: {"image": "node:20-slim",                 "compile": None,
         "run": "node /code/solution.js"},
    54: {"image": "gcc:13", "compile": "g++ /code/solution.cpp -o /code/out", "run": "/code/out"},
    50: {"image": "gcc:13", "compile": "gcc /code/solution.c -o /code/out",   "run": "/code/out"},
    62: {"image": "eclipse-temurin:17-jdk-alpine","compile": "javac /code/solution.java",
         "run": "java -cp /code solution"},
}

FILE_EXTENSION = {71: "py", 50: "c", 54: "cpp", 62: "java", 63: "js"}

MEMORY_LIMIT = "128m"
CPU_LIMIT    = "0.5"
TIMEOUT_SEC  = 10
PID_LIMIT    = "50"


class LocalCodeExecutionService:

    @staticmethod
    def normalize_output(s: str) -> str:
        if not s:
            return ""
        return s.strip().replace('\r\n', '\n').replace('\r', '\n')

    @staticmethod
    def get_language(lang_id: int) -> dict:
        if lang_id not in LANGUAGE_CONFIG:
            raise NoLanguageFound()
        return LANGUAGE_CONFIG[lang_id]

    @staticmethod
    def log_model(obj, name="Model"):
        if obj is None:
            logger.warning(f"{name} is None")
            return
        data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        logger.info(f"{name}: {data}")

    @staticmethod
    async def _run_all_in_docker(lang_id: int, code: str, test_cases: List[TestCaseItem]) -> List[ExecutionResult]:
        import tempfile, os, time, shutil, subprocess

        config = LocalCodeExecutionService.get_language(lang_id)
        image  = config["image"]
        ext    = FILE_EXTENSION[lang_id]

        tmpdir    = tempfile.mkdtemp(prefix="codered_")
        code_path = os.path.join(tmpdir, f"solution.{ext}")
        with open(code_path, "w") as f:
            f.write(code)

        results = []

        try:
            # Step 1: compile once if needed
            if config["compile"]:
                compile_cmd = [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "-v", f"{tmpdir}:/code",
                    image, "sh", "-c", config["compile"]
                ]
                def do_compile():
                    return subprocess.run(compile_cmd, capture_output=True, timeout=30)

                cp = await asyncio.to_thread(do_compile)
                if cp.returncode != 0:
                    err = cp.stderr.decode(errors="replace")
                    for i, tc in enumerate(test_cases):
                        results.append(ExecutionResult(
                            index=i+1, status="Compilation Error", passed=False,
                            std_input=tc.input, std_output=tc.output,
                            actual_output="", stderr=err,
                            exec_time=0, mem_time=0, is_hidden=tc.hidden
                        ))
                    return results

            # Step 2: run each test case
            for i, tc in enumerate(test_cases):
                stdin_path = os.path.join(tmpdir, "stdin.txt")
                with open(stdin_path, "w") as f:
                    f.write(tc.input)

                run_cmd = [
                    "docker", "run", "--rm",
                    "--memory", MEMORY_LIMIT,
                    "--cpus",   CPU_LIMIT,
                    "--network", "none",
                    "--pids-limit", PID_LIMIT,
                    "-v", f"{tmpdir}:/code",
                    image, "sh", "-c", f"{config['run']} < /code/stdin.txt"
                ]

                start = time.monotonic()

                def do_run():
                    return subprocess.run(run_cmd, capture_output=True, timeout=TIMEOUT_SEC)

                try:
                    rp       = await asyncio.to_thread(do_run)
                    elapsed  = round(time.monotonic() - start, 3)
                    stdout   = LocalCodeExecutionService.normalize_output(rp.stdout.decode(errors="replace"))
                    stderr   = rp.stderr.decode(errors="replace")
                    expected = LocalCodeExecutionService.normalize_output(tc.output)

                    if rp.returncode != 0:
                        status, passed = "Runtime Error", False
                    elif stdout != expected:
                        status, passed = "Wrong Answer", False
                    else:
                        status, passed = "Accepted", True

                except subprocess.TimeoutExpired:
                    elapsed        = TIMEOUT_SEC
                    stdout, stderr = "", ""
                    status, passed = "Time Limit Exceeded", False

                results.append(ExecutionResult(
                    index=i+1, status=status, passed=passed,
                    std_input=tc.input, std_output=tc.output,
                    actual_output=stdout, stderr=stderr,
                    exec_time=elapsed, mem_time=0, is_hidden=tc.hidden
                ))

        except FileNotFoundError:
            logger.error("Docker not found")
            raise FailedPistonExecution()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        return results

    @staticmethod
    def _calculate_run_verdict(results: List[ExecutionResult]) -> str:
        for res in results:
            if not res.passed:
                return res.status
        return "Accepted"

    @staticmethod
    def _calculate_submit_verdict(results: List[ExecutionResult]):
        status, error = "Accepted", ""
        total_run, exec_time, mem_time = 0, 0, 0
        output_mismatch = {}

        for res in results:
            if res.passed:
                total_run += 1
                exec_time += res.exec_time
                mem_time  += res.mem_time
            if res.actual_output != res.std_output and not output_mismatch:
                output_mismatch = {
                    "input": res.std_input,
                    "expected": res.std_output,
                    "actual": res.actual_output
                }
            if not res.passed and error == "":
                status = res.status
                error  = res.stderr

        return status, error, total_run, output_mismatch, exec_time, mem_time

    @staticmethod
    async def run_code_service(db: AsyncSession, run_request: CodeRunRequest) -> RunCodeResponse:
        logger.info("local: run_code_service")
        LocalCodeExecutionService.get_language(run_request.language_id)

        test_cases = await TestCaseService.get_test_cases_by_problem_id(db, run_request.problem_id)
        public     = [TestCaseItem(**tc) for tc in test_cases if not tc.get("hidden", False)]

        results = await LocalCodeExecutionService._run_all_in_docker(
            run_request.language_id, run_request.source_code, public
        )
        verdict = LocalCodeExecutionService._calculate_run_verdict(results)

        return RunCodeResponse(verdict=verdict, total_public_cases=len(public), results=results)

    @staticmethod
    async def submit_code_service(db: AsyncSession, submission_request: CodeSubmitRequest, user_id: int) -> SubmissionResponse:
        logger.info("local: submit_code_service")
        LocalCodeExecutionService.get_language(submission_request.language_id)

        submission_exists = None
        if not submission_request.match_id:
            submission_exists = await SubmissionRepo.get_submission_by_match_id(
                db, user_id, submission_request.match_id
            )
        if not submission_exists:
            new_submission = await SubmissionRepo.create_submission(db, submission_request, user_id)

        test_cases = await TestCaseService.get_test_cases_by_problem_id(db, submission_request.problem_id)
        tc_items   = [TestCaseItem(**tc) for tc in test_cases]

        all_results = await LocalCodeExecutionService._run_all_in_docker(
            submission_request.language_id, submission_request.source_code, tc_items
        )

        # early exit on first failure, skip remaining
        results = []
        for result in all_results:
            results.append(result)
            if not result.passed:
                for j, rem in enumerate(tc_items[result.index:], start=result.index + 1):
                    results.append(ExecutionResult(
                        index=j, status="Skipped", passed=False,
                        std_input=rem.input, std_output=rem.output,
                        actual_output="", stderr="",
                        exec_time=0, mem_time=0, is_hidden=rem.hidden
                    ))
                break

        verdict, error, total_run, output_mismatch, exec_time, mem_time = \
            LocalCodeExecutionService._calculate_submit_verdict(results)

        passed = verdict == "Accepted"
        time_compl = space_compl = None
        if passed:
            time_compl, space_compl = CodeAnalyzeService.analyze(submission_request.source_code)

        updated = SubmissionResponse(
            verdict=verdict, error=error,
            test_cases_passed=total_run, total_test_cases=len(test_cases),
            output_mismatch=output_mismatch,
            execution_time=exec_time, memory_used=mem_time,
            time_complexity=time_compl, space_complexity=space_compl
        )
        await SubmissionRepo.update_submission(db, new_submission.submission_id, updated)
        submission = await SubmissionRepo.get_submission(db, new_submission.submission_id)

        return SubmissionResponse(
            submission_id=submission.submission_id, passed=passed,
            problem_id=submission.problem_id, verdict=verdict,
            execution_time=exec_time, memory_used=mem_time,
            output_mismatch=output_mismatch, stderr=error,
            test_cases_passed=total_run, total_test_cases=len(test_cases),
            time_complexity=time_compl, space_complexity=space_compl
        )

    @staticmethod
    async def winner_declare(db: AsyncSession, winner_request: FinalWinnerRequest) -> FinalWinnerResponse:
        logger.info("declaring winner")

        p1 = await SubmissionRepo.get_submission_by_match_id(db, winner_request.player1_id, winner_request.match_id)
        p2 = await SubmissionRepo.get_submission_by_match_id(db, winner_request.player2_id, winner_request.match_id)

        LocalCodeExecutionService.log_model(p1, "Player1")
        LocalCodeExecutionService.log_model(p2, "Player2")

        if not p1 or not p2:
            raise ValueError("Submission not found")

        if p1.test_cases_passed != p2.test_cases_passed:
            winner = p1.user_id if p1.test_cases_passed > p2.test_cases_passed else p2.user_id
            loser  = p2.user_id if winner == p1.user_id else p1.user_id
            reason = "Winner passed more test cases"
        else:
            winner = p1.user_id if p1.judged_at < p2.judged_at else p2.user_id
            loser  = p2.user_id if winner == p1.user_id else p1.user_id
            reason = f"Winner submitted earlier by {abs(p1.judged_at - p2.judged_at)}"

        r1 = SubmissionResponse.model_validate(p1)
        r2 = SubmissionResponse.model_validate(p2)
        results = [r1, r2] if p1.user_id == winner else [r2, r1]

        return FinalWinnerResponse(results=results, winner_id=winner, losser_id=loser, reason=reason)