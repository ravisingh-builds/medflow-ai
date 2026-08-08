from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.prompts.priority import PRIORITY_PROMPT
from app.ai.parser import parse_json_response

prompt = ChatPromptTemplate.from_template(PRIORITY_PROMPT)

chain = prompt | llm


def classify_priority(referral: str):

    response = chain.invoke({"referral": referral})

    return parse_json_response(response)