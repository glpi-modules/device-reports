from abc import ABC, abstractmethod

from reports.domain.types import EventId, MediaId, ReportId


class IdGenerator(ABC):
    @abstractmethod
    def report_id(self) -> ReportId: ...
    @abstractmethod
    def media_id(self) -> MediaId: ...
    @abstractmethod
    def event_id(self) -> EventId: ...
