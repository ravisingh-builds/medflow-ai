from sqlalchemy.orm import Session
import json
from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
class ConversationService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ConversationRepository(db)

    def start(self, lead_id: str, field: str, question: str,):

        conversation = Conversation(lead_id=lead_id, current_field=field, current_question=question,)

        return self.repository.create(conversation)
    
    def reply(self,conversation_id: str,answer: str,):
        
        conversation = self.repository.get(conversation_id)
        answers = json.loads(conversation.answers)
        answers[conversation.current_field] = answer
        conversation.answers = json.dumps(answers)
        self.repository.update()

        return conversation