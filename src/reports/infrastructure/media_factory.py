from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.ports.events import EventAdder
from reports.application.ports.id_generator import IdGenerator
from reports.application.ports.time_provider import TimeProvider
from reports.domain.media.events import ReportMediaGenerated
from reports.domain.media.factory import MediaFactory
from reports.domain.media.media import ReportMedia
from reports.domain.media.value_objects import MediaMetadata
from reports.domain.report.repository import ReportRepository
from reports.domain.types import ReportId, UserId


class MediaFactoryImpl(MediaFactory):
    def __init__(
        self,
        id_generator: IdGenerator,
        time_provider: TimeProvider,
        report_repository: ReportRepository,
        event_adder: EventAdder,
    ) -> None:
        self._id_generator = id_generator
        self._time_provider = time_provider
        self._report_repository = report_repository
        self._event_adder = event_adder

    async def create_report_media(
        self, report_id: ReportId, metadata: MediaMetadata, uploaded_by: UserId
    ) -> ReportMedia:
        if not await self._report_repository.device_report_with_id(report_id=report_id):
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Report with id {report_id} not found",
            )

        report_media = ReportMedia(
            entity_id=self._id_generator.media_id(),
            uploaded_at=self._time_provider.current(),
            metadata=metadata,
            report_id=report_id,
            uploaded_by=uploaded_by,
        )

        self._event_adder.add(
            event=ReportMediaGenerated(
                media_id=report_media.entity_id,
                uploaded_by=report_media.uploaded_by,
                metadata=report_media.metadata,
                report_id=report_media.report_id,
            )
        )

        return report_media
