from alembic.config import Config as AlembicConfig
from dishka import (
    AsyncContainer,
    Container,
    make_async_container,
    make_container,
)
from dishka.integrations.fastapi import FastapiProvider
from hatchet_sdk import Worker
from socketio import AsyncServer
from structlog.stdlib import BoundLogger as Logger
from uvicorn import Config as UvicornConfig
from uvicorn import Server as UvicornServer

from reports.bootstrap.config import (
    DatabaseConfig,
    GlpiApiConfig,
    S3MinioConfig,
)
from reports.bootstrap.providers import (
    ApiApplicationHandlersProvider,
    ApiConfigProvider,
    ApiDomainAdaptersProvider,
    ApplicationAdaptersProvider,
    AuthProvider,
    BazarioProvider,
    CliConfigProvider,
    InfrastructureAdaptersProvider,
    PersistenceProvider,
    SioConfigProvider,
    WorkerApplicationHandlersProvider,
    WorkerDomainAdaptersProvider,
)


def bootstrap_api_container(
    database_config: DatabaseConfig,
    s3_minio_config: S3MinioConfig,
    glpi_api_config: GlpiApiConfig,
    logger: Logger,
) -> AsyncContainer:
    return make_async_container(
        BazarioProvider(),
        FastapiProvider(),
        ApiConfigProvider(),
        PersistenceProvider(),
        ApiDomainAdaptersProvider(),
        ApplicationAdaptersProvider(),
        ApiApplicationHandlersProvider(),
        InfrastructureAdaptersProvider(),
        AuthProvider(),
        context={
            DatabaseConfig: database_config,
            S3MinioConfig: s3_minio_config,
            GlpiApiConfig: glpi_api_config,
            Logger: logger,
        },
    )


def bootstrap_cli_container(
    alembic_config: AlembicConfig,
    uvicorn_config: UvicornConfig,
    uvicorn_server: UvicornServer,
    hatchet_worker: Worker,
) -> Container:
    return make_container(
        CliConfigProvider(),
        context={
            AlembicConfig: alembic_config,
            UvicornConfig: uvicorn_config,
            UvicornServer: uvicorn_server,
            Worker: hatchet_worker,
        },
    )


def bootstrap_tasks_container(
    database_config: DatabaseConfig,
    sio_server: AsyncServer,
    glpi_api_config: GlpiApiConfig,
    minio_config: S3MinioConfig,
    logger: Logger,
) -> AsyncContainer:
    return make_async_container(
        ApiConfigProvider(),
        WorkerDomainAdaptersProvider(),
        SioConfigProvider(),
        PersistenceProvider(),
        ApplicationAdaptersProvider(),
        WorkerApplicationHandlersProvider(),
        InfrastructureAdaptersProvider(),
        BazarioProvider(),
        context={
            DatabaseConfig: database_config,
            AsyncServer: sio_server,
            GlpiApiConfig: glpi_api_config,
            S3MinioConfig: minio_config,
            Logger: logger,
        },
    )
