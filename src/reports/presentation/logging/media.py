from bazario.asyncio import NotificationHandler
from structlog.stdlib import BoundLogger as Logger

from reports.domain.media.events import ReportMediaDeleted, ReportMediaGenerated


class LogReportMediaCreatedNotHandler(NotificationHandler[ReportMediaGenerated]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: ReportMediaGenerated) -> None:
        self._logger.info(
            event="report_media_created",
            report_id=notification.report_id,
            media_id=notification.media_id,
            uploaded_by=notification.uploaded_by,
            uploaded_at=notification.event_date,
            metadata=notification.metadata,
        )


class LogReportMediaDeletedNotHandler(NotificationHandler[ReportMediaDeleted]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: ReportMediaDeleted) -> None:
        self._logger.info(
            event="report_media_deleted",
            report_id=notification.report_id,
            media_id=notification.media_id,
        )
