from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get(self, appointment_id: str) -> Appointment | None:
        return self.db.get(Appointment, appointment_id)

    def save(self) -> None:
        self.db.commit()

    def list_by_status(self, status: str) -> list[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(Appointment.status == status)
            .order_by(Appointment.starts_at.asc())
            .all()
        )

    def get_by_workflow(self, workflow_id: str) -> Appointment | None:
        return (
            self.db.query(Appointment)
            .filter(Appointment.workflow_id == workflow_id)
            .order_by(Appointment.created_at.desc())
            .first()
        )

    def booked_slot_ids(self) -> set[str]:
        rows = (
            self.db.query(Appointment.slot_id)
            .filter(Appointment.status == "SCHEDULED")
            .all()
        )
        return {row[0] for row in rows}
