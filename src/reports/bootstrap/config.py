import logging
import sys
from collections.abc import Callable, Generator, Mapping, MutableMapping
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from importlib.resources import files
from os import environ
from pathlib import Path
from types import FunctionType
from typing import Any, Final, cast

import structlog
from alembic.config import Config as AlembicConfig
from hatchet_sdk import Worker
from uvicorn import Config as UvicornConfig

DEFAULT_DB_URI: Final[str] = "sqlite+aiosqlite:///reports.db"
DEFAULT_MQ_URI: Final[str] = "amqp://guest:guest@localhost:5672/"
DEFAULT_SERVER_HOST: Final[str] = "127.0.0.1"
DEFAULT_SERVER_PORT: Final[int] = 8000
DEFAULT_S3_MINIO_URI: Final[str] = "http://localhost:9000"


@dataclass(frozen=True)
class RabbitmqConfig:
    uri: str


@dataclass(frozen=True)
class DatabaseConfig:
    uri: str


@dataclass(frozen=True)
class S3MinioConfig:
    base_uri: str
    access_key: str
    secret_key: str


@dataclass(frozen=True)
class TaskiqBrokerConfig:
    factory_path: str


@dataclass(frozen=True)
class GlpiApiConfig:
    app_token: str
    glpi_uri: str
    user_token: str


def get_rabbitmq_config() -> RabbitmqConfig:
    return RabbitmqConfig(environ.get("RABBITMQ_URI", DEFAULT_MQ_URI))


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig(environ.get("DATABASE_URI", DEFAULT_DB_URI))


def get_s3_minio_config() -> S3MinioConfig:
    return S3MinioConfig(
        environ.get("S3_MINIO_BASE_URI", DEFAULT_S3_MINIO_URI),
        environ.get("S3_MINIO_ACCESS_KEY", ""),
        environ.get("S3_MINIO_SECRET_KEY", ""),
    )


def get_glpi_api_config() -> GlpiApiConfig:
    return GlpiApiConfig(
        environ.get("GLPI_API_TOKEN", ""),
        environ.get("GLPI_API_URL", ""),
        environ.get("GLPI_USER_TOKEN", ""),
    )


def get_alembic_config() -> AlembicConfig:
    resource = files("reports.infrastructure.persistence.alembic")
    config_file = resource.joinpath("alembic.ini")
    config_object = AlembicConfig(str(config_file))
    config_object.set_main_option("sqlalchemy.url", get_database_config().uri)
    return config_object


def get_uvicorn_config() -> UvicornConfig:
    return UvicornConfig(
        environ.get(
            "SERVER_FACTORY_PATH",
            "reports.bootstrap.entrypoints.api:bootstrap_application",
        ),
        environ.get("SERVER_HOST", DEFAULT_SERVER_HOST),
        int(environ.get("SERVER_PORT", DEFAULT_SERVER_PORT)),
        factory=True,
    )


@contextmanager
def add_cwd_in_path() -> Generator[None, None, None]:
    cwd = Path.cwd()

    if str(cwd) in sys.path:
        yield
    else:
        sys.path.insert(0, str(cwd))
        try:
            yield
        finally:
            sys.path.remove(str(cwd))


def import_object(object_spec: str) -> Any:
    import_spec = object_spec.split(":")
    if len(import_spec) != 2:
        raise ValueError(
            "Invalid object specification. " "It should be in format '<module>:<object>'"
        )
    with add_cwd_in_path():
        module = import_module(import_spec[0])
    return getattr(module, import_spec[1])


def get_hatchet_worker() -> Worker:
    worker = import_object(
        environ.get(
            "WORKER_FACTORY_PATH", "reports.bootstrap.entrypoints.tasks:bootstrap_worker"
        )
    )

    if isinstance(worker, Worker):
        return worker

    if isinstance(worker, FunctionType):
        worker = worker()

        if not isinstance(worker, Worker):
            raise TypeError("Worker factory function should return instance of Worker")

        return worker

    raise TypeError("Worker factory should be instance of Worker or function")


def build_logger() -> structlog.stdlib.BoundLogger:
    type ProcessorType = Callable[
        [Any, str, MutableMapping[str, Any]],
        Mapping[str, Any] | str | bytes | bytearray | tuple[Any, ...],
    ]

    shared_processors: list[ProcessorType] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    return cast("structlog.stdlib.BoundLogger", structlog.get_logger("reports"))
