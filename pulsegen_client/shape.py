"""Basic pulse generation instructions."""

import typing as _typing

import attrs as _attrs

import pulsegen_client.contracts as _cts


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

    x_array: _typing.List[float] = _attrs.field(converter=list)
    """The x values of the shape."""
    y_array: _typing.List[float] = _attrs.field(converter=list)
    """The y values of the shape."""
