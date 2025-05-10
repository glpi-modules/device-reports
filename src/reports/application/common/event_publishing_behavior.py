from bazario.asyncio import HandleNext, PipelineBehavior, Publisher

from reports.application.common.markers import Command
from reports.application.ports.events import EventsRaiser


class EventPublishingBehavior[C: Command, R](PipelineBehavior[C, R]):
    def __init__(
        self,
        publisher: Publisher,
        events_raiser: EventsRaiser,
    ) -> None:
        self._publisher = publisher
        self._events_raiser = events_raiser

    async def handle(self, request: C, handle_next: HandleNext[C, R]) -> R:
        response = await handle_next(request)

        for event in self._events_raiser.raise_events():
            await self._publisher.publish(event)

        return response
