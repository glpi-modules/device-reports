from abc import ABC, abstractmethod

from reports.domain.report.report import DeviceReport
from reports.domain.types import DeviceId, DeviceType, UserId


class ReportFactory(ABC):
    @abstractmethod
    async def create_device_report(
        self,
        report_name: str,
        comment: str,
        device_id: DeviceId,
        device_type: DeviceType,
        creator_id: UserId,
    ) -> DeviceReport: ...
