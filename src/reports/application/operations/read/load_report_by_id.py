from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.common.markers import Query
from reports.application.models.report import ReportReadModel
from reports.application.ports.identity_provider import IdentityProvider
from reports.application.ports.report_gateway import ReportGateway
from reports.domain.types import ReportId


@dataclass(frozen=True)
class LoadReportById(Query[ReportReadModel]):
    report_id: ReportId


class LoadReportByIdHandler(RequestHandler[LoadReportById, ReportReadModel]):
    def __init__(
        self, identity_provider: IdentityProvider, report_gateway: ReportGateway
    ) -> None:
        self._identity_provider = identity_provider
        self._report_gateway = report_gateway

    async def handle(self, request: LoadReportById) -> ReportReadModel:
        self._identity_provider.current_user_id()

        report = await self._report_gateway.with_id(report_id=request.report_id)

        if not report:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Report with id {request.report_id} not found",
            )

        return report
