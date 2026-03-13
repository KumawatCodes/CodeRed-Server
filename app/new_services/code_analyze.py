from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List,Optional
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI


class CodeAnalyzeService:

    @staticmethod
    def analyze(code: str) -> dict[str,str]:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite"
        )

        class Code(BaseModel):
            time_complexity : str
            space_complexity: str

        parser = PydanticOutputParser(pydantic_object=Code)


        prompt = ChatPromptTemplate.from_messages([
            ('system',"""
        Extract code information from the format
            {format_instructions}
        """),
        ("human","{code}")
        ]
        )

        code = code

        final_prompt = prompt.invoke(
            {"code" : code,
            'format_instructions': parser.get_format_instructions()
            }
        )

        response = model.invoke(final_prompt)
        code_analysis = parser.parse(response.content)

        return code_analysis.time_complexity,code_analysis.space_complexity
