"""
models for the event controller
"""

from itertools import pairwise
from uuid import UUID

from pydantic import BaseModel, RootModel


class EventHeader(BaseModel):
    """
    model returned by /api/Event/prozess/<id goes here>
    """

    number: int
    name: str
    id: UUID


class EventHeaders(RootModel[list[EventHeader]]):
    """wrapper around a list of EventHeaders"""

    @property
    def is_continuous(self) -> bool:
        """
        returns true iff all event numbers are continuous.
        a gap like: 1,2,3,5 indicates that there is a problem with the event at position 4
        """
        number_pairs = pairwise(sorted((x.number for x in self.root)))
        return all(abs(x - y) == 1 for x, y in number_pairs)


__all__ = ["EventHeader", "EventHeaders"]
