from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.scheduling.base import CalendarEvent, CalendarSlot


DOCTORS = (
    "Dr. Sarah Chen",
    "Dr. James Okonkwo",
    "Dr. Priya Nair",
)


class MockCalendar:
    """
    Deterministic in-process clinic calendar.

    Generates weekday 30-minute slots and tracks bookings in memory.
    Google Calendar can replace this class behind the same protocol later.
    """

    def __init__(self) -> None:
        self._booked_slot_ids: set[str] = set()
        self._events: dict[str, CalendarEvent] = {}

    def list_free_slots(
        self,
        window_start: datetime,
        window_end: datetime,
        *,
        exclude_slot_ids: set[str] | None = None,
    ) -> list[CalendarSlot]:
        blocked = set(self._booked_slot_ids)
        if exclude_slot_ids:
            blocked |= exclude_slot_ids

        slots: list[CalendarSlot] = []
        cursor = window_start.astimezone(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = window_end.astimezone(timezone.utc)

        while cursor < end:
            if cursor.weekday() < 5:  # Mon–Fri
                for hour in range(9, 17):
                    for minute in (0, 30):
                        starts = cursor.replace(hour=hour, minute=minute)
                        if starts < window_start.astimezone(timezone.utc):
                            continue
                        if starts >= end:
                            break

                        ends = starts + timedelta(minutes=30)
                        slot_id = f"slot-{starts.strftime('%Y%m%d%H%M')}"

                        if slot_id in blocked:
                            continue

                        doctor = DOCTORS[len(slots) % len(DOCTORS)]
                        slots.append(
                            CalendarSlot(
                                id=slot_id,
                                starts_at=starts,
                                ends_at=ends,
                                doctor_name=doctor,
                            )
                        )

            cursor += timedelta(days=1)

        return slots

    def create_event(
        self,
        slot: CalendarSlot,
        *,
        summary: str,
        description: str = "",
    ) -> CalendarEvent:
        if slot.id in self._booked_slot_ids:
            raise ValueError(f"Slot already booked: {slot.id}")

        event = CalendarEvent(
            id=f"evt-{uuid4()}",
            slot_id=slot.id,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            doctor_name=slot.doctor_name,
            summary=summary,
        )
        self._booked_slot_ids.add(slot.id)
        self._events[event.id] = event
        return event


# Process-wide singleton so holds/bookings are visible across requests.
mock_calendar = MockCalendar()
