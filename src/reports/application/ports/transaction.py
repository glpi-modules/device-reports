from abc import ABC, abstractmethod


class Transaction(ABC):
    @abstractmethod
    async def commit(self) -> None: ...
    @abstractmethod
    async def flush(self) -> None: ...
