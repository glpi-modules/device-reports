from dataclasses import dataclass

from reports.domain.shared.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class MediaMetadata(ValueObject):
    file_size: int
    content_type: str
