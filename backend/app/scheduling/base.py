from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CalendarSlot:
    id: str
    starts_at: datetime
    ends_at: datetime
    doctor_name: str

    @property
    def label(self) -> str:
        day = self.starts_at.strftime("%a, %b %d")
        time = self.starts_at.strftime("%I:%M %p").lstrip("0")
        return f"{day} · {time} with {self.doctor_name}"


@dataclass(frozen=True)
class CalendarEvent:
    id: str
    slot_id: str
    starts_at: datetime
    ends_at: datetime
    doctor_name: str
    summary: str


class CalendarProvider(Protocol):
    """Swap MockCalendar for GoogleCalendar later without changing callers."""

    def list_free_slots(
        self,
        window_start: datetime,
        window_end: datetime,
        *,
        exclude_slot_ids: set[str] | None = None,
    ) -> list[CalendarSlot]:
        ...

    def create_event(
        self,
        slot: CalendarSlot,
        *,
        summary: str,
        description: str = "",
    ) -> CalendarEvent:
        ...
