"""Base classes for message objects."""

from typing import ClassVar, Iterable

import msgpack
from attrs import astuple, frozen


@frozen
class MsgObject:
    """Base class for all message objects."""

    @property
    def data(self) -> tuple:
        """The data of the message object to be serialized."""
        return astuple(self, recurse=False)

    def packb(self) -> bytes:
        """Serialize the message object to bytes in msgpack format."""

        def encode(obj: MsgObject):
            return obj.data

        return msgpack.packb(self, default=encode)  # type: ignore


@frozen
class UnionObject(MsgObject):
    """Base class for all union objects.

    A union object is a message object that can be one of several types.
    """

    TYPE_ID: ClassVar[int]
    """The type ID of the union object."""

    @property
    def data(self) -> tuple:
        """The data of the message object to be serialized."""
        return (self.TYPE_ID, super().data)
