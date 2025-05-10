from datetime import UTC, datetime

from reports.application.ports.time_provider import TimeProvider


class UtcTimeProvider(TimeProvider):
    def current(self) -> datetime:
        return datetime.now(UTC)
