"""Contract classes for channels."""

from attrs import frozen

from ._msgbase import MsgObject


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
