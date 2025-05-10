from typing import Annotated

from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from reports.application.common.application_error import ApplicationError
from reports.application.models.pagination import Pagination
from reports.application.models.report import ReportReadModel
from reports.application.operations.read.load_report_by_id import LoadReportById
from reports.application.operations.read.load_reports import LoadReports
from reports.application.operations.write.add_report import AddDeviceReport
from reports.application.operations.write.change_report import ChangeDeviceReport
from reports.application.operations.write.delete_report import DeleteDeviceReport
from reports.domain.types import ReportId
from reports.presentation.api.response_models import ErrorResponse, SuccessResponse

REPORTS_ROUTER = APIRouter(prefix="/reports", tags=["Reports"])


@REPORTS_ROUTER.post(
    path="/",
    responses={
        HTTP_201_CREATED: {"model": SuccessResponse[ReportId]},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_201_CREATED,
)
@inject
async def add_report(
    request: AddDeviceReport, *, sender: FromDishka[Sender]
) -> SuccessResponse[ReportId]:
    report_id = await sender.send(request=request)
    return SuccessResponse(status=HTTP_201_CREATED, result=report_id)


@REPORTS_ROUTER.put(
    path="/{report_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def change_report(
    report_id: ReportId,
    comment: Annotated[str, Body()],
    report_name: Annotated[str, Body()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[None]:
    await sender.send(
        request=ChangeDeviceReport(
            report_id=report_id, comment=comment, report_name=report_name
        )
    )
    return SuccessResponse(status=HTTP_200_OK, result=None)


@REPORTS_ROUTER.delete(
    path="/{report_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_201_CREATED,
)
@inject
async def delete_report(
    report_id: ReportId, *, sender: FromDishka[Sender]
) -> SuccessResponse[None]:
    await sender.send(request=DeleteDeviceReport(report_id=report_id))
    return SuccessResponse(status=HTTP_201_CREATED, result=None)


@REPORTS_ROUTER.get(
    path="/",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[list[ReportReadModel]]},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def load_reports(
    pagination: Annotated[Pagination, Depends()], *, sender: FromDishka[Sender]
) -> SuccessResponse[list[ReportReadModel]]:
    reports = await sender.send(request=LoadReports(pagination=pagination))
    return SuccessResponse(status=HTTP_200_OK, result=reports)


@REPORTS_ROUTER.get(
    path="/{report_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[ReportReadModel]},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def load_report_by_id(
    report_id: ReportId, *, sender: FromDishka[Sender]
) -> SuccessResponse[ReportReadModel]:
    report = await sender.send(request=LoadReportById(report_id=report_id))
    return SuccessResponse(status=HTTP_200_OK, result=report)
