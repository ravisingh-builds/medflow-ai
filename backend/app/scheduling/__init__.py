from app.scheduling.base import CalendarEvent, CalendarProvider, CalendarSlot
from app.scheduling.mock import mock_calendar


def get_calendar() -> CalendarProvider:
    """Return the active calendar provider (mock today, Google later)."""
    return mock_calendar


__all__ = [
    "CalendarEvent",
    "CalendarProvider",
    "CalendarSlot",
    "get_calendar",
]
