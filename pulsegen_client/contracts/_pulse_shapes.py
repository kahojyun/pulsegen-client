"""Contract classes for pulse shapes."""
from attrs import field, frozen

from ._msgbase import UnionObject


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
