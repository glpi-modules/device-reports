from abc import ABC, abstractmethod
from collections.abc import Iterable

from reports.domain.shared.events import DomainEvent


class EventAdder(ABC):
    @abstractmethod
    def add(self, event: DomainEvent) -> None: ...


class EventsRaiser(ABC):
    @abstractmethod
    def raise_events(self) -> Iterable[DomainEvent]: ...
