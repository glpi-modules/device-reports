from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from reports.domain.media.value_objects import MediaMetadata
from reports.domain.types import MediaId, ReportId, UserId

PresignedUrl = NewType("PresignedUrl", str)
FileName = NewType("FileName", str)


@dataclass(frozen=True, kw_only=True, slots=True)
class MediaReadModel:
    media_id: MediaId
    report_id: ReportId
    metadata: MediaMetadata
    uploaded_at: datetime
    presigned_url: PresignedUrl
    uploaded_by: UserId


def build_file_name(content_type: str, media_id: MediaId) -> FileName:
    return FileName(f"{media_id}.{content_type}")
