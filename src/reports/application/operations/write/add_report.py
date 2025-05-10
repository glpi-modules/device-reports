from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.markers import Command
from reports.application.ports.identity_provider import IdentityProvider
from reports.domain.report.factory import ReportFactory
from reports.domain.report.repository import ReportRepository
from reports.domain.types import DeviceId, DeviceType, ReportId


@dataclass(frozen=True)
class AddDeviceReport(Command[ReportId]):
    report_name: str
    comment: str
    device_id: DeviceId
    device_type: DeviceType


class AddDeviceReportHandler(RequestHandler[AddDeviceReport, ReportId]):
    def __init__(
        self,
        report_repository: ReportRepository,
        report_factory: ReportFactory,
        identity_provider: IdentityProvider,
    ) -> None:
        self._report_repository = report_repository
        self._report_factory = report_factory
        self._identity_provider = identity_provider

    async def handle(self, request: AddDeviceReport) -> ReportId:
        report = await self._report_factory.create_device_report(
            report_name=request.report_name,
            comment=request.comment,
            device_id=request.device_id,
            device_type=request.device_type,
            creator_id=self._identity_provider.current_user_id(),
        )

        self._report_repository.add(report)

        return report.entity_id
