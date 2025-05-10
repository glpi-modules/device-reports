from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.common.markers import Command
from reports.application.models.media import FileName, build_file_name
from reports.application.ports.device_gateway import DeviceGateway
from reports.application.ports.media_gateway import ObjectMediaGateway
from reports.application.ports.report_pdf_generator import PdfReportGenerator
from reports.domain.media.factory import MediaFactory
from reports.domain.media.repository import MediaRepository
from reports.domain.report.repository import ReportRepository
from reports.domain.types import ReportId


@dataclass(frozen=True)
class GeneratePdfReport(Command[FileName]):
    device_report_id: ReportId


class GeneratePdfReportHandler(RequestHandler[GeneratePdfReport, FileName]):
    def __init__(
        self,
        media_factory: MediaFactory,
        media_repository: MediaRepository,
        pdf_report_generator: PdfReportGenerator,
        media_gateway: ObjectMediaGateway,
        report_repository: ReportRepository,
        device_gateway: DeviceGateway,
    ) -> None:
        self._media_factory = media_factory
        self._media_repository = media_repository
        self._pdf_report_generator = pdf_report_generator
        self._media_gateway = media_gateway
        self._report_repository = report_repository
        self._device_gateway = device_gateway

    async def handle(self, request: GeneratePdfReport) -> FileName:
        if await self._media_repository.with_report_id(
            report_id=request.device_report_id
        ):
            raise ApplicationError(
                error_type=ErrorType.CONFLICT,
                message=f"Report with id {request.device_report_id} already exists",
            )

        report = await self._report_repository.device_report_with_id(
            report_id=request.device_report_id
        )

        if not report:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Report with id {request.device_report_id} not found",
            )

        device = await self._device_gateway.load(
            device_id=report.device_id, device_type=report.device_type
        )

        if not device:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Device with id {report.device_id} \
                    and type {report.device_type} not found",
            )

        pdf_report = self._pdf_report_generator.generate(device=device)
        media = await self._media_factory.create_report_media(
            request.device_report_id, pdf_report.metadata, report.creator_id
        )
        filename = build_file_name(
            content_type=pdf_report.metadata.content_type, media_id=media.entity_id
        )

        self._media_repository.add(media=media)
        await self._media_gateway.save(file_name=filename, file=pdf_report.file)

        return filename
