from bazario.asyncio import HandleNext, PipelineBehavior

from reports.application.operations.write.add_report import AddDeviceReport
from reports.domain.types import ReportId
from reports.infrastructure.pdf_reports.generate_pdf_report import REPORTS_WORKFLOW
from reports.infrastructure.pdf_reports.shemas import CreatePdfReportRequest


class GeneratePdfReportBehavior(PipelineBehavior[AddDeviceReport, ReportId]):
    async def handle(
        self, request: AddDeviceReport, handle_next: HandleNext[AddDeviceReport, ReportId]
    ) -> ReportId:
        report_id = await handle_next(request)

        await REPORTS_WORKFLOW.aio_run_no_wait(
            input=CreatePdfReportRequest(report_id=report_id)
        )

        return report_id
