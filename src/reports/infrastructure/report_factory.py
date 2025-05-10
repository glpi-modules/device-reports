from typing import cast

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.ports.device_gateway import DeviceGateway
from reports.application.ports.events import EventAdder
from reports.application.ports.id_generator import IdGenerator
from reports.application.ports.time_provider import TimeProvider
from reports.domain.report.events import DeviceReportCreated
from reports.domain.report.factory import ReportFactory
from reports.domain.report.report import DeviceReport
from reports.domain.types import DeviceId, DeviceType, UserId
from reports.infrastructure.report_proxy import DeviceReportProxy


class ReportFactoryImlp(ReportFactory):
    def __init__(
        self,
        id_generator: IdGenerator,
        time_provider: TimeProvider,
        device_gateway: DeviceGateway,
        event_adder: EventAdder,
    ) -> None:
        self._id_generator = id_generator
        self._time_provider = time_provider
        self._device_gateway = device_gateway
        self._event_adder = event_adder

    async def create_device_report(
        self,
        report_name: str,
        comment: str,
        device_id: DeviceId,
        device_type: DeviceType,
        creator_id: UserId,
    ) -> DeviceReport:
        device = await self._device_gateway.load(
            device_id=device_id, device_type=device_type
        )

        if not device:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Device with id {device_id} and type {device_type} not found",
            )

        device_report = DeviceReport(
            report_name=report_name,
            entity_id=self._id_generator.report_id(),
            creator_id=creator_id,
            comment=comment,
            created_at=self._time_provider.current(),
            device_id=device_id,
            device_type=device_type,
        )

        self._event_adder.add(
            event=DeviceReportCreated(
                report_id=device_report.entity_id,
                report_name=device_report.report_name,
                comment=device_report.comment,
                creator_id=device_report.creator_id,
                device_id=device_report.device_id,
                device_type=device_report.device_type,
            )
        )

        return cast(DeviceReport, DeviceReportProxy(device_report, self._event_adder))
