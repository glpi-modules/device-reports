from io import BytesIO
from typing import Final

from weasyprint import HTML  # type: ignore

from reports.application.models.device import DeviceReadModel
from reports.application.ports.report_pdf_generator import PdfReport, PdfReportGenerator
from reports.domain.media.value_objects import MediaMetadata
from reports.infrastructure.pdf_reports.templates_loader import TemplatesLoader


class PdfReportGeneratorImpl(PdfReportGenerator):
    _PDF_CONTENT_TYPE: Final[str] = "pdf"

    def __init__(self, loader: TemplatesLoader) -> None:
        self._loader = loader

    def generate(self, device: DeviceReadModel) -> PdfReport:
        report_template = self._loader.get_report_template()
        html_content = report_template.render(device=device)

        with BytesIO() as buffer:
            HTML(string=html_content).write_pdf(buffer)
            pdf_bytes = buffer.getvalue()

        return self._load(
            media_metadata=MediaMetadata(
                file_size=len(pdf_bytes), content_type=self._PDF_CONTENT_TYPE
            ),
            file=pdf_bytes,
        )

    def _load(self, media_metadata: MediaMetadata, file: bytes) -> PdfReport:
        return PdfReport(metadata=media_metadata, file=file)
