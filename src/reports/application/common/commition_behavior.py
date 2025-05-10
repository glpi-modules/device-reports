from bazario.asyncio import HandleNext, PipelineBehavior

from reports.application.common.markers import Command
from reports.application.ports.transaction import Transaction


class CommitionBehavior[C: Command, R](PipelineBehavior[C, R]):
    def __init__(self, transaction: Transaction) -> None:
        self._transaction = transaction

    async def handle(self, request: C, handle_next: HandleNext[C, R]) -> R:
        response = await handle_next(request)

        await self._transaction.commit()

        return response
