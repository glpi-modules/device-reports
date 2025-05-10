from abc import ABC, abstractmethod

from reports.domain.types import UserId


class IdentityProvider(ABC):
    @abstractmethod
    def current_user_id(self) -> UserId: ...
