from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reports.domain.media.media import ReportMedia, _BaseMedia
from reports.domain.media.repository import MediaRepository
from reports.domain.types import ReportId
from reports.infrastructure.persistence.sql_tables import REPORT_MEDIA_TABLE


class SqlMediaRepository(MediaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, media: _BaseMedia) -> None:
        self._session.add(media)

    async def delete(self, media: _BaseMedia) -> None:
        await self._session.delete(media)

    async def with_report_id(self, report_id: ReportId) -> ReportMedia | None:
        stmt = select(ReportMedia).where(REPORT_MEDIA_TABLE.c.report_id == report_id)
        media = (await self._session.execute(stmt)).scalar_one_or_none()

        return media
