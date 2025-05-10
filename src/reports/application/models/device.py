from dataclasses import dataclass

from reports.domain.types import DeviceId


@dataclass(frozen=True)
class DeviceReadModel:
    device_id: DeviceId
    device_name: str | None
    device_inventory_number: str
    device_serial_number: str
