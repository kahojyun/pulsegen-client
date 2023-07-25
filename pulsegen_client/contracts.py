"""Data contracts for the pulsegen service."""

import enum as _enum
import typing as _typing

import attrs as _attrs
import msgpack as _msgpack


@_attrs.frozen
class MsgObject:
    """Base class for all message objects."""

    @property
    def data(self) -> tuple:
        """The data of the message object to be serialized."""
        return _attrs.astuple(self, recurse=False)

    def packb(self) -> bytes:
        """Serialize the message object to bytes in msgpack format."""

        def encode(obj: _typing.Union[MsgObject, _enum.Enum]):
            if isinstance(obj, MsgObject):
                return obj.data
            if isinstance(obj, _enum.Enum):
                return obj.value
            raise TypeError(f"Cannot encode object of type {type(obj)}")

        return _msgpack.packb(self, default=encode)  # type: ignore


@_attrs.frozen
class UnionObject(MsgObject):
    """Base class for all union objects.

    A union object is a message object that can be one of several types.
    """

    TYPE_ID: _typing.ClassVar[int]
    """The type ID of the union object."""

    @property
    def data(self) -> tuple:
        return (self.TYPE_ID, super().data)


@_attrs.frozen
class ChannelInfo(MsgObject):
    """Information about a channel.

    :param name: The name of the channel.
    :param base_freq: The base frequency of the channel.
    :param sample_rate: The sample rate of the channel.
    :param delay: The delay of the channel.
    :param length: The length of the channel.
    :param align_level: The alignment level of the channel.
    """

    name: str
    """The name of the channel."""
    base_freq: float
    """The base frequency of the channel."""
    sample_rate: float
    """The sample rate of the channel."""
    delay: float
    """The delay of the channel."""
    length: int
    """The length of the channel."""
    align_level: int
    """The alignment level of the channel."""


class DataType(_enum.Enum):
    """Data types for waveforms."""

    FLOAT32 = 0
    """32-bit floating point."""
    FLOAT64 = 1
    """64-bit floating point."""
