from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=settings.gemini_api_key,
    temperature=0,
)