from collections.abc import AsyncGenerator

from dishka import AsyncContainer, Scope
from hatchet_sdk.worker.worker import Worker
from pydantic import BaseModel, ConfigDict

from reports.bootstrap.config import (
    build_logger,
    get_database_config,
    get_glpi_api_config,
    get_s3_minio_config,
)
from reports.bootstrap.containers import bootstrap_tasks_container
from reports.bootstrap.entrypoints.sio import socketio_server
from reports.infrastructure.hatchet_client import build_hacthcet_client_config
from reports.infrastructure.pdf_reports.generate_pdf_report import REPORTS_WORKFLOW
from reports.infrastructure.persistence.mappings import map_tables


class Lifespan(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dishka_container: AsyncContainer


async def lifespan() -> AsyncGenerator[Lifespan, None]:
    map_tables()
    dishka_container = bootstrap_tasks_container(
        database_config=get_database_config(),
        sio_server=socketio_server(),
        glpi_api_config=get_glpi_api_config(),
        minio_config=get_s3_minio_config(),
        logger=build_logger(),
    )

    async with dishka_container(scope=Scope.REQUEST) as req_container:
        yield Lifespan(dishka_container=req_container)


def bootstrap_worker() -> Worker:
    worker = Worker(
        name="Worker",
        config=build_hacthcet_client_config(),
        slots=20,
        durable_slots=5,
        lifespan=lifespan,
        workflows=[REPORTS_WORKFLOW],
    )

    return worker
