from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.markers import Query
from reports.application.models.pagination import Pagination
from reports.application.models.report import ReportReadModel
from reports.application.ports.identity_provider import IdentityProvider
from reports.application.ports.report_gateway import ReportGateway


@dataclass(frozen=True)
class LoadReports(Query[list[ReportReadModel]]):
    pagination: Pagination


class LoadReportsHandler(RequestHandler[LoadReports, list[ReportReadModel]]):
    def __init__(
        self, identity_provider: IdentityProvider, report_gateway: ReportGateway
    ) -> None:
        self._identity_provider = identity_provider
        self._report_gateway = report_gateway

    async def handle(self, request: LoadReports) -> list[ReportReadModel]:
        self._identity_provider.current_user_id()

        reports = await self._report_gateway.load_many(pagination=request.pagination)

        return reports
