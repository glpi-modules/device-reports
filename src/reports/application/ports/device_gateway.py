from abc import ABC, abstractmethod

from reports.application.models.device import DeviceReadModel
from reports.domain.types import DeviceId, DeviceType


class DeviceGateway(ABC):
    @abstractmethod
    async def load(
        self, device_id: DeviceId, device_type: DeviceType
    ) -> DeviceReadModel | None: ...
