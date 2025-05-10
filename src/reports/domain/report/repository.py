from abc import ABC, abstractmethod

from reports.domain.report.report import DeviceReport
from reports.domain.types import ReportId


class ReportRepository(ABC):
    @abstractmethod
    def add(self, report: DeviceReport) -> None: ...
    @abstractmethod
    async def delete(self, report: DeviceReport) -> None: ...
    @abstractmethod
    async def with_device_id(self, device_id: ReportId) -> list[DeviceReport]: ...
    @abstractmethod
    async def device_report_with_id(self, report_id: ReportId) -> DeviceReport | None: ...
