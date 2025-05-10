from collections.abc import AsyncIterator

from aioboto3 import Session
from alembic.config import Config as AlembicConfig
from bazario.asyncio import Dispatcher, Registry
from bazario.asyncio.resolvers.dishka import DishkaResolver
from dishka import (
    Provider,
    Scope,
    WithParents,
    alias,
    from_context,
    provide,
    provide_all,
)
from hatchet_sdk import Worker
from httpx import AsyncClient
from socketio import AsyncServer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from structlog.stdlib import BoundLogger as Logger
from types_aiobotocore_s3.client import S3Client
from uvicorn import Config as UvicornConfig
from uvicorn import Server as UvicornServer

from reports.application.common.commition_behavior import (
    CommitionBehavior,
)
from reports.application.common.event_date_setter_behavior import EventDateSetterBehavior
from reports.application.common.event_id_generation_behavior import (
    EventIdGenerationBehavior,
)
from reports.application.common.event_publishing_behavior import EventPublishingBehavior
from reports.application.common.markers import Command
from reports.application.operations.events.delete_media_on_report_deletion import (
    DeleteMediaOnReportDeletionHandler,
)
from reports.application.operations.read.load_media_by_report_id import (
    LoadMediaByReportId,
    LoadMediaByReportIdHandler,
)
from reports.application.operations.read.load_report_by_id import (
    LoadReportById,
    LoadReportByIdHandler,
)
from reports.application.operations.read.load_reports import (
    LoadReports,
    LoadReportsHandler,
)
from reports.application.operations.write.add_report import (
    AddDeviceReport,
    AddDeviceReportHandler,
)
from reports.application.operations.write.change_report import (
    ChangeDeviceReport,
    ChangeDeviceReportHandler,
)
from reports.application.operations.write.delete_report import (
    DeleteDeviceReport,
    DeleteDeviceReportHandler,
)
from reports.application.operations.write.generate_pdf_report import (
    GeneratePdfReport,
    GeneratePdfReportHandler,
)
from reports.application.ports.transaction import Transaction
from reports.bootstrap.config import DatabaseConfig, GlpiApiConfig, S3MinioConfig
from reports.domain.media.events import (
    ReportMediaDeleted,
    ReportMediaGenerated,
)
from reports.domain.report.events import (
    DeviceReportCreated,
    ReportCommentChanged,
    ReportDeleted,
    ReportNameChanged,
)
from reports.domain.shared.events import DomainEvent
from reports.infrastructure.events import DomainEvents
from reports.infrastructure.http.http_device_gateway import HttpDeviceGateway
from reports.infrastructure.http.http_glpi_auth_client import GlpiAuthClient, UserToken
from reports.infrastructure.media_factory import MediaFactoryImpl
from reports.infrastructure.pdf_reports.adapters.pdf_report_generator import (
    PdfReportGeneratorImpl,
)
from reports.infrastructure.pdf_reports.pdf_report_behavior import (
    GeneratePdfReportBehavior,
)
from reports.infrastructure.pdf_reports.templates_loader import TemplatesLoader
from reports.infrastructure.persistence.adapters.blob_media_gateway import (
    BlobMediaGateway,
)
from reports.infrastructure.persistence.adapters.sql_media_gateway import SqlMediaGateway
from reports.infrastructure.persistence.adapters.sql_media_repository import (
    SqlMediaRepository,
)
from reports.infrastructure.persistence.adapters.sql_report_gateway import (
    SqlReportGateway,
)
from reports.infrastructure.persistence.adapters.sql_report_repository import (
    SqlReportRepository,
)
from reports.infrastructure.report_factory import ReportFactoryImlp
from reports.infrastructure.utc_time_provider import UtcTimeProvider
from reports.infrastructure.uuid7_id_generator import UUID7IdGenerator
from reports.presentation.api.htpp_identity_provider import HttpIdentityProvider
from reports.presentation.logging.media import (
    LogReportMediaCreatedNotHandler,
    LogReportMediaDeletedNotHandler,
)
from reports.presentation.logging.reports import (
    LogReportCommentChangedNotHandler,
    LogReportCreatedNotHandler,
    LogReportDeletedNotHandler,
    LogReportNameChangedNotHandler,
)


class ApiConfigProvider(Provider):
    scope = Scope.APP

    database_config = from_context(DatabaseConfig)
    s3_minio_config = from_context(S3MinioConfig)
    glpi_api_config = from_context(GlpiApiConfig)
    logger = from_context(Logger)


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(self, postgres_config: DatabaseConfig) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(postgres_config.uri)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False, autoflush=True)

    @provide(provides=AsyncSession)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.APP)
    def s3_session(self, config: S3MinioConfig) -> Session:
        return Session(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    @provide(scope=Scope.REQUEST)
    async def s3_client(
        self, session: Session, config: S3MinioConfig
    ) -> AsyncIterator[S3Client]:
        async with session.client(
            service_name="s3", endpoint_url=config.base_uri
        ) as client:
            yield client


class ApiDomainAdaptersProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SqlMediaRepository],  # type: ignore[misc]
        WithParents[SqlReportRepository],  # type: ignore[misc]
    )
    post_factory = provide(WithParents[ReportFactoryImlp])  # type: ignore[misc]
    media_factory = provide(WithParents[MediaFactoryImpl])  # type: ignore[misc]


class WorkerDomainAdaptersProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SqlMediaRepository],  # type: ignore[misc]
        WithParents[SqlReportRepository],  # type: ignore[misc]
    )
    media_factory = provide(WithParents[MediaFactoryImpl])  # type: ignore[misc]


class ApplicationAdaptersProvider(Provider):
    scope = Scope.REQUEST

    gateways = provide_all(
        WithParents[SqlMediaGateway],  # type: ignore[misc]
        WithParents[BlobMediaGateway],  # type: ignore[misc]
        WithParents[HttpDeviceGateway],  # type: ignore[misc]
        WithParents[SqlReportGateway],  # type: ignore[misc]
    )
    id_generator = provide(
        WithParents[UUID7IdGenerator],  # type: ignore[misc]
        scope=Scope.APP,
    )
    time_provider = provide(
        WithParents[UtcTimeProvider],  # type: ignore[misc]
        scope=Scope.APP,
    )
    transaction = alias(AsyncSession, provides=Transaction)
    report_generator = provide(WithParents[PdfReportGeneratorImpl])  # type: ignore[misc]
    domain_events = provide(WithParents[DomainEvents])  # type: ignore[misc]


class AuthProvider(Provider):
    scope = Scope.REQUEST

    identity_provider = provide(
        WithParents[HttpIdentityProvider],  # type: ignore[misc]
    )


class InfrastructureAdaptersProvider(Provider):
    scope = Scope.REQUEST

    transaction = alias(AsyncSession, provides=Transaction)
    templates_loader = provide(WithParents[TemplatesLoader])  # type: ignore[misc]

    @provide(scope=Scope.APP)
    async def http_client(self, config: GlpiApiConfig) -> AsyncIterator[AsyncClient]:
        async with AsyncClient(base_url=config.glpi_uri) as client:
            yield client

    @provide
    async def glpi_auth_client(
        self, http_client: AsyncClient, config: GlpiApiConfig
    ) -> GlpiAuthClient:
        return GlpiAuthClient(client=http_client, user_token=UserToken(config.user_token))


class ApiApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        LoadMediaByReportIdHandler,
        AddDeviceReportHandler,
        LogReportCommentChangedNotHandler,
        LogReportCreatedNotHandler,
        LogReportNameChangedNotHandler,
        LogReportDeletedNotHandler,
        LogReportMediaDeletedNotHandler,
        DeleteMediaOnReportDeletionHandler,
        DeleteDeviceReportHandler,
        ChangeDeviceReportHandler,
        LoadReportsHandler,
        LoadReportByIdHandler,
    )
    behaviors = provide_all(
        CommitionBehavior,
        GeneratePdfReportBehavior,
        EventDateSetterBehavior,
        EventIdGenerationBehavior,
        EventPublishingBehavior,
    )


class WorkerApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        LoadMediaByReportIdHandler,
        GeneratePdfReportHandler,
        LogReportMediaCreatedNotHandler,
        LogReportMediaDeletedNotHandler,
    )
    behaviors = provide_all(
        CommitionBehavior,
        EventDateSetterBehavior,
        EventIdGenerationBehavior,
        EventPublishingBehavior,
    )


class BazarioProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def registry(self) -> Registry:
        registry = Registry()

        registry.add_request_handler(LoadReportById, LoadReportByIdHandler)
        registry.add_request_handler(LoadReports, LoadReportsHandler)
        registry.add_request_handler(LoadMediaByReportId, LoadMediaByReportIdHandler)
        registry.add_request_handler(GeneratePdfReport, GeneratePdfReportHandler)
        registry.add_request_handler(AddDeviceReport, AddDeviceReportHandler)
        registry.add_request_handler(ChangeDeviceReport, ChangeDeviceReportHandler)
        registry.add_request_handler(DeleteDeviceReport, DeleteDeviceReportHandler)
        registry.add_notification_handlers(
            ReportDeleted, DeleteMediaOnReportDeletionHandler
        )
        registry.add_notification_handlers(
            ReportMediaGenerated, LogReportMediaCreatedNotHandler
        )
        registry.add_notification_handlers(
            DeviceReportCreated, LogReportCreatedNotHandler
        )
        registry.add_notification_handlers(
            ReportNameChanged, LogReportNameChangedNotHandler
        )
        registry.add_notification_handlers(
            ReportCommentChanged, LogReportCommentChangedNotHandler
        )
        registry.add_notification_handlers(ReportDeleted, LogReportDeletedNotHandler)
        registry.add_notification_handlers(
            ReportMediaDeleted, LogReportMediaDeletedNotHandler
        )
        registry.add_pipeline_behaviors(AddDeviceReport, GeneratePdfReportBehavior)
        registry.add_pipeline_behaviors(
            DomainEvent, EventDateSetterBehavior, EventIdGenerationBehavior
        )
        registry.add_pipeline_behaviors(
            Command,
            EventPublishingBehavior,
            CommitionBehavior,
        )
        return registry

    resolver = provide(WithParents[DishkaResolver])  # type: ignore[misc]
    dispatcher = provide(WithParents[Dispatcher])  # type: ignore[misc]


class CliConfigProvider(Provider):
    scope = Scope.APP

    alembic_config = from_context(AlembicConfig)
    uvicorn_config = from_context(UvicornConfig)
    uvicorn_server = from_context(UvicornServer)
    hatchet_worker = from_context(Worker)


class SioConfigProvider(Provider):
    scope = Scope.APP

    sio = from_context(AsyncServer)
