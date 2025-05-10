from pydantic import BaseModel

from reports.domain.types import ReportId


class CreatePdfReportRequest(BaseModel):
    report_id: ReportId
