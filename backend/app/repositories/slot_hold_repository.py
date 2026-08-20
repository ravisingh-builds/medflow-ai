from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.slot_hold import SlotHold


class SlotHoldRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, holds: list[SlotHold]) -> list[SlotHold]:
        self.db.add_all(holds)
        self.db.commit()
        for hold in holds:
            self.db.refresh(hold)
        return holds

    def save(self) -> None:
        self.db.commit()

    def active_for_workflow(self, workflow_id: str) -> list[SlotHold]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(SlotHold)
            .filter(SlotHold.workflow_id == workflow_id)
            .filter(SlotHold.status == "ACTIVE")
            .filter(SlotHold.expires_at > now)
            .all()
        )

    def get_active_hold(
        self, workflow_id: str, slot_id: str
    ) -> SlotHold | None:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(SlotHold)
            .filter(SlotHold.workflow_id == workflow_id)
            .filter(SlotHold.slot_id == slot_id)
            .filter(SlotHold.status == "ACTIVE")
            .filter(SlotHold.expires_at > now)
            .first()
        )

    def blocked_slot_ids(
        self, *, except_workflow_id: str | None = None
    ) -> set[str]:
        """Slots held by other workflows (still unexpired)."""
        now = datetime.now(timezone.utc)
        query = (
            self.db.query(SlotHold.slot_id)
            .filter(SlotHold.status == "ACTIVE")
            .filter(SlotHold.expires_at > now)
        )
        if except_workflow_id:
            query = query.filter(SlotHold.workflow_id != except_workflow_id)
        return {row[0] for row in query.all()}

    def release_workflow_holds(
        self, workflow_id: str, *, except_slot_id: str | None = None
    ) -> None:
        holds = (
            self.db.query(SlotHold)
            .filter(SlotHold.workflow_id == workflow_id)
            .filter(SlotHold.status == "ACTIVE")
            .all()
        )
        for hold in holds:
            if except_slot_id and hold.slot_id == except_slot_id:
                continue
            hold.status = "RELEASED"
        self.db.commit()
