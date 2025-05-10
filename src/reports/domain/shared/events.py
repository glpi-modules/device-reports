from dataclasses import dataclass, field
from datetime import datetime

from bazario import Notification

from reports.domain.types import EventId


@dataclass(frozen=True, kw_only=True)
class DomainEvent(Notification):
    event_date: datetime | None = field(default=None, init=False)
    event_id: EventId | None = field(default=None, init=False)

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def set_event_id(self, event_id: EventId) -> None:
        if self.event_id:
            return

        object.__setattr__(self, "event_id", event_id)

    def set_event_date(self, event_date: datetime) -> None:
        if self.event_date:
            return

        object.__setattr__(self, "event_date", event_date)
