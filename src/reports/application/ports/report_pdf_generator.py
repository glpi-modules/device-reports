from abc import ABC, abstractmethod
from dataclasses import dataclass

from reports.application.models.device import DeviceReadModel
from reports.domain.media.value_objects import MediaMetadata


@dataclass(frozen=True)
class PdfReport:
    metadata: MediaMetadata
    file: bytes


class PdfReportGenerator(ABC):
    @abstractmethod
    def generate(self, device: DeviceReadModel) -> PdfReport: ...
