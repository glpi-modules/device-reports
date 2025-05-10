from typing import Final
from uuid import UUID

from fastapi import Request

from reports.application.common.application_error import ApplicationError, ErrorType
from reports.application.ports.identity_provider import IdentityProvider
from reports.domain.types import UserId


class HttpIdentityProvider(IdentityProvider):
    _USER_ID_HEADER: Final[str] = "X-User-Id"

    def __init__(self, request: Request) -> None:
        self._request = request

    def current_user_id(self) -> UserId:
        user_id = self._request.headers.get(self._USER_ID_HEADER)

        if not user_id:
            raise ApplicationError(
                message="User not provided", error_type=ErrorType.UNAUTHORIZED
            )

        return UserId(UUID(user_id))
