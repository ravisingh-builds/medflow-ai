import json

from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.prompts.conversation import CONVERSATION_PROMPT
from app.ai.parser import parse_json_response

prompt = ChatPromptTemplate.from_template(
    CONVERSATION_PROMPT
)

chain = prompt | llm


def next_question(referral: str, extracted: dict, priority: dict, missing_fields: dict):

    response = chain.invoke(
        {
            "referral": referral,
            "extracted": json.dumps(extracted, indent=2),
            "priority": json.dumps(priority, indent=2),
            "missing_fields": json.dumps(missing_fields, indent=2),
        }
    )

    return parse_json_response(response)