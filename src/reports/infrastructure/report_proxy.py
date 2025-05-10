from datetime import datetime

from reports.application.ports.events import EventAdder
from reports.domain.report.events import ReportCommentChanged, ReportNameChanged
from reports.domain.report.report import DeviceReport
from reports.domain.types import DeviceId, DeviceType, ReportId, UserId


class DeviceReportProxy:
    def __init__(
        self,
        device_report: DeviceReport,
        event_adder: EventAdder,
    ) -> None:
        self.device_report = device_report
        self.event_adder = event_adder

    def edit(self, comment: str, report_name: str) -> None:
        self.change_comment(comment=comment)
        self.change_report_name(report_name=report_name)

    def change_comment(self, comment: str) -> None:
        self.device_report.change_comment(comment)
        self.event_adder.add(
            ReportCommentChanged(
                report_id=self.device_report.entity_id, comment=self.device_report.comment
            )
        )

    def change_report_name(self, report_name: str) -> None:
        self.device_report.change_report_name(report_name)
        self.event_adder.add(
            ReportNameChanged(
                report_id=self.device_report.entity_id,
                report_name=self.device_report.report_name,
            )
        )

    @property
    def entity_id(self) -> ReportId:
        return self.device_report.entity_id

    @property
    def creator_id(self) -> UserId:
        return self.device_report.creator_id

    @property
    def created_at(self) -> datetime:
        return self.device_report.created_at

    @property
    def comment(self) -> str:
        return self.device_report.comment

    @property
    def report_name(self) -> str:
        return self.device_report.report_name

    @property
    def device_id(self) -> DeviceId:
        return self.device_report.device_id

    @property
    def device_type(self) -> DeviceType:
        return self.device_report.device_type
