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

    def upsert(self, conversation_id: str | None, lead_id: str, workflow_id: str | None, field: str, question: str,):
        """
        Create the conversation the first time a workflow reaches this point,
        then update the same row on every later question/answer loop instead
        of inserting a new one, so one workflow == one resumable row.
        """
        if conversation_id:
            conversation = self.repository.get(conversation_id)

            if conversation is not None:
                conversation.current_field = field
                conversation.current_question = question
                conversation.status = "IN_PROGRESS"

                if workflow_id:
                    conversation.workflow_id = workflow_id

                self.repository.save()
                return conversation

        conversation = Conversation(
            lead_id=lead_id,
            workflow_id=workflow_id,
            current_field=field,
            current_question=question,
        )

        return self.repository.create(conversation)

    def complete(self, conversation_id: str | None):
        if not conversation_id:
            return None

        conversation = self.repository.get(conversation_id)

        if conversation is not None:
            conversation.status = "COMPLETED"
            self.repository.save()

        return conversation

    def list_resumable(self):
        rows = self.repository.list_in_progress()

        return [
            {
                "conversation_id": conversation.id,
                "workflow_id": conversation.workflow_id,
                "lead_id": lead.id,
                "patient_name": f"{lead.first_name} {lead.last_name}".strip()
                or "Unknown Patient",
                "chief_complaint": lead.chief_complaint,
                "priority": lead.ai_priority,
                "current_question": conversation.current_question,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
            for conversation, lead in rows
        ]

    def reply(self,conversation_id: str,answer: str,):
        
        conversation = self.repository.get(conversation_id)
        answers = json.loads(conversation.answers)
        answers[conversation.current_field] = answer
        conversation.answers = json.dumps(answers)
        self.repository.update()

        return conversation