from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reports.application.ports.events import EventAdder
from reports.domain.report.report import DeviceReport
from reports.domain.report.repository import ReportRepository
from reports.domain.types import ReportId
from reports.infrastructure.persistence.sql_tables import DEVICE_REPORT_TABLE
from reports.infrastructure.report_proxy import DeviceReportProxy


class SqlReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession, event_adder: EventAdder) -> None:
        self._session = session
        self._event_adder = event_adder

    def add(self, report: DeviceReport) -> None:
        proxy = cast(DeviceReportProxy, report)
        self._session.add(proxy.device_report)

    async def delete(self, report: DeviceReport) -> None:
        proxy = cast(DeviceReportProxy, report)
        await self._session.delete(proxy.device_report)

    async def with_device_id(self, device_id: ReportId) -> list[DeviceReport]:
        stmt = select(DeviceReport).where(DEVICE_REPORT_TABLE.c.device_id == device_id)
        reports = (await self._session.execute(stmt)).scalars().all()

        return [
            cast(DeviceReport, DeviceReportProxy(report, self._event_adder))
            for report in reports
        ]

    async def device_report_with_id(self, report_id: ReportId) -> DeviceReport | None:
        stmt = select(DeviceReport).where(DEVICE_REPORT_TABLE.c.report_id == report_id)
        report = (await self._session.execute(stmt)).scalar_one_or_none()

        if not report:
            return None

        return cast(DeviceReport, DeviceReportProxy(report, self._event_adder))
