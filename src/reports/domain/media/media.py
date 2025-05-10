from datetime import datetime

from reports.domain.media.value_objects import MediaMetadata
from reports.domain.shared.entity import Entity
from reports.domain.types import MediaId, ReportId, UserId


class _BaseMedia(Entity[MediaId]):
    def __init__(
        self,
        entity_id: MediaId,
        *,
        uploaded_at: datetime,
        metadata: MediaMetadata,
    ) -> None:
        Entity.__init__(self, entity_id)

        self._uploaded_at = uploaded_at
        self._metadata = metadata

    @property
    def uploaded_at(self) -> datetime:
        return self._uploaded_at

    @property
    def metadata(self) -> MediaMetadata:
        return self._metadata


class ReportMedia(_BaseMedia):
    def __init__(
        self,
        entity_id: MediaId,
        *,
        uploaded_by: UserId,
        uploaded_at: datetime,
        metadata: MediaMetadata,
        report_id: ReportId,
    ) -> None:
        _BaseMedia.__init__(
            self=self, entity_id=entity_id, uploaded_at=uploaded_at, metadata=metadata
        )

        self._report_id = report_id
        self._uploaded_by = uploaded_by

    @property
    def report_id(self) -> ReportId:
        return self._report_id

    @property
    def uploaded_by(self) -> UserId:
        return self._uploaded_by
