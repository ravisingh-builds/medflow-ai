from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.slot_hold import SlotHold
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.slot_hold_repository import SlotHoldRepository
from app.scheduling import CalendarSlot, get_calendar

APPOINTMENT_SLOT_FIELD = "__appointment_slot__"

# P1 windows: (start_offset_days, end_offset_days) from now
PRIORITY_WINDOWS_DAYS = {
    "HIGH": (0, 2),
    "MEDIUM": (3, 7),
    "LOW": (8, 14),
    "UNKNOWN": (3, 7),
}

HOLD_MINUTES = 10
OFFER_COUNT = 3


def slot_to_dict(slot: CalendarSlot) -> dict:
    return {
        "id": slot.id,
        "label": slot.label,
        "starts_at": slot.starts_at.isoformat(),
        "ends_at": slot.ends_at.isoformat(),
        "doctor_name": slot.doctor_name,
    }


def appointment_to_dict(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "lead_id": appointment.lead_id,
        "conversation_id": appointment.conversation_id,
        "workflow_id": appointment.workflow_id,
        "slot_id": appointment.slot_id,
        "starts_at": appointment.starts_at.isoformat(),
        "ends_at": appointment.ends_at.isoformat(),
        "doctor_name": appointment.doctor_name,
        "priority": appointment.priority,
        "status": appointment.status,
        "label": _format_label(
            appointment.starts_at, appointment.doctor_name
        ),
    }


def _format_label(starts_at: datetime, doctor_name: str) -> str:
    day = starts_at.strftime("%a, %b %d")
    time = starts_at.strftime("%I:%M %p").lstrip("0")
    return f"{day} · {time} with {doctor_name}"


class SchedulingService:
    def __init__(self, db: Session):
        self.db = db
        self.holds = SlotHoldRepository(db)
        self.appointments = AppointmentRepository(db)
        self.calendar = get_calendar()

    def offer_slots(
        self,
        *,
        workflow_id: str,
        priority: str,
        count: int = OFFER_COUNT,
    ) -> list[dict]:
        """
        Soft-hold the next free seats in the priority window (movie-seat style).
        """
        self.holds.release_workflow_holds(workflow_id)

        now = datetime.now(timezone.utc)
        start_offset, end_offset = PRIORITY_WINDOWS_DAYS.get(
            (priority or "UNKNOWN").upper(),
            PRIORITY_WINDOWS_DAYS["UNKNOWN"],
        )
        window_start = now + timedelta(days=start_offset)
        window_end = now + timedelta(days=end_offset + 1)

        blocked = self.appointments.booked_slot_ids() | self.holds.blocked_slot_ids(
            except_workflow_id=workflow_id
        )

        free = self.calendar.list_free_slots(
            window_start,
            window_end,
            exclude_slot_ids=blocked,
        )

        chosen = free[:count]
        if not chosen:
            # Fallback: widen search a bit so the patient still gets options
            free = self.calendar.list_free_slots(
                now,
                now + timedelta(days=21),
                exclude_slot_ids=blocked,
            )
            chosen = free[:count]

        expires_at = now + timedelta(minutes=HOLD_MINUTES)
        hold_rows = [
            SlotHold(
                slot_id=slot.id,
                workflow_id=workflow_id,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                doctor_name=slot.doctor_name,
                status="ACTIVE",
                expires_at=expires_at,
            )
            for slot in chosen
        ]
        self.holds.create_many(hold_rows)

        return [slot_to_dict(slot) for slot in chosen]

    def confirm_slot(
        self,
        *,
        workflow_id: str,
        slot_id: str,
        lead_id: str,
        conversation_id: str | None,
        priority: str,
        patient_name: str,
        diagnosis: str = "",
    ) -> Appointment | None:
        hold = self.holds.get_active_hold(workflow_id, slot_id)
        if hold is None:
            return None

        slot = CalendarSlot(
            id=hold.slot_id,
            starts_at=hold.starts_at,
            ends_at=hold.ends_at,
            doctor_name=hold.doctor_name,
        )

        summary = f"Appointment — {patient_name or 'Patient'}"
        description = (
            f"Priority: {priority}\n"
            f"Diagnosis: {diagnosis or 'n/a'}\n"
            f"Workflow: {workflow_id}"
        )

        try:
            event = self.calendar.create_event(
                slot, summary=summary, description=description
            )
        except ValueError:
            hold.status = "RELEASED"
            self.holds.save()
            return None

        hold.status = "CONVERTED"
        self.holds.save()
        self.holds.release_workflow_holds(workflow_id, except_slot_id=slot_id)

        appointment = Appointment(
            lead_id=lead_id,
            conversation_id=conversation_id,
            workflow_id=workflow_id,
            slot_id=slot.id,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            doctor_name=slot.doctor_name,
            priority=(priority or "UNKNOWN").upper(),
            status="SCHEDULED",
            calendar_event_id=event.id,
        )
        return self.appointments.create(appointment)

    def list_scheduled(self) -> list[dict]:
        return [
            appointment_to_dict(row)
            for row in self.appointments.list_by_status("SCHEDULED")
        ]

    def complete(self, appointment_id: str) -> Appointment | None:
        appointment = self.appointments.get(appointment_id)
        if appointment is None:
            return None
        appointment.status = "COMPLETED"
        self.appointments.save()
        return appointment

    def get_by_workflow(self, workflow_id: str) -> dict | None:
        appointment = self.appointments.get_by_workflow(workflow_id)
        if appointment is None:
            return None
        return appointment_to_dict(appointment)
