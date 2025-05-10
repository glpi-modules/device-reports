from bazario.asyncio import HandleNext, PipelineBehavior

from reports.application.ports.time_provider import TimeProvider
from reports.domain.shared.events import DomainEvent


class EventDateSetterBehavior(PipelineBehavior[DomainEvent, None]):
    def __init__(self, time_provider: TimeProvider) -> None:
        self._time_provider = time_provider

    async def handle(
        self,
        request: DomainEvent,
        handle_next: HandleNext[DomainEvent, None],
    ) -> None:
        request.set_event_date(
            self._time_provider.current(),
        )

        return await handle_next(request)
