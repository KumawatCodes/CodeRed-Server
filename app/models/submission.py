from sqlalchemy import Column, Integer, String, Boolean, DateTime,TEXT,Float,ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Submission(Base):
    __tablename__ = "submission"

    submission_id = Column(Integer,primary_key=True,index=True)
    # foreign key relationship
    user_id = Column(Integer,nullable=False, index=True)
    # Add relationship in future
    problem_id = Column(Integer,nullable=False, index=True)
    match_id = Column(String,nullable=True, index=True)
    token = Column(String, unique=True, index=True, nullable=True)
    language_id = Column(Integer,nullable=False, index=True)
    source_code = Column(TEXT,nullable=False)
    verdict = Column(String,nullable=False)
    execution_time = Column(Float,nullable= True)
    memory_used = Column(Integer,nullable=True)
    test_cases_passed = Column(Integer,default=0,nullable=True)
    total_test_cases = Column(Integer,default=0,nullable=True)
    error_message = Column(TEXT,nullable=True)
    time_complexity = Column(String,nullable=True)
    space_complexity = Column(String,nullable=True)
    is_final_submission = Column(Boolean,default=False)
    submitted_at = Column(DateTime(timezone=True),server_default=func.now())
    judged_at = Column(DateTime(timezone=True), server_default=func.now())