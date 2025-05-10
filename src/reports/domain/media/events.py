from dataclasses import dataclass

from reports.domain.media.value_objects import MediaMetadata
from reports.domain.shared.events import DomainEvent
from reports.domain.types import MediaId, ReportId, UserId


@dataclass(frozen=True)
class ReportMediaGenerated(DomainEvent):
    media_id: MediaId
    uploaded_by: UserId
    metadata: MediaMetadata
    report_id: ReportId


@dataclass(frozen=True)
class ReportMediaDeleted(DomainEvent):
    media_id: MediaId
    report_id: ReportId
