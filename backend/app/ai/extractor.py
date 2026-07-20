from langchain_core.prompts import ChatPromptTemplate
import json
from app.ai.llm import llm
from app.ai.prompts import EXTRACTION_PROMPT


prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)

chain = prompt | llm


def extract_referral(referral: str):
    response = chain.invoke({"referral": referral})

    text = (
        response.content[0]["text"]
        if isinstance(response.content, list)
        else response.content
    )

    return json.loads(text)     