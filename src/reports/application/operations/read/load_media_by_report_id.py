from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.common.markers import Query
from reports.application.models.media import MediaReadModel
from reports.application.ports.media_gateway import MediaGateway
from reports.domain.types import ReportId


@dataclass(frozen=True)
class LoadMediaByReportId(Query[MediaReadModel]):
    device_report_id: ReportId


class LoadMediaByReportIdHandler(RequestHandler[LoadMediaByReportId, MediaReadModel]):
    def __init__(self, media_gateway: MediaGateway) -> None:
        self._media_gateway = media_gateway

    async def handle(self, request: LoadMediaByReportId) -> MediaReadModel:
        media = await self._media_gateway.with_report_id(
            report_id=request.device_report_id
        )

        if not media:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Media with report {request.device_report_id} not found",
            )

        return media
