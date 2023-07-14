"""Data contracts for the pulsegen service."""

from typing import ClassVar, Iterable

import msgpack
import numpy as np
from attrs import astuple, field, frozen

__all__ = [
    "MsgObject",
    "UnionObject",
    "ChannelInfo",
    "Instruction",
    "Play",
    "ShiftPhase",
    "SetPhase",
    "ShiftFrequency",
    "SetFrequency",
    "SwapPhase",
    "ShapeInfo",
    "HannShape",
    "TriangleShape",
    "InterpolatedShape",
    "PulseGenRequest",
    "RequestBuilder",
    "unpack_response",
]


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
        return (self.TYPE_ID, super().data)


@frozen
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


@frozen
class Instruction(UnionObject):
    """An instruction."""


@frozen
class Play(Instruction):
    """Play a pulse on a channel.

    :param time: The time at which to play the pulse.
    :param channel_id: The ID of the channel on which to play the pulse.
    :param shape_id: The ID of the shape to play.
    :param width: The width of the pulse.
    :param plateau: The plateau of the pulse.
    :param frequency: The frequency of the pulse.
    :param phase: The phase of the pulse.
    :param amplitude: The amplitude of the pulse.
    :param drag_coef: The drag coefficient of the pulse.
    """

    TYPE_ID = 0

    time: float
    """The time at which to play the pulse."""
    channel_id: int
    """The ID of the channel on which to play the pulse."""
    shape_id: int
    """The ID of the shape to play."""
    width: float
    """The width of the pulse."""
    plateau: float
    """The plateau of the pulse."""
    frequency: float
    """The frequency of the pulse."""
    phase: float
    """The phase of the pulse."""
    amplitude: float
    """The amplitude of the pulse."""
    drag_coef: float
    """The drag coefficient of the pulse."""


@frozen
class ShiftPhase(Instruction):
    """Shift the phase of a channel.

    :param channel_id: The ID of the channel on which to shift the phase.
    :param phase: The phase to shift by.
    """

    TYPE_ID = 1

    channel_id: int
    """The ID of the channel on which to shift the phase."""
    phase: float
    """The phase to shift by."""


@frozen
class SetPhase(Instruction):
    """Set the phase of a channel.

    :param time: The time at which to set the phase.
    :param channel_id: The ID of the channel on which to set the phase.
    :param phase: The phase to set.
    """

    TYPE_ID = 2

    time: float
    """The time at which to set the phase."""
    channel_id: int
    """The ID of the channel on which to set the phase."""
    phase: float
    """The phase to set."""


@frozen
class ShiftFrequency(Instruction):
    """Shift the frequency of a channel.

    :param time: The time at which to shift the frequency.
    :param channel_id: The ID of the channel on which to shift the frequency.
    :param frequency: The frequency to shift by.
    """

    TYPE_ID = 3

    time: float
    """The time at which to shift the frequency."""
    channel_id: int
    """The ID of the channel on which to shift the frequency."""
    frequency: float
    """The frequency to shift by."""


@frozen
class SetFrequency(Instruction):
    """Set the frequency of a channel.

    :param time: The time at which to set the frequency.
    :param channel_id: The ID of the channel on which to set the frequency.
    :param frequency: The frequency to set.
    """

    TYPE_ID = 4

    time: float
    """The time at which to set the frequency."""
    channel_id: int
    """The ID of the channel on which to set the frequency."""
    frequency: float
    """The frequency to set."""


@frozen
class SwapPhase(Instruction):
    """Swap the phase of two channels.

    :param time: The time at which to swap the phase.
    :param channel_id1: The ID of the first channel.
    :param channel_id2: The ID of the second channel.
    """

    TYPE_ID = 5

    time: float
    """The time at which to swap the phase."""
    channel_id1: int
    """The ID of the first channel."""
    channel_id2: int
    """The ID of the second channel."""


@frozen
class ShapeInfo(UnionObject):
    """Information about a shape."""


@frozen
class HannShape(ShapeInfo):
    """A Hann shape."""

    TYPE_ID = 0


@frozen
class TriangleShape(ShapeInfo):
    """A triangle shape."""

    TYPE_ID = 1


@frozen
class InterpolatedShape(ShapeInfo):
    """An interpolated shape.

    :param x_array: The x values of the shape.
    :param y_array: The y values of the shape.
    """

    TYPE_ID = 2

    x_array: list[float] = field(converter=list[float])
    """The x values of the shape."""
    y_array: list[float] = field(converter=list[float])
    """The y values of the shape."""


@frozen
class PulseGenRequest(MsgObject):
    """A request to generate a pulse sequence.

    :param channels: The channels to use.
    :param shapes: The shapes to use.
    :param instructions: The instructions to use.
    """

    channels: list[ChannelInfo] = field(converter=list[ChannelInfo])
    """The channels to use."""
    shapes: list[ShapeInfo] = field(converter=list[ShapeInfo])
    """The shapes to use."""
    instructions: list[Instruction] = field(converter=list[Instruction])
    """The instructions to use."""


class RequestBuilder:
    """A builder for pulse generation requests.

    .. note::
        All phase values are in number of cycles. For example, a phase of 0.25 means
        pi/2 radians.
    """

    def __init__(self) -> None:
        self._channels: list[ChannelInfo] = []
        self._channel_ids: dict[str, int] = {}
        self._shapes: list[ShapeInfo] = [HannShape(), TriangleShape()]
        self._shape_ids = {
            "rect": -1,
            "hann": 0,
            "triangle": 1,
        }
        self._instructions: list[Instruction] = []

    def add_channel(
        self,
        name: str,
        base_freq: float,
        sample_rate: float,
        delay: float,
        length: int,
        align_level: int,
    ) -> None:
        """Add a channel.

        The alignment level determines the alignment of all pulses on the channel. A
        value of :math:`n` means that all pulses will be aligned to a multiple of
        :math:`2^n` samples. Negative values are allowed, and will result in
        alignment to a fraction of a sample.

        :param name: The name of the channel.
        :param base_freq: The base frequency of the channel.
        :param sample_rate: The sample rate of the channel.
        :param delay: The delay of the channel.
        :param length: The length of the channel.
        :param align_level: The alignment level of the channel.
        :raises ValueError: If the channel name already exists.
        """
        if name in self._channel_ids:
            raise ValueError(f"Channel name {name} already exists")
        channel_id = len(self._channels)
        self._channels.append(
            ChannelInfo(
                name,
                base_freq,
                sample_rate,
                delay,
                length,
                align_level,
            )
        )
        self._channel_ids[name] = channel_id

    def add_interpolated_shape(
        self,
        name: str,
        x_array: Iterable[float],
        y_array: Iterable[float],
    ):
        """Add an interpolated shape.

        :param name: The name of the shape.
        :param x_array: The x values of the shape. Should be between -0.5 and 0.5.
        :param y_array: The y values of the shape.
        :raises ValueError: If the shape name already exists.
        """
        if name in self._shape_ids:
            raise ValueError(f"Shape name {name} already exists")
        shape_id = len(self._shapes)
        self._shapes.append(InterpolatedShape(x_array, y_array))
        self._shape_ids[name] = shape_id

    def play(
        self,
        time: float,
        channel_name: str,
        amplitude: float,
        shape_name: str,
        width: float,
        plateau: float = 0,
        drag_coef: float = 0,
        frequency: float = 0,
        phase: float = 0,
    ) -> None:
        """Play a pulse.

        :param time: The time at which to play the pulse.
        :param channel_name: The name of the channel on which to play the pulse.
        :param amplitude: The amplitude of the pulse.
        :param shape_name: The name of the shape of the pulse. Can be "rect", "hann",
            or "triangle".
        :param width: The width of the pulse.
        :param plateau: The plateau of the pulse.
        :param drag_coef: The drag coefficient of the pulse.
        :param frequency: Additional frequency of the pulse.
        :param phase: Additional phase of the pulse.
        :raises KeyError: If the channel or shape name does not exist.
        """
        channel_id = self._channel_ids[channel_name]
        shape_id = self._shape_ids[shape_name]
        self._instructions.append(
            Play(
                time,
                channel_id,
                shape_id,
                width,
                plateau,
                frequency,
                phase,
                amplitude,
                drag_coef,
            )
        )

    def shift_phase(self, channel_name: str, phase: float) -> None:
        """Shift the phase of a channel.

        :param channel_name: The name of the channel on which to shift the phase.
        :param phase: The phase to shift by.
        :raises KeyError: If the channel name does not exist.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftPhase(channel_id, phase))

    def set_phase(self, time: float, channel_name: str, phase: float) -> None:
        """Set the phase of a channel.

        :param time: The time at which to set the phase.
        :param channel_name: The name of the channel on which to set the phase.
        :param phase: The phase to set.
        :raises KeyError: If the channel name does not exist.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetPhase(time, channel_id, phase))

    def shift_frequency(self, time: float, channel_name: str, frequency: float) -> None:
        """Shift the frequency of a channel.

        :param time: The time at which to shift the frequency.
        :param channel_name: The name of the channel on which to shift the frequency.
        :param frequency: The frequency to shift by.
        :raises KeyError: If the channel name does not exist.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftFrequency(time, channel_id, frequency))

    def set_frequency(self, time: float, channel_name: str, frequency: float) -> None:
        """Set the frequency of a channel.

        :param time: The time at which to set the frequency.
        :param channel_name: The name of the channel on which to set the frequency.
        :param frequency: The frequency to set.
        :raises KeyError: If the channel name does not exist.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetFrequency(time, channel_id, frequency))

    def swap_phase(self, time: float, channel_name1: str, channel_name2: str) -> None:
        """Swap the phase of two channels.

        :param time: The time at which to swap the phase.
        :param channel_name1: The name of the first channel.
        :param channel_name2: The name of the second channel.
        :raises KeyError: If the channel name does not exist.
        """
        channel_id1 = self._channel_ids[channel_name1]
        channel_id2 = self._channel_ids[channel_name2]
        self._instructions.append(SwapPhase(time, channel_id1, channel_id2))

    def build(self) -> PulseGenRequest:
        """Build the request.

        :return: The request.
        """
        return PulseGenRequest(self._channels, self._shapes, self._instructions)


def unpack_response(
    channels: Iterable[ChannelInfo], content: bytes
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Unpack the binary response from the server.

    :param channels: Channel information from the corresponding request.
    :param content: The binary response.
    :return: The unpacked response. The keys are the channel names and the
        values are tuples of (I, Q) arrays.
    """
    response_obj = msgpack.unpackb(content)[0]
    result = {}
    for i, channel in enumerate(channels):
        result[channel.name] = (
            np.frombuffer(response_obj[i][0], dtype=np.float64),
            np.frombuffer(response_obj[i][1], dtype=np.float64),
        )
    return result
