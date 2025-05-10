from uuid_extensions import uuid7

from reports.application.ports.id_generator import IdGenerator
from reports.domain.types import EventId, MediaId, ReportId


class UUID7IdGenerator(IdGenerator):
    def report_id(self) -> ReportId:
        return ReportId(uuid7())

    def media_id(self) -> MediaId:
        return MediaId(uuid7())

    def event_id(self) -> EventId:
        return EventId(uuid7())
