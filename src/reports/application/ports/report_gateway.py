from abc import ABC, abstractmethod

from reports.application.models.pagination import Pagination
from reports.application.models.report import ReportReadModel
from reports.domain.types import ReportId


class ReportGateway(ABC):
    @abstractmethod
    async def load_many(self, pagination: Pagination) -> list[ReportReadModel]: ...
    @abstractmethod
    async def with_id(self, report_id: ReportId) -> ReportReadModel | None: ...
