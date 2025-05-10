from collections.abc import Awaitable
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Final, cast

from bazario.asyncio import Sender
from hatchet_sdk import Context
from hatchet_sdk.runnables.task import Task
from hatchet_sdk.runnables.workflow import Workflow
from socketio import AsyncServer  # type: ignore

from reports.application.operations.read.load_media_by_report_id import (
    LoadMediaByReportId,
)
from reports.application.operations.write.generate_pdf_report import GeneratePdfReport
from reports.infrastructure.hatchet_client import HATCHET
from reports.infrastructure.pdf_reports.shemas import CreatePdfReportRequest

if TYPE_CHECKING:
    from dishka import AsyncContainer

REPORTS_WORKFLOW: Final[Workflow] = HATCHET.workflow(
    name="reports", input_validator=CreatePdfReportRequest
)


@REPORTS_WORKFLOW.task(retries=3, name="generate_pdf_report")
async def generate_pdf_report_task(req: CreatePdfReportRequest, ctx: Context) -> None:
    container = cast("AsyncContainer", ctx.lifespan.dishka_container)
    sender = await container.get(Sender)

    await sender.send(request=GeneratePdfReport(device_report_id=req.report_id))


@REPORTS_WORKFLOW.task(
    retries=3, parents=[generate_pdf_report_task], name="load_media_by_report_id"
)
async def load_media_by_report_id_task(
    req: CreatePdfReportRequest, ctx: Context
) -> dict[str, dict[str, Any]]:
    container = cast("AsyncContainer", ctx.lifespan.dishka_container)
    sender = await container.get(Sender)

    media = await sender.send(request=LoadMediaByReportId(device_report_id=req.report_id))
    return {"media": asdict(media)}


@REPORTS_WORKFLOW.task(
    retries=3, parents=[load_media_by_report_id_task], name="emitting_media"
)
async def emitting_media_task(
    req: CreatePdfReportRequest,
    ctx: Context,
) -> None:
    container = cast("AsyncContainer", ctx.lifespan.dishka_container)
    sio = await container.get(AsyncServer)
    media = cast(
        dict[str, dict[str, Any]],
        await ctx.task_output(
            cast(Task[Any, Awaitable[Any]], load_media_by_report_id_task)
        ),
    )

    await sio.emit(event="Pdf Report", data={"report": media}, room=req.report_id)
