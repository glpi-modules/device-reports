from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, MetaData, Table, Text
from sqlalchemy.orm import registry

METADATA = MetaData()
MAPPER_REGISTRY = registry(metadata=METADATA)


DEVICE_REPORT_TABLE = Table(
    "device_report",
    METADATA,
    Column("report_id", UUID, primary_key=True),
    Column("report_name", Text, nullable=False),
    Column("creator_id", UUID, nullable=False),
    Column("comment", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("device_id", Integer, nullable=False),
    Column("device_type", Text, nullable=False),
)


REPORT_MEDIA_TABLE = Table(
    "report_media",
    METADATA,
    Column("media_id", UUID, primary_key=True),
    Column("uploaded_at", DateTime(timezone=True), nullable=False),
    Column("file_size", Integer, nullable=False),
    Column("content_type", Text, nullable=False),
    Column("report_id", ForeignKey("device_report.report_id"), nullable=False),
    Column("uploaded_by", UUID, nullable=False),
)
