"""Data contracts for pulsegen client and server
"""

from typing import Iterable

import msgpack
import numpy as np


class MsgObject:
    """Base class for all message objects."""

    def __init__(self, data: Iterable) -> None:
        self._data = data

    @property
    def data(self) -> Iterable:
        """The data of the message object to be serialized."""
        return self._data

    def packb(self) -> bytes:
        """Serialize the message object to bytes in msgpack format."""

        def encode(obj: MsgObject):
            return obj.data

        return msgpack.packb(self, default=encode)  # type: ignore


class UnionObject(MsgObject):
    """Base class for all union objects.

    A union object is a message object that can be one of several types.

    :param type_id: The ID of the type of the union object.
    :param data: The data of the union object.
    """

    def __init__(self, type_id: int, data: Iterable) -> None:
        super().__init__([type_id, data])


class ChannelInfo(MsgObject):
    """Information about a channel.

    :param name: The name of the channel.
    :param base_freq: The base frequency of the channel.
    :param sample_rate: The sample rate of the channel.
    :param delay: The delay of the channel.
    :param length: The length of the channel.
    :param align_level: The alignment level of the channel.
    """

    def __init__(
        self,
        name: str,
        base_freq: float,
        sample_rate: float,
        delay: float,
        length: int,
        align_level: int,
    ) -> None:
        super().__init__(
            [
                name,
                base_freq,
                sample_rate,
                delay,
                length,
                align_level,
            ]
        )
        self.name = name


class ShapeInfo(UnionObject):
    """Information about a shape."""

    HANN_SHAPE = 0
    TRIANGLE_SHAPE = 1
    INTERPOLATED_SHAPE = 2


class HannShape(ShapeInfo):
    """A Hann shape."""

    def __init__(self) -> None:
        super().__init__(ShapeInfo.HANN_SHAPE, [])


class TriangleShape(ShapeInfo):
    """A triangle shape."""

    def __init__(self) -> None:
        super().__init__(ShapeInfo.TRIANGLE_SHAPE, [])


class InterpolatedShape(ShapeInfo):
    """An interpolated shape.

    :param x: The x values of the shape.
    :param y: The y values of the shape.
    """

    def __init__(self, x: Iterable[float], y: Iterable[float]) -> None:
        super().__init__(ShapeInfo.INTERPOLATED_SHAPE, [list(x), list(y)])


class Instruction(UnionObject):
    """An instruction."""

    PLAY = 0
    SHIFT_PHASE = 1
    SET_PHASE = 2
    SHIFT_FREQUENCY = 3
    SET_FREQUENCY = 4
    SWAP_PHASE = 5


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

    def __init__(
        self,
        time: float,
        channel_id: int,
        shape_id: int,
        width: float,
        plateau: float,
        frequency: float,
        phase: float,
        amplitude: float,
        drag_coef: float,
    ) -> None:
        super().__init__(
            Instruction.PLAY,
            [
                time,
                channel_id,
                shape_id,
                width,
                plateau,
                frequency,
                phase,
                amplitude,
                drag_coef,
            ],
        )


class ShiftPhase(Instruction):
    """Shift the phase of a channel.

    :param channel_id: The ID of the channel on which to shift the phase.
    :param phase: The phase to shift by.
    """

    def __init__(self, channel_id: int, phase: float) -> None:
        super().__init__(Instruction.SHIFT_PHASE, [channel_id, phase])


class SetPhase(Instruction):
    """Set the phase of a channel.

    :param time: The time at which to set the phase.
    :param channel_id: The ID of the channel on which to set the phase.
    :param phase: The phase to set.
    """

    def __init__(self, time: float, channel_id: int, phase: float) -> None:
        super().__init__(Instruction.SET_PHASE, [time, channel_id, phase])


class ShiftFrequency(Instruction):
    """Shift the frequency of a channel.

    :param channel_id: The ID of the channel on which to shift the frequency.
    :param frequency: The frequency to shift by.
    """

    def __init__(self, time: float, channel_id: int, frequency: float) -> None:
        super().__init__(Instruction.SHIFT_FREQUENCY, [time, channel_id, frequency])


class SetFrequency(Instruction):
    """Set the frequency of a channel.

    :param time: The time at which to set the frequency.
    :param channel_id: The ID of the channel on which to set the frequency.
    :param frequency: The frequency to set.
    """

    def __init__(self, time: float, channel_id: int, frequency: float) -> None:
        super().__init__(Instruction.SET_FREQUENCY, [time, channel_id, frequency])


class SwapPhase(Instruction):
    """Swap the phase of two channels.

    :param time: The time at which to swap the phase.
    :param channel_id1: The ID of the first channel.
    :param channel_id2: The ID of the second channel.
    """

    def __init__(self, time: float, channel_id1: int, channel_id2: int) -> None:
        super().__init__(Instruction.SWAP_PHASE, [time, channel_id1, channel_id2])


class PulseGenRequest(MsgObject):
    """A request to generate a pulse sequence.

    :param channels: The channels to use.
    :param shapes: The shapes to use.
    :param instructions: The instructions to use.
    """

    def __init__(
        self,
        channels: Iterable[ChannelInfo],
        shapes: Iterable[ShapeInfo],
        instructions: Iterable[Instruction],
    ) -> None:
        self.channels = list(channels)
        super().__init__([self.channels, list(shapes), list(instructions)])


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

        :param name: The name of the channel.
        :param base_freq: The base frequency of the channel.
        :param sample_rate: The sample rate of the channel.
        :param delay: The delay of the channel.
        :param length: The length of the channel.
        :param align_level: The alignment level of the channel.
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

    def play(
        self,
        time: float,
        channel_name: str,
        shape_name: str,
        width: float,
        plateau: float,
        frequency: float,
        phase: float,
        amplitude: float,
        drag_coef: float,
    ) -> None:
        """Play a pulse.

        :param time: The time at which to play the pulse.
        :param channel_name: The name of the channel on which to play the pulse.
        :param shape_name: The name of the shape of the pulse. Can be "rect", "hann",
            or "triangle".
        :param width: The width of the pulse.
        :param plateau: The plateau of the pulse.
        :param frequency: Additional frequency of the pulse.
        :param phase: Additional phase of the pulse.
        :param amplitude: The amplitude of the pulse.
        :param drag_coef: The drag coefficient of the pulse.
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
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftPhase(channel_id, phase))

    def set_phase(self, time: float, channel_name: str, phase: float) -> None:
        """Set the phase of a channel.

        :param time: The time at which to set the phase.
        :param channel_name: The name of the channel on which to set the phase.
        :param phase: The phase to set.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetPhase(time, channel_id, phase))

    def shift_frequency(self, time: float, channel_name: str, frequency: float) -> None:
        """Shift the frequency of a channel.

        :param time: The time at which to shift the frequency.
        :param channel_name: The name of the channel on which to shift the frequency.
        :param frequency: The frequency to shift by.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftFrequency(time, channel_id, frequency))

    def set_frequency(self, time: float, channel_name: str, frequency: float) -> None:
        """Set the frequency of a channel.

        :param time: The time at which to set the frequency.
        :param channel_name: The name of the channel on which to set the frequency.
        :param frequency: The frequency to set.
        """
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetFrequency(time, channel_id, frequency))

    def swap_phase(self, time: float, channel_name1: str, channel_name2: str) -> None:
        """Swap the phase of two channels.

        :param time: The time at which to swap the phase.
        :param channel_name1: The name of the first channel.
        :param channel_name2: The name of the second channel.
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
