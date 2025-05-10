from datetime import timedelta
from typing import Any, Final, NewType

from httpx import AsyncClient, HTTPStatusError, RequestError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from reports.application.common.application_error import ApplicationError, ErrorType

SessionToken = NewType("SessionToken", str)
UserToken = NewType("UserToken", str)


class GlpiAuthClient:
    def __init__(self, client: AsyncClient, user_token: UserToken) -> None:
        self._client = client
        self._user_token = user_token
        self._session_token: SessionToken | None = None

    @retry(
        retry=retry_if_exception_type((RequestError, HTTPStatusError)),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
        stop=stop_after_attempt(5),
    )
    async def __aenter__(self) -> SessionToken:
        _headers = {"Authorization": f"user_token {self._user_token}"}
        response = await self._client.get(url="/initSession", headers=_headers)

        data: dict[str, str] = response.json()

        if response.status_code != 200 or not data.get("session_token"):
            raise ApplicationError(
                error_type=ErrorType.UNAUTHORIZED,
                message="Failed to authenticate with GLPI API",
            )

        self._change_token_value(session_token := SessionToken(data["session_token"]))

        return session_token

    @retry(
        retry=retry_if_exception_type((RequestError, HTTPStatusError)),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
        stop=stop_after_attempt(5),
    )
    async def __aexit__(self, *args: object, **kwargs: dict[Any, Any]) -> None:
        if not self._session_token:
            raise ValueError("Session token is not set")

        _headers: Final[dict[str, str]] = {"Session-Token": self._session_token}

        await self._client.get(url="/killSession", headers=_headers)

        self._change_token_value(token=None)

    def _change_token_value(self, token: SessionToken | None) -> None:
        self._session_token = token
