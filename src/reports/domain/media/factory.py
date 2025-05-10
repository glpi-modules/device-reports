from abc import ABC, abstractmethod

from reports.domain.media.media import ReportMedia
from reports.domain.media.value_objects import MediaMetadata
from reports.domain.types import ReportId, UserId


class MediaFactory(ABC):
    @abstractmethod
    async def create_report_media(
        self, report_id: ReportId, metadata: MediaMetadata, uploaded_by: UserId
    ) -> ReportMedia: ...
