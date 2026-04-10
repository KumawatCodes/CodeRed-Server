import asyncio
import base64
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.new_services.test_cases import TestCaseService
from app.config import settings
from app.schemas.test_cases import TestCaseItem
from app.schemas.submission import CodeRunRequest, CodeSubmitRequest, SubmissionResponse, FinalWinnerRequest, FinalWinnerResponse
from app.schemas.execution import ExecutionResult, RunCodeResponse
from app.core.exceptions import NoLanguageFound, FailedPistonExecution
from app.repositories.submission_repo import SubmissionRepo
from typing import Dict, List, Any
from app.new_services.code_analyze import CodeAnalyzeService
import logging

logger = logging.getLogger(__name__)

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"
JUDGE0_KEY = settings.JUDGE0_API_KEY

VALID_LANGUAGES = {71, 50, 54, 62, 63}

JUDGE0_HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": JUDGE0_KEY,
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
}

class CodeExecutionService:

    @staticmethod
    def encode(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode(text: str) -> str:
        if not text:
            return ""
        return base64.b64decode(text).decode()

    @staticmethod
    def normalize_output(s: str) -> str:
        if not s:
            return ""
        return s.strip().replace('\r\n', '\n').replace('\r', '\n')

    @staticmethod
    def get_piston_lanuage(lang_id: int) -> int:
        if lang_id not in VALID_LANGUAGES:
            logger.warning("invalid language id")
            raise NoLanguageFound()
        return lang_id

    @staticmethod
    def log_model(obj, name="Model"):
        if obj is None:
            logger.warning(f"{name} is None")
            return
        data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        logger.info(f"{name} data: {data}")

    @staticmethod
    async def run_judge0_request(
        client: httpx.AsyncClient,
        lang_id: int,
        code: str,
        stdin: str
    ) -> Dict:
        payload = {
            "language_id": lang_id,
            "source_code": CodeExecutionService.encode(code),
            "stdin": CodeExecutionService.encode(stdin),
        }
        response = await client.post(
            f"{JUDGE0_URL}/submissions?wait=true&base64_encoded=true",
            json=payload,
            headers=JUDGE0_HEADERS
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            raise FailedPistonExecution()
        return data

    @staticmethod
    async def run_test_case(
        client: httpx.AsyncClient,
        lang_name: int,          # now int (judge0 lang id)
        code: str,
        test_case: TestCaseItem,
        index: int
    ) -> ExecutionResult:
        logger.info(f"running test case {index}")

        data = await CodeExecutionService.run_judge0_request(
            client, lang_name, code, test_case.input
        )

        status_desc = data.get("status", {}).get("description", "")
        stdout = CodeExecutionService.normalize_output(
            CodeExecutionService.decode(data.get("stdout") or "")
        )
        stderr = CodeExecutionService.decode(data.get("stderr") or "")
        compile_output = CodeExecutionService.decode(data.get("compile_output") or "")
        expected = CodeExecutionService.normalize_output(test_case.output)

        if status_desc == "Time Limit Exceeded":
            status, passed = "Time Limit Exceeded", False
        elif status_desc == "Compilation Error":
            status, passed = "Compilation Error", False
            stderr = compile_output or stderr
        elif status_desc in ["Runtime Error (NZEC)", "Runtime Error (SIGSEGV)",
                             "Runtime Error (SIGFPE)", "Runtime Error (SIGABRT)", "Runtime Error"]:
            status, passed = "Runtime Error", False
        elif stdout != expected:
            status, passed = "Wrong Answer", False
        else:
            status, passed = "Accepted", True

        return ExecutionResult(
            index=index,
            status=status,
            passed=passed,
            std_input=test_case.input,
            std_output=test_case.output,
            actual_output=stdout,
            stderr=stderr,
            exec_time=float(data.get("time") or 0),
            mem_time=float(data.get("memory") or 0),
            is_hidden=test_case.hidden
        )

    @staticmethod
    def calculate_run_verdict(results: List[ExecutionResult]) -> str:
        logger.info("judging final run verdict")
        for res in results:
            if not res.passed:
                return res.status
        return "Accepted"

    @staticmethod
    def calculate_submit_verdict(results: List[ExecutionResult]):
        logger.info("judging final submit verdict")
        status = "Accepted"
        error = ""
        total_run = 0
        output_mismatch = {}
        exec_time = 0
        mem_time = 0

        for res in results:
            if res.passed:
                total_run += 1
                exec_time += res.exec_time
                mem_time += res.mem_time
            if res.actual_output != res.std_output and not output_mismatch:
                output_mismatch = {
                    "input": res.std_input,
                    "expected": res.std_output,
                    "actual": res.actual_output
                }
            if not res.passed and error == "":
                status = res.status
                error = res.stderr

        return status, error, total_run, output_mismatch, exec_time, mem_time

    @staticmethod
    async def run_code_service(
        db: AsyncSession,
        run_request: CodeRunRequest
    ) -> RunCodeResponse:
        logger.info("running code run service")

        lang_id = CodeExecutionService.get_piston_lanuage(run_request.language_id)
        test_cases = await TestCaseService.get_test_cases_by_problem_id(
            db, run_request.problem_id
        )
        public_cases = [tc for tc in test_cases if not tc.get("hidden", False)]
        logger.info(f"executing {len(public_cases)} public test cases")

        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [
                CodeExecutionService.run_test_case(
                    client=client,
                    lang_name=lang_id,
                    code=run_request.source_code,
                    test_case=TestCaseItem(**tc),
                    index=i + 1
                )
                for i, tc in enumerate(public_cases)
            ]
            results: List[ExecutionResult] = await asyncio.gather(*tasks)

        verdict = CodeExecutionService.calculate_run_verdict(results)

        return RunCodeResponse(
            verdict=verdict,
            total_public_cases=len(public_cases),
            results=results
        )

    @staticmethod
    async def submit_code_service(
        db: AsyncSession,
        submission_request: CodeSubmitRequest,
        user_id: int
    ) -> SubmissionResponse:
        logger.info("running code submit service")

        submission_exists = None
        if not submission_request.match_id:
            submission_exists = await SubmissionRepo.get_submission_by_match_id(
                db, user_id, submission_request.match_id
            )
        if not submission_exists:
            new_submission = await SubmissionRepo.create_submission(
                db, submission_request, user_id
            )

        lang_id = CodeExecutionService.get_piston_lanuage(submission_request.language_id)
        test_cases = await TestCaseService.get_test_cases_by_problem_id(
            db, submission_request.problem_id
        )
        logger.info(f"executing {len(test_cases)} test cases")

        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, tc in enumerate(test_cases):
                result = await CodeExecutionService.run_test_case(
                    client=client,
                    lang_name=lang_id,
                    code=submission_request.source_code,
                    test_case=TestCaseItem(**tc),
                    index=i + 1
                )
                results.append(result)

                # early exit on first failure
                if not result.passed:
                    for j, remaining_tc in enumerate(test_cases[i + 1:], start=i + 2):
                        results.append(ExecutionResult(
                            index=j,
                            status="Skipped",
                            passed=False,
                            std_input=remaining_tc["input"],
                            std_output=remaining_tc["output"],
                            actual_output="",
                            stderr="",
                            exec_time=0,
                            mem_time=0,
                            is_hidden=remaining_tc.get("hidden", False)
                        ))
                    break

        verdict, error, total_run, output_mismatch, exec_time, mem_time = \
            CodeExecutionService.calculate_submit_verdict(results)

        passed = False
        time_compl = None
        space_compl = None

        if verdict == "Accepted":
            passed = True
            time_compl, space_compl = CodeAnalyzeService.analyze(
                submission_request.source_code
            )

        updated_submission = SubmissionResponse(
            verdict=verdict,
            error=error,
            test_cases_passed=total_run,
            total_test_cases=len(test_cases),
            output_mismatch=output_mismatch,
            execution_time=exec_time,
            memory_used=mem_time,
            time_complexity=time_compl,
            space_complexity=space_compl
        )
        await SubmissionRepo.update_submission(
            db, new_submission.submission_id, updated_submission
        )
        submission = await SubmissionRepo.get_submission(db, new_submission.submission_id)

        return SubmissionResponse(
            submission_id=submission.submission_id,
            passed=passed,
            problem_id=submission.problem_id,
            verdict=verdict,
            execution_time=exec_time,
            memory_used=mem_time,
            output_mismatch=output_mismatch,
            stderr=error,
            test_cases_passed=total_run,
            total_test_cases=len(test_cases),
            time_complexity=time_compl,
            space_complexity=space_compl
        )

    @staticmethod
    async def winner_declare(
        db: AsyncSession,
        winner_request: FinalWinnerRequest
    ) -> FinalWinnerResponse:
        logger.info("declaring winner and loser")

        player1_result = await SubmissionRepo.get_submission_by_match_id(
            db, winner_request.player1_id, winner_request.match_id
        )
        player2_result = await SubmissionRepo.get_submission_by_match_id(
            db, winner_request.player2_id, winner_request.match_id
        )

        CodeExecutionService.log_model(player1_result, "Player1")
        CodeExecutionService.log_model(player2_result, "Player2")

        if not player1_result or not player2_result:
            raise ValueError("Submission not found")

        winner = None
        losser = None
        reason = None

        if player1_result.test_cases_passed != player2_result.test_cases_passed:
            if player1_result.test_cases_passed > player2_result.test_cases_passed:
                winner = player1_result.user_id
                losser = player2_result.user_id
            else:
                winner = player2_result.user_id
                losser = player1_result.user_id
            reason = "Winner passed more test cases"
        else:
            if player1_result.judged_at < player2_result.judged_at:
                winner = player1_result.user_id
                losser = player2_result.user_id
                reason = f"Winner submitted earlier by {player2_result.judged_at - player1_result.judged_at}"
            else:
                winner = player2_result.user_id
                losser = player1_result.user_id
                reason = f"Winner submitted earlier by {player1_result.judged_at - player2_result.judged_at}"

        result1 = SubmissionResponse.model_validate(player1_result)
        result2 = SubmissionResponse.model_validate(player2_result)

        if player1_result.user_id == winner:
            results = [result1, result2]
        else:
            results = [result2, result1]

        return FinalWinnerResponse(
            results=results,
            winner_id=winner,
            losser_id=losser,
            reason=reason
        )