from collections.abc import Hashable


class Entity[TEntityID: Hashable]:
    def __init__(
        self,
        entity_id: TEntityID,
    ) -> None:
        self._entity_id = entity_id

    @property
    def entity_id(self) -> TEntityID:
        return self._entity_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return bool(other.entity_id == self.entity_id)

    def __hash__(self) -> int:
        return hash(self.entity_id)
