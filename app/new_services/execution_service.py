import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.new_services.test_cases import TestCaseService
from app.config import PISTON_API_URL
from app.models.submission import Submission
from app.schemas.test_cases import TestCaseItem
from app.schemas.submission import CodeRunRequest,CodeSubmitRequest, SubmissionResponse
from app.schemas.execution import ExecutionResult,RunCodeResponse
from app.core.exceptions import NoLanguageFound, FailedPistonExecution

from typing import Dict,List,Any
import logging

logger = logging.getLogger(__name__)

LANGUAGE_MAP: Dict[int, str] = {
    71: "python",      # Python 3
    50: "c",           # C (GCC)
    54: "c++",         # C++ (GCC)
    62: "java",        # Java (OpenJDK)
    63: "javascript",  # Node.js
}

class CodeExecutionService:
    """ service for code submission """

    @staticmethod
    def get_piston_lanuage(lang_id: int) -> str:
        """
        getting language name from its id\n
        Args:
            lang_id(int): id of language
        Returns:
            language_name(str)
        """

        logger.info("fetching language name by its id")

        lang_name= LANGUAGE_MAP.get(lang_id)
        
        if not lang_name:
            logger.warning("for the id no programming language exists")
            raise NoLanguageFound()
        
        logger.info("successfully fetched the language name")

        return lang_name
    
    @staticmethod
    async def run_piston_request(
        client: httpx.AsyncClient,
        lang_name: str,
        code: str,
        stdin: str
    )-> Dict:
        """
        run a test case
        Args:
            client: httpx.AsyncClient,
            language name: str,
            code: str,
            stdin: str (std input)
        Returns:
            Json output of piston
        """

        logger.info("preparing payload to make a request to piston.")
        payload= {
            "language": lang_name,
            "version": "*", #latest version
            "files": [{"content": code}],
            "stdin": stdin,
            "run_timeout": 3000 # 3sec
        }

        response= await client.post(PISTON_API_URL, json=payload)
        response.raise_for_status()
        data= response.json()

        if not data:
            logger.warning("failed to get the response")
            raise FailedPistonExecution()

        logger.info("successfully got the response")
        return data



    @staticmethod
    def handle_compile_error(
        compile_stage: Dict,
        test_case: TestCaseItem,
        index: int
    ) -> ExecutionResult:
        """
        handling compilation error
        Args:
            compile_stage: dict data of output,
            test_case: test cases,
            index: total test cases
        Returns:
            ExecutionResult: output returned by piston
        """
        logger.info("creating an execution response for compilation error")

        return ExecutionResult(
            index= index,
            status= "Compilation Error",
            passed= False,
            input= test_case.input,
            expected= test_case.output,
            actual= "",
            stderr= compile_stage.get("stderr"),
            time= compile_stage.get("cpu_time")/1000.0 or 0,
            memory= compile_stage.get("memory")or 0,
            hidden= test_case.hidden
        )



    @staticmethod
    def handle_runtime_result(
        run_stage: Dict,
        test_case: TestCaseItem,
        index: int
    ) -> ExecutionResult:
        """
        handling runtime result
        initialzed verdict.
        Args:
            run_stage: dict data of output,
            test_case: test cases,
            index: total test cases
        Returns:
            ExecutionResult: output returned by piston
        """
        logger.info("handling run time result")

        actual_output:str= (run_stage.get("stdout") or "").strip()
        exit_code:int= run_stage.get("code",0)
        
        status= "Accepted"
        passed= True

        # check runtime error
        if exit_code != 0:
            status= "Runtime Error"
            passed= False
        # checking outputs
        elif actual_output!=test_case.output:
            status= "Wrong Answer"
            passed= False
        
        return ExecutionResult(
            index= index,
            status= status,
            passed= passed,
            input= test_case.input,
            expected= test_case.output,
            actual= actual_output,
            stderr= run_stage.get("stderr"),
            time= run_stage.get("cpu_time")/1000.0 or 0,
            memory= run_stage.get("memory")or 0,
            hidden= test_case.hidden
        )

    @staticmethod
    async def run_test_case(
        client: httpx.AsyncClient,
        lang_name: str,
        code: str,
        test_case: TestCaseItem,
        index: int
    ) -> ExecutionResult:
        """
        run each test case using run_piston_request
        Args:
            client: httpx.AsyncClient,
            language name: str,
            code: str,
            test_case: testCase,
            stdin: str (std input)
        Returns:
            ExecutionResult: output returned by piston
        """

        logger.info("running test case")

        data= await CodeExecutionService.run_piston_request(
            client,lang_name,code,test_case.input
        )
        
        run_stage: Dict[str,Any] = data.get("run",{}) or{}
        compile_stage: Dict[str,Any] = data.get("compile",{}) or {}
        # check for compilation error
        response = None
        if compile_stage and compile_stage.get("code",0) !=0:
            response= CodeExecutionService.handle_compile_error(
                compile_stage,test_case,index
            )
        else:
            response= CodeExecutionService.handle_runtime_result(
                run_stage,test_case,index
            )
        
        logger.info("returning response of the test case")
        return response


    @staticmethod
    def calculate_run_verdict(
        results: List[ExecutionResult]
    ) -> str:
        """
        check compilation error and then finalise verdict
        Args:
            List[ExecutionResult]: all test cases result
        Returns:
            verdict(str):
                Accepted,wrong answer, error
        """
        logger.info("judging the final run verdict")
        status="Accepted"
        for res in results:
            if not res["passed"]:
                status= res["status"]
                break

        return status

    @staticmethod
    def calculate_submit_verdict(
        results: List[ExecutionResult]
    ) -> tuple[str, str] :
        """
        check compilation error and then finalise verdict
        Args:
            List[ExecutionResult]: all test cases result
        Returns:
            verdict(str):
                Accepted,wrong answer, error
        """
        logger.info("judging the final submit verdict")
        status = "Accepted"
        error = ""
        for res in results:
            if not res["passed"]:
                status= res["status"]
                error = res["stderr"]
                break;

        return tuple(status,error)


    @staticmethod
    async def run_code_service(
        db: AsyncSession,
        run_request: CodeRunRequest
    ) -> RunCodeResponse:
        """
        run service for non-hidden test cases
        Args:
            db: asyncsession,
            run_request:
                code,stdin,problem_id,language_id
        Returns:
            RunCodeResponse:
                verdict,
                totat_public_cases,
                results: list[ExecutionResult]
        """
        logger.info("running code run service")
        
        # getting language name
        lang_name= CodeExecutionService.get_piston_lanuage(run_request.language_id)

        test_cases = await TestCaseService.get_test_cases_by_problem_id(
            db,run_request.problem_id
        )
        public_cases = [tc for tc in test_cases if not tc.get("hidden",False)]
        logger.info(f"executing {len(public_cases)} test cases")

        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks= [
                CodeExecutionService.run_test_case(
                    client= client,
                    lang_name= lang_name,
                    code= run_request.source_code,
                    test_case=tc,
                    index= i+1
                )
                for i,tc in enumerate(public_cases)
            ]
            results: List[ExecutionResult]= await asyncio.gather(*tasks)
        # getting final verdict
        verdict= CodeExecutionService.calculate_run_verdict(results)

        return RunCodeResponse(
            verdict= verdict,
            total_public_cases= len(public_cases),
            results= results
        )
        


    @staticmethod
    async def submit_code_service(
        db: AsyncSession,
        submission_request: CodeSubmitRequest,
        user_id: int
    ) -> SubmissionResponse:
        """
        run service for non-hidden test cases
        Args:
            db: asyncsession,
            submission_request:
                code,problem_id,language_id
        Returns:
            SubmissionResponse:
                verdict,
                totat_public_cases,
                results: list[ExecutionResult]
        """

        logger.info("running code submit service")

        #getting language name
        lang_name = CodeExecutionService.get_piston_lanuage(submission_request.language_id)

        test_cases = await TestCaseService.get_test_cases_by_problem_id(
            db, submission_request.problem_id
        )

        logger.info(f"executing {len(test_cases)} test cases")

        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks= [
                CodeExecutionService.run_test_case(
                    client= client,
                    lang_name= lang_name,
                    code= submission_request.source_code,
                    test_case= tc,
                    index= i+1
                )
                for i,tc in enumerate(test_cases)
            ]
            results: List[ExecutionResult]= await asyncio.gather(*tasks)
        
        #getting final verdict
        verdict,error = CodeExecutionService.calculate_submit_verdict(results)

        


        