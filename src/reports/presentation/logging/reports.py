from bazario.asyncio import NotificationHandler
from structlog.stdlib import BoundLogger as Logger

from reports.domain.report.events import (
    DeviceReportCreated,
    ReportCommentChanged,
    ReportDeleted,
    ReportNameChanged,
)


class LogReportCreatedNotHandler(NotificationHandler[DeviceReportCreated]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: DeviceReportCreated) -> None:
        self._logger.info(
            event="report_created",
            report_id=notification.report_id,
            device_id=notification.device_id,
            report_name=notification.report_name,
            report_comment=notification.comment,
            creator_id=notification.creator_id,
            created_at=notification.event_date,
            device_type=notification.device_type,
        )


class LogReportNameChangedNotHandler(NotificationHandler[ReportNameChanged]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: ReportNameChanged) -> None:
        self._logger.info(
            event="report_name_changed",
            report_id=notification.report_id,
            report_name=notification.report_name,
        )


class LogReportCommentChangedNotHandler(NotificationHandler[ReportCommentChanged]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: ReportCommentChanged) -> None:
        self._logger.info(
            event="report_comment_changed",
            report_id=notification.report_id,
            report_comment=notification.comment,
        )


class LogReportDeletedNotHandler(NotificationHandler[ReportDeleted]):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def handle(self, notification: ReportDeleted) -> None:
        self._logger.info(
            event="report_deleted",
            report_id=notification.report_id,
        )
