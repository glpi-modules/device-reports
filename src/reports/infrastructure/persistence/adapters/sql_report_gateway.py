from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from reports.application.models.media import MediaReadModel, build_file_name
from reports.application.models.pagination import Pagination
from reports.application.models.report import ReportReadModel
from reports.application.ports.media_gateway import ObjectMediaGateway
from reports.application.ports.report_gateway import ReportGateway
from reports.domain.media.value_objects import MediaMetadata
from reports.domain.types import ReportId
from reports.infrastructure.persistence.sql_tables import (
    DEVICE_REPORT_TABLE,
    REPORT_MEDIA_TABLE,
)


class SqlReportGateway(ReportGateway):
    def __init__(
        self, session: AsyncSession, object_media_gateway: ObjectMediaGateway
    ) -> None:
        self._session = session
        self._object_media_gateway = object_media_gateway

    async def load_many(self, pagination: Pagination) -> list[ReportReadModel]:
        stmt = (
            select(DEVICE_REPORT_TABLE, REPORT_MEDIA_TABLE)
            .join(
                REPORT_MEDIA_TABLE,
                REPORT_MEDIA_TABLE.c.report_id == DEVICE_REPORT_TABLE.c.report_id,
                isouter=True,
            )
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        result = (await self._session.execute(stmt)).all()
        return [await self._load(row) for row in result]

    async def with_id(self, report_id: ReportId) -> ReportReadModel | None:
        stmt = (
            select(DEVICE_REPORT_TABLE, REPORT_MEDIA_TABLE)
            .join(
                REPORT_MEDIA_TABLE,
                REPORT_MEDIA_TABLE.c.report_id == DEVICE_REPORT_TABLE.c.report_id,
                isouter=True,
            )
            .where(DEVICE_REPORT_TABLE.c.report_id == report_id)
        )
        row = (await self._session.execute(stmt)).one_or_none()

        if not row:
            return None

        return await self._load(row)

    async def _load(self, row: Row) -> ReportReadModel:
        media: MediaReadModel | None = None

        if row.media_id:
            file_name = build_file_name(
                content_type=row.content_type, media_id=row.media_id
            )
            media = MediaReadModel(
                media_id=row.media_id,
                report_id=row.report_id,
                uploaded_at=row.uploaded_at,
                uploaded_by=row.uploaded_by,
                metadata=MediaMetadata(
                    file_size=row.file_size,
                    content_type=row.content_type,
                ),
                presigned_url=await self._object_media_gateway.get(file_name),
            )

        return ReportReadModel(
            report_id=row.report_id,
            creator_id=row.creator_id,
            comment=row.comment,
            created_at=row.created_at,
            report_name=row.report_name,
            device_id=row.device_id,
            device_type=row.device_type,
            media=media,
        )
