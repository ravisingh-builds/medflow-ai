from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation):

        self.db.add(conversation)

        self.db.commit()

        self.db.refresh(conversation)

        return conversation

    def get(self, conversation_id: str):

        return self.db.get(
            Conversation,
            conversation_id,
        )

    def update(self):

        self.db.commit()

    def save(self):

        self.db.commit()