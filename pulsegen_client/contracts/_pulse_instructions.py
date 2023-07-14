"""Contract classes for pulse instructions."""

from attrs import frozen

from ._msgbase import UnionObject


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
