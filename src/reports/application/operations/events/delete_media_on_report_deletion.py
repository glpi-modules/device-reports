from bazario.asyncio import NotificationHandler

from reports.application.models.media import build_file_name
from reports.application.ports.events import EventAdder
from reports.application.ports.media_gateway import ObjectMediaGateway
from reports.domain.media.events import ReportMediaDeleted
from reports.domain.media.repository import MediaRepository
from reports.domain.report.events import ReportDeleted


class DeleteMediaOnReportDeletionHandler(NotificationHandler[ReportDeleted]):
    def __init__(
        self,
        media_gateway: ObjectMediaGateway,
        media_repository: MediaRepository,
        event_adder: EventAdder,
    ) -> None:
        self._media_gateway = media_gateway
        self._media_repository = media_repository
        self._event_adder = event_adder

    async def handle(self, notification: ReportDeleted) -> None:
        report_media = await self._media_repository.with_report_id(
            report_id=notification.report_id
        )

        if not report_media:
            return

        filename = build_file_name(
            content_type=report_media.metadata.content_type,
            media_id=report_media.entity_id,
        )

        self._event_adder.add(
            event=ReportMediaDeleted(
                media_id=report_media.entity_id, report_id=report_media.report_id
            )
        )
        await self._media_gateway.delete(file_name=filename)
