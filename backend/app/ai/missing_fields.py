import json

from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.prompts.missing_fields import MISSING_FIELDS_PROMPT
from app.ai.parser import parse_json_response

prompt = ChatPromptTemplate.from_template(MISSING_FIELDS_PROMPT)

chain = prompt | llm


def detect_missing_fields(referral: str, extracted: dict):

    response = chain.invoke({"referral": referral, "extracted": json.dumps(extracted, indent=2),})

    return parse_json_response(response)

