import typing as _typing

import attrs as _attrs

import pulsegen_client.contracts as _cts


@_attrs.frozen
class Instruction(_cts.UnionObject):
    """An instruction."""


@_attrs.frozen
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


@_attrs.frozen
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


@_attrs.frozen
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


@_attrs.frozen
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


@_attrs.frozen
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


@_attrs.frozen
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


@_attrs.frozen
class ShapeInfo(_cts.UnionObject):
    """Information about a shape."""


@_attrs.frozen
class HannShape(ShapeInfo):
    """A Hann shape."""

    TYPE_ID = 0


@_attrs.frozen
class TriangleShape(ShapeInfo):
    """A triangle shape."""

    TYPE_ID = 1


@_attrs.frozen
class InterpolatedShape(ShapeInfo):
    """An interpolated shape.

    :param x_array: The x values of the shape.
    :param y_array: The y values of the shape.
    """

    TYPE_ID = 2

    x_array: list[float] = _attrs.field(converter=list[float])
    """The x values of the shape."""
    y_array: list[float] = _attrs.field(converter=list[float])
    """The y values of the shape."""


@_attrs.frozen
class Request(_cts.MsgObject):
    """A request to generate a pulse sequence.

    :param channels: The channels to use.
    :param shapes: The shapes to use.
    :param instructions: The instructions to use.
    """

    channels: list[_cts.ChannelInfo] = _attrs.field(converter=list[_cts.ChannelInfo])
    """The channels to use."""
    shapes: list[ShapeInfo] = _attrs.field(converter=list[ShapeInfo])
    """The shapes to use."""
    instructions: list[Instruction] = _attrs.field(converter=list[Instruction])
    """The instructions to use."""


class RequestBuilder:
    """A builder for pulse generation requests.

    .. note::
        All phase values are in number of cycles. For example, a phase of 0.25 means
        pi/2 radians.
    """

    def __init__(self) -> None:
        self._channels: list[_cts.ChannelInfo] = []
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
            _cts.ChannelInfo(
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
        x_array: _typing.Iterable[float],
        y_array: _typing.Iterable[float],
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

    def build(self) -> Request:
        """Build the request.

        :return: The request.
        """
        return Request(self._channels, self._shapes, self._instructions)
