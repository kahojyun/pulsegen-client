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
class Biquad(MsgObject):
    """A biquad filter.

    :param b0: The b0 coefficient.
    :param b1: The b1 coefficient.
    :param b2: The b2 coefficient.
    :param a1: The a1 coefficient.
    :param a2: The a2 coefficient.
    """

    b0: float
    """The b0 coefficient."""
    b1: float
    """The b1 coefficient."""
    b2: float
    """The b2 coefficient."""
    a1: float
    """The a1 coefficient."""
    a2: float
    """The a2 coefficient."""


@_attrs.frozen
class IqCalibration(MsgObject):
    """IQ calibration data.

    The calibration data consists of a 2x2 transformation matrix and an 2x1 offset
    vector. The transformation matrix is applied first, followed by the offset vector.

    .. math::
        \\begin{bmatrix}
            I_{out} \\\\
            Q_{out}
        \\end{bmatrix} =
        \\begin{bmatrix}
            a & b \\\\
            c & d
        \\end{bmatrix}
        \\begin{bmatrix}
            I_{in} \\\\
            Q_{in}
        \\end{bmatrix} +
        \\begin{bmatrix}
            i_{offset} \\\\
            q_{offset}
        \\end{bmatrix}

    
    :param a: The a coefficient.
    :param b: The b coefficient.
    :param c: The c coefficient.
    :param d: The d coefficient.
    :param i_offset: The I offset.
    :param q_offset: The Q offset.
    """

    a: float
    """The a coefficient."""
    b: float
    """The b coefficient."""
    c: float
    """The c coefficient."""
    d: float
    """The d coefficient."""
    i_offset: float = 0
    """The I offset."""
    q_offset: float = 0
    """The Q offset."""


@_attrs.frozen
class ChannelInfo(MsgObject):
    """Information about a channel.

    :param name: The name of the channel.
    :param base_freq: The base frequency of the channel.
    :param sample_rate: The sample rate of the channel.
    :param delay: The delay of the channel.
    :param length: The length of the channel.
    :param align_level: The alignment level of the channel.
    :param iir: The biquad filter chain of the channel.
    :param fir: The FIR filter of the channel.
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
    iq_calibration: _typing.Optional[IqCalibration] = None
    iir: _typing.List[Biquad] = _attrs.field(factory=list, converter=list)
    """The biquad filter chain of the channel."""
    fir: _typing.List[float] = _attrs.field(factory=list, converter=list)
    """The FIR filter of the channel."""


class DataType(_enum.Enum):
    """Data types for waveforms."""

    FLOAT32 = 0
    """32-bit floating point."""
    FLOAT64 = 1
    """64-bit floating point."""
