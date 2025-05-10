from dataclasses import dataclass

from reports.domain.shared.events import DomainEvent
from reports.domain.types import DeviceId, DeviceType, ReportId, UserId


@dataclass(frozen=True)
class DeviceReportCreated(DomainEvent):
    report_id: ReportId
    creator_id: UserId
    comment: str
    report_name: str
    device_id: DeviceId
    device_type: DeviceType


@dataclass(frozen=True)
class ReportCommentChanged(DomainEvent):
    report_id: ReportId
    comment: str


@dataclass(frozen=True)
class ReportNameChanged(DomainEvent):
    report_id: ReportId
    report_name: str


@dataclass(frozen=True)
class ReportDeleted(DomainEvent):
    report_id: ReportId
