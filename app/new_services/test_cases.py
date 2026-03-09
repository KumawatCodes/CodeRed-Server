import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.testcase_repo import TestCaseRepo
from app.models.test_cases import TestCases
# from app.schemas.test_cases import 
from app.core.exceptions import NoTestCasesFound
logger = logging.getLogger(__name__)

class TestCaseService:
    """ Service for test cases"""


    @staticmethod
    async def get_test_cases_by_problem_id(
        db: AsyncSession,
        problem_id: int
    ):
        """
        fetching test case by problem id\n
        Args:
            db (AsyncSession): database sessiong
            problem_id (int): id of problem
        Returns:
            list of test cases
        """

        logger.info("fetching test case for the particular problem id")

        test_cases = await TestCaseRepo.get_test_cases_by_problem_id(db,problem_id)

        if not test_cases:
            logger.warning("No test cases found!")
            raise NoTestCasesFound()
        
        logger.info("successfully fetched the test cases")

        return test_cases