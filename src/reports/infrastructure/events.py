from collections.abc import Iterable

from reports.application.ports.events import EventAdder, EventsRaiser
from reports.domain.shared.events import DomainEvent


class DomainEvents(EventsRaiser, EventAdder):
    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def add(self, event: DomainEvent) -> None:
        self._events.append(event)

    def raise_events(self) -> Iterable[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
