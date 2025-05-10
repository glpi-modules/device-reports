from dataclasses import dataclass
from os import environ
from typing import Final

from hatchet_sdk import Hatchet
from hatchet_sdk.config import ClientConfig

DEFAULT_HATCHET_API_KEY: Final[str] = (
    "eyJhbGciOiJFUzI1NiIsImtpZCI6IkxKN2NBZyJ9.eyJhdWQiOiJodHRwczovL2Nsb3VkLm9uaGF0Y2hldC5ydW4iLCJleHAiOjQ4OTkyODA4NDEsImdycGNfYnJvYWRjYXN0X2FkZHJlc3MiOiIxMDRhZC5jbG91ZC5vbmhhdGNoZXQucnVuOjQ0MyIsImlhdCI6MTc0NTY4MDg0MSwiaXNzIjoiaHR0cHM6Ly9jbG91ZC5vbmhhdGNoZXQucnVuIiwic2VydmVyX3VybCI6Imh0dHBzOi8vY2xvdWQub25oYXRjaGV0LnJ1biIsInN1YiI6ImIxNzVhYzEzLTQ0MmYtNDA5My1hN2Q4LTVlYThmMTZmMTI2NiIsInRva2VuX2lkIjoiZjgxNjdkODktY2M4NC00NGRkLThhNDgtMThjODkzZGRkOTQwIn0.joTdp5On4GH6UWkemchNMuUe02NqB4QIATrfJofcSaAnS2IWIiPz2fhx8euKuDpPa5bWGt5mDIrCEWfD4LkaTQ"
)


@dataclass(frozen=True)
class HatchetConfig:
    api_key: str


def load_hatchet_config() -> HatchetConfig:
    return HatchetConfig(environ.get("HATCHET_API_KEY", DEFAULT_HATCHET_API_KEY))


def build_hacthcet_client_config() -> ClientConfig:
    _config = load_hatchet_config()

    return ClientConfig(token=_config.api_key)


def hatchet_factory() -> Hatchet:
    _hatchet_client_config = build_hacthcet_client_config()

    return Hatchet(debug=True, config=_hatchet_client_config)


HATCHET: Final[Hatchet] = hatchet_factory()
