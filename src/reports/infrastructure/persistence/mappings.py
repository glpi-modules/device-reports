from sqlalchemy.orm import composite

from reports.domain.media.media import ReportMedia
from reports.domain.media.value_objects import MediaMetadata
from reports.domain.report.report import DeviceReport
from reports.infrastructure.persistence.sql_tables import (
    DEVICE_REPORT_TABLE,
    MAPPER_REGISTRY,
    REPORT_MEDIA_TABLE,
)


def map_device_report_table() -> None:
    MAPPER_REGISTRY.map_imperatively(
        DeviceReport,
        DEVICE_REPORT_TABLE,
        properties={
            "_entity_id": DEVICE_REPORT_TABLE.c.report_id,
            "_report_name": DEVICE_REPORT_TABLE.c.report_name,
            "_creator_id": DEVICE_REPORT_TABLE.c.creator_id,
            "_comment": DEVICE_REPORT_TABLE.c.comment,
            "_created_at": DEVICE_REPORT_TABLE.c.created_at,
            "_device_id": DEVICE_REPORT_TABLE.c.device_id,
            "_device_type": DEVICE_REPORT_TABLE.c.device_type,
        },
    )


def map_report_media_table() -> None:
    MAPPER_REGISTRY.map_imperatively(
        ReportMedia,
        REPORT_MEDIA_TABLE,
        properties={
            "_entity_id": REPORT_MEDIA_TABLE.c.media_id,
            "_uploaded_at": REPORT_MEDIA_TABLE.c.uploaded_at,
            "_metadata": composite(
                MediaMetadata,
                REPORT_MEDIA_TABLE.c.file_size,
                REPORT_MEDIA_TABLE.c.content_type,
            ),
            "_report_id": REPORT_MEDIA_TABLE.c.report_id,
            "_uploaded_by": REPORT_MEDIA_TABLE.c.uploaded_by,
        },
    )


def map_tables() -> None:
    map_device_report_table()
    map_report_media_table()
