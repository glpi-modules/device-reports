from datetime import timedelta
from typing import Final

from tenacity import retry, stop_after_attempt, wait_exponential
from types_aiobotocore_s3.client import S3Client

from reports.application.models.media import FileName, PresignedUrl
from reports.application.ports.media_gateway import ObjectMediaGateway


class BlobMediaGateway(ObjectMediaGateway):
    _BUCKET_NAME: Final[str] = "media"

    def __init__(self, client: S3Client) -> None:
        self._client = client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
    )
    async def save(self, file_name: FileName, file: bytes) -> None:
        await self._client.put_object(
            Bucket=self._BUCKET_NAME, Key=str(file_name), Body=file
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
    )
    async def get(self, file_name: FileName) -> PresignedUrl:
        presigned_url = await self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self._BUCKET_NAME, "Key": file_name},
            ExpiresIn=3600,
        )

        return PresignedUrl(presigned_url)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=timedelta(seconds=3), max=10),
    )
    async def delete(self, file_name: FileName) -> None:
        await self._client.delete_object(Bucket=self._BUCKET_NAME, Key=file_name)
