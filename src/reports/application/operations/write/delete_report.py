from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.common.markers import Command
from reports.application.ports.events import EventAdder
from reports.application.ports.identity_provider import IdentityProvider
from reports.domain.report.events import ReportDeleted
from reports.domain.report.repository import ReportRepository
from reports.domain.types import ReportId


@dataclass(frozen=True)
class DeleteDeviceReport(Command[None]):
    report_id: ReportId


class DeleteDeviceReportHandler(RequestHandler[DeleteDeviceReport, None]):
    def __init__(
        self,
        report_repository: ReportRepository,
        identity_provider: IdentityProvider,
        event_adder: EventAdder,
    ) -> None:
        self._report_repository = report_repository
        self._identity_provider = identity_provider
        self._event_adder = event_adder

    async def handle(self, request: DeleteDeviceReport) -> None:
        current_user_id = self._identity_provider.current_user_id()
        report = await self._report_repository.device_report_with_id(
            report_id=request.report_id
        )

        if not report:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Report with id {request.report_id} not found",
            )

        if report.creator_id != current_user_id:
            raise ApplicationError(
                error_type=ErrorType.FORBIDDEN,
                message=f"User {current_user_id} is not the creator of the report",
            )

        self._event_adder.add(event=ReportDeleted(report_id=request.report_id))

        await self._report_repository.delete(report)
