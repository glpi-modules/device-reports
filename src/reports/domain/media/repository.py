from abc import ABC, abstractmethod

from reports.domain.media.media import ReportMedia, _BaseMedia
from reports.domain.types import ReportId


class MediaRepository(ABC):
    @abstractmethod
    def add(self, media: _BaseMedia) -> None: ...
    @abstractmethod
    async def delete(self, media: _BaseMedia) -> None: ...
    @abstractmethod
    async def with_report_id(self, report_id: ReportId) -> ReportMedia | None: ...
