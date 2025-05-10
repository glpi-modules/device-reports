from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from reports.application.models.media import MediaReadModel, build_file_name
from reports.application.ports.media_gateway import MediaGateway, ObjectMediaGateway
from reports.domain.media.value_objects import MediaMetadata
from reports.domain.types import ReportId
from reports.infrastructure.persistence.sql_tables import REPORT_MEDIA_TABLE


class SqlMediaGateway(MediaGateway):
    def __init__(
        self, session: AsyncSession, object_media_gateway: ObjectMediaGateway
    ) -> None:
        self._session = session
        self._object_media_gateway = object_media_gateway

    async def with_report_id(self, report_id: ReportId) -> MediaReadModel | None:
        query = select(REPORT_MEDIA_TABLE).where(
            REPORT_MEDIA_TABLE.c.report_id == report_id
        )
        cursor_result = await self._session.execute(query)
        cursor_row = cursor_result.fetchone()

        if not cursor_row:
            return None

        return await self._load(cursor_row)

    async def _load(self, cursor_row: Row) -> MediaReadModel:
        return MediaReadModel(
            media_id=cursor_row.media_id,
            report_id=cursor_row.report_id,
            uploaded_at=cursor_row.uploaded_at,
            uploaded_by=cursor_row.uploaded_by,
            metadata=MediaMetadata(
                file_size=cursor_row.file_size,
                content_type=cursor_row.content_type,
            ),
            presigned_url=await self._object_media_gateway.get(
                build_file_name(
                    content_type=cursor_row.content_type,
                    media_id=cursor_row.media_id,
                )
            ),
        )
