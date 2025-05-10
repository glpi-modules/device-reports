from datetime import timedelta
from typing import Any

from httpx import AsyncClient, HTTPStatusError, RequestError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from reports.application.models.device import DeviceReadModel
from reports.application.ports.device_gateway import DeviceGateway
from reports.domain.types import DeviceId, DeviceType
from reports.infrastructure.http.http_glpi_auth_client import GlpiAuthClient


class HttpDeviceGateway(DeviceGateway):
    def __init__(self, client: AsyncClient, auth_client: GlpiAuthClient) -> None:
        self._client = client
        self._glpi_auth_client = auth_client

    @retry(
        retry=retry_if_exception_type((RequestError, HTTPStatusError)),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
        stop=stop_after_attempt(5),
    )
    async def load(
        self, device_id: DeviceId, device_type: DeviceType
    ) -> DeviceReadModel | None:
        async with self._glpi_auth_client as session:
            _header = {"Session-Token": session}

            response = await self._client.get(
                url=f"/{device_type}/{device_id}",
                headers=_header,
            )

            data: dict[str, Any] = response.json()

            if response.status_code != 200 or not data:
                return None

            try:
                return self._load(data)
            except (KeyError, AttributeError):
                return None

    def _load(self, data: dict[str, Any]) -> DeviceReadModel:
        return DeviceReadModel(
            device_id=DeviceId(data["id"]),
            device_inventory_number=data["otherserial"],
            device_serial_number=data["serial"],
            device_name=data.get("name"),
        )
