from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ValueObject):
            return NotImplemented

        return self.__dict__ == value.__dict__
