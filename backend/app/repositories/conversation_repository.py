from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.lead import Lead
class ConversationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation):
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get(self, conversation_id: str):
        return self.db.get(Conversation, conversation_id,)

    def update(self):
        self.db.commit()

    def save(self):
        self.db.commit()

    def list_in_progress(self):
        """Paused/unfinished conversations, most recently active first."""
        return (
            self.db.query(Conversation, Lead)
            .join(Lead, Conversation.lead_id == Lead.id)
            .filter(Conversation.status == "IN_PROGRESS")
            .filter(Conversation.workflow_id.isnot(None))
            .order_by(Conversation.updated_at.desc())
            .all()
        )