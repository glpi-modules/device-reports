from abc import ABC, abstractmethod

from reports.application.models.media import FileName, MediaReadModel, PresignedUrl
from reports.domain.types import ReportId


class ObjectMediaGateway(ABC):
    @abstractmethod
    async def save(self, file_name: FileName, file: bytes) -> None: ...
    @abstractmethod
    async def get(self, file_name: FileName) -> PresignedUrl: ...
    @abstractmethod
    async def delete(self, file_name: FileName) -> None: ...


class MediaGateway(ABC):
    @abstractmethod
    async def with_report_id(self, report_id: ReportId) -> MediaReadModel | None: ...
