from datetime import datetime

from reports.domain.shared.entity import Entity
from reports.domain.types import DeviceId, DeviceType, ReportId, UserId


class DeviceReport(Entity[ReportId]):
    def __init__(
        self,
        entity_id: ReportId,
        *,
        creator_id: UserId,
        comment: str,
        created_at: datetime,
        report_name: str,
        device_id: DeviceId,
        device_type: DeviceType,
    ) -> None:
        Entity.__init__(self, entity_id)

        self._creator_id = creator_id
        self._created_at = created_at
        self._comment = comment
        self._report_name = report_name
        self._device_id = device_id
        self._device_type = device_type

    def edit(self, comment: str, report_name: str) -> None:
        self.change_comment(comment)
        self.change_report_name(report_name)

    def change_comment(self, comment: str) -> None:
        if self._comment == comment:
            return

        self._comment = comment

    def change_report_name(self, report_name: str) -> None:
        if self._report_name == report_name:
            return

        self._report_name = report_name

    @property
    def creator_id(self) -> UserId:
        return self._creator_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def report_name(self) -> str:
        return self._report_name

    @property
    def device_id(self) -> DeviceId:
        return self._device_id

    @property
    def device_type(self) -> DeviceType:
        return self._device_type
