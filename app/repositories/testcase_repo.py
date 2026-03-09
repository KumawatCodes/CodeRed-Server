from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.test_cases import TestCases
from typing import List, Dict, Any
import json

class TestCaseRepo:

    @staticmethod
    async def get_test_cases_by_problem_id(db: AsyncSession, problem_id: int) -> List[Dict[str,Any]]:
        """
        fetching test case by problem id\n
        Args:
            db (AsyncSession): database sessiong
            problem_id (int): id of problem
        Returns:
            list of test cases
        """
        stmt = select(TestCases).where(TestCases.problem_id == problem_id)
        result = await db.execute(stmt)
        
        record = result.scalars().first()

        if not record:
            return []
        
        # fetching test cases
        test_cases = record.test_cases 

        if isinstance(test_cases,str):
            test_cases = json.loads(test_cases)

        return test_cases

