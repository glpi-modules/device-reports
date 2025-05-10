from dataclasses import asdict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from reports.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from reports.presentation.api.response_models import ErrorData, ErrorResponse

STATUS_MAP = {
    ErrorType.NOT_FOUND: HTTP_404_NOT_FOUND,
    ErrorType.VALIDATION_ERROR: HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorType.APPLICATION_ERROR: HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorType.UNAUTHORIZED: HTTP_401_UNAUTHORIZED,
}


async def application_error_handler(_: Request, exception: ApplicationError) -> Response:
    error_data = ErrorData[None](exception.message)
    status_code = STATUS_MAP[exception.error_type]
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)


async def internal_error_handler(_: Request, exception: Exception) -> Response:
    error_data = ErrorData[None](str(exception))
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)
