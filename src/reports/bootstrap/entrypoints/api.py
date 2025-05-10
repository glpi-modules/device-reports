from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, cast

from dishka.integrations.fastapi import (
    setup_dishka as add_container_to_fastapi,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from reports.application.common.application_error import ApplicationError
from reports.bootstrap.config import (
    build_logger,
    get_database_config,
    get_glpi_api_config,
    get_s3_minio_config,
)
from reports.bootstrap.containers import bootstrap_api_container
from reports.bootstrap.entrypoints.sio import socket_io_app, socketio_server
from reports.infrastructure.persistence.mappings import map_tables
from reports.presentation.api.exception_handlers import (
    application_error_handler,
    internal_error_handler,
)
from reports.presentation.api.routers.healthcheck import HEALTHCHECK_ROUTER
from reports.presentation.api.routers.reports import REPORTS_ROUTER

if TYPE_CHECKING:
    from dishka import AsyncContainer
    from starlette.types import HTTPExceptionHandler


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    map_tables()
    container = cast("AsyncContainer", application.state.dishka_container)
    yield
    await container.close()


def add_middlewares(application: FastAPI) -> None:
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


def add_api_routers(application: FastAPI) -> None:
    application.include_router(HEALTHCHECK_ROUTER)
    application.include_router(REPORTS_ROUTER)


def add_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(
        ApplicationError,
        cast("HTTPExceptionHandler", application_error_handler),
    )
    application.add_exception_handler(
        Exception,
        cast("HTTPExceptionHandler", internal_error_handler),
    )


def bootstrap_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    sio_server = socketio_server()
    dishka_container = bootstrap_api_container(
        database_config=get_database_config(),
        s3_minio_config=get_s3_minio_config(),
        glpi_api_config=get_glpi_api_config(),
        logger=build_logger(),
    )
    socket_io_app(application, sio_server)

    add_middlewares(application)
    add_api_routers(application)
    add_exception_handlers(application)
    add_container_to_fastapi(dishka_container, application)

    return application
