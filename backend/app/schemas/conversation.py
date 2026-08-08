from pydantic import BaseModel


class ConversationReply(BaseModel):
    conversation_id: str
    answer: str
    workflow_id: str