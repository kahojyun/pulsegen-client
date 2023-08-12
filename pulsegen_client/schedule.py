"""Classes for pulse scheduling."""

import enum as _enum
import math as _math
import typing as _typing

import attrs as _attrs

import pulsegen_client.contracts as _cts
import pulsegen_client.shape as _shape


class Alignment(_enum.Enum):
    """Alignment of a schedule element."""

    END = 0
    """Align to the end of parent element."""
    START = 1
    """Align to the start of parent element."""
    CENTER = 2
    """Align to the center of parent element."""
    STRETCH = 3
    """Stretch to fill parent element."""


def _convert_margin(
    margin: _typing.Union[float, _typing.Tuple[float, float]]
) -> _typing.Tuple[float, float]:
    if not isinstance(margin, tuple):
        margin = (margin, margin)
    return margin


def _convert_alignment(
    alignment: _typing.Union[
        _typing.Literal["end", "start", "center", "stretch"], Alignment
    ]
) -> Alignment:
    if isinstance(alignment, str):
        return Alignment[alignment.upper()]
    return alignment


@_attrs.frozen
class Element(_cts.UnionObject):
    """Base class for schedule elements.

    A schedule element is a node in the tree structure of a schedule similar to
    HTML elements. The design is inspired by `XAML in WPF / WinUI <https://learn.
    microsoft.com/en-us/windows/apps/design/layout/layouts-with-xaml>`_

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    margin: _typing.Tuple[float, float] = _attrs.field(
        kw_only=True, default=(0, 0), converter=_convert_margin
    )
    """The margin of the element."""
    alignment: Alignment = _attrs.field(
        kw_only=True, default=Alignment.END, converter=_convert_alignment
    )
    """The alignment of the element."""
    visibility: bool = _attrs.field(kw_only=True, default=True)
    """Whether the element has effect on the output."""
    duration: _typing.Optional[float] = _attrs.field(kw_only=True, default=None)
    """Requested duration of the element."""
    max_duration: float = _attrs.field(kw_only=True, default=_math.inf)
    """Maximum duration of the element."""
    min_duration: float = _attrs.field(kw_only=True, default=0)
    """Minimum duration of the element."""


@_attrs.frozen
class Play(Element):
    """A pulse play element.

    If :attr:`flexible` is set to ``True`` and :attr:`alignment` is set to
    :attr:`Alignment.STRETCH`, the duration of the pulse is determined by the
    parent element such as :class:`Grid`.

    :param channel_id: Target channel ID.
    :param amplitude: The amplitude of the pulse.
    :param shape_id: The shape ID of the pulse.
    :param width: The width of the pulse.
    :param plateau: The plateau of the pulse.
    :param drag_coef: The drag coefficient of the pulse.
    :param frequency: The frequency of the pulse.
    :param phase: The phase of the pulse in **cycles**.
    :param flexible: Whether the pulse can be shortened or extended.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 0

    channel_id: int
    """Target channel ID."""
    amplitude: float
    """The amplitude of the pulse."""
    shape_id: int
    """The shape ID of the pulse."""
    width: float
    """The width of the pulse."""
    plateau: float = _attrs.field(kw_only=True, default=0)
    """The plateau of the pulse."""
    drag_coef: float = _attrs.field(kw_only=True, default=0)
    """The drag coefficient of the pulse."""
    frequency: float = _attrs.field(kw_only=True, default=0)
    """The frequency of the pulse."""
    phase: float = _attrs.field(kw_only=True, default=0)
    """The phase of the pulse in **cycles**."""
    flexible: bool = _attrs.field(kw_only=True, default=False)
    """Whether the plateau can be shortened or extended."""


@_attrs.frozen
class ShiftPhase(Element):
    """A phase shift element.

    :param channel_id: Target channel ID.
    :param phase: Delta phase in **cycles**.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 1

    channel_id: int
    """Target channel ID."""
    phase: float
    """Delta phase in **cycles**."""


@_attrs.frozen
class SetPhase(Element):
    """A phase set element.

    Currently the effect of set phase instruction is calculated based on the
    cumulative frequency shift. This may change in the future.

    :param channel_id: Target channel ID.
    :param phase: Target phase in **cycles**.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 2

    channel_id: int
    """Target channel ID."""
    phase: float
    """Target phase in **cycles**."""


@_attrs.frozen
class ShiftFrequency(Element):
    """A frequency shift element.

    :param channel_id: Target channel ID.
    :param frequency: Delta frequency.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 3

    channel_id: int
    """Target channel ID."""
    frequency: float
    """Delta frequency."""


@_attrs.frozen
class SetFrequency(Element):
    """A frequency set element.

    :param channel_id: Target channel ID.
    :param frequency: Target frequency.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 4

    channel_id: int
    """Target channel ID."""
    frequency: float
    """Target frequency."""


@_attrs.frozen
class SwapPhase(Element):
    """A phase swap element.

    Let :math:`\\phi_1` and :math:`\\phi_2` be the phases of the two target
    channels, respectively. The effect of the swap phase instruction is to
    change the phases to :math:`\\phi_2` and :math:`\\phi_1`, respectively.
    Currently the phase :math:`\\phi` is defined as

    .. math::
        \\phi = (f + \\Delta f) t + \\phi_0

    where :math:`f` is the frequency defined in
    :class:`pulsegen_client.contracts.ChannelInfo`, :math:`\\Delta f` is the
    frequency shift due to :class:`ShiftFrequency`, and :math:`\\phi_0` is the
    phase offset due to :class:`ShiftPhase` and other phase instructions.

    :param channel_id1: Target channel ID 1.
    :param channel_id2: Target channel ID 2.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 5

    channel_id1: int
    """Target channel ID 1."""
    channel_id2: int
    """Target channel ID 2."""


@_attrs.frozen
class Barrier(Element):
    """A barrier element.

    A barrier element is a zero-duration no-op element. Useful for aligning
    elements on different channels in :class:`Stack`.

    If :attr:`channel_ids` is empty, the barrier is applied to all channels in
    its parent element.

    :param channel_ids: Target channel IDs.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 6

    channel_ids: _typing.List[int] = _attrs.field(converter=list, factory=list)
    """Target channel IDs."""


@_attrs.frozen
class Repeat(Element):
    """A repeated schedule element.

    :param element: The repeated element.
    :param count: The number of repetitions.
    :param spacing: The spacing between repeated elements.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 7

    child: Element
    """The repeated element."""
    count: int
    """The number of repetitions."""
    spacing: float = _attrs.field(kw_only=True, default=0)
    """The spacing between repeated elements."""


class ArrangeDirection(_enum.Enum):
    """Direction of arrangement."""

    BACKWARDS = 0
    """Arrange from the end of the schedule."""
    FORWARDS = 1
    """Arrange from the start of the schedule."""


def _convert_direction(
    direction: _typing.Union[_typing.Literal["backwards", "forwards"], ArrangeDirection]
) -> ArrangeDirection:
    if isinstance(direction, str):
        return ArrangeDirection[direction.upper()]
    return direction


@_attrs.frozen
class Stack(Element):
    """Layout child elements in one direction.

    The child elements are arranged in one direction. The direction can be
    forwards or backwards. :class:`Barrier` can be used to synchronize
    multiple channels.

    :param elements: Child elements.
    :param direction: The direction of arrangement.

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :keyword max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 8

    children: _typing.List[Element] = _attrs.field(converter=list, factory=list)
    """Child elements."""
    direction: ArrangeDirection = _attrs.field(
        kw_only=True, default=ArrangeDirection.BACKWARDS, converter=_convert_direction
    )
    """The direction of arrangement."""

    def with_children(self, *children: Element) -> "Stack":
        """Create a new stack with different children.

        :param children: The new children.
        :return: The new stack.
        """
        return _attrs.evolve(self, children=children)


@_attrs.frozen
class AbsoluteEntry(_cts.MsgObject):
    """An entry in the absolute schedule."""

    time: float
    """Time relative to the start of the absolute schedule."""
    element: Element
    """The child element."""

    @classmethod
    def from_tuple(
        cls, obj: _typing.Union[Element, _typing.Tuple[float, Element], "AbsoluteEntry"]
    ) -> "AbsoluteEntry":
        """Create an absolute entry from a tuple.

        :param obj: The object to be converted.
        :return: The converted object.
        """
        if isinstance(obj, Element):
            return cls(time=0, element=obj)
        if isinstance(obj, tuple):
            return cls(time=obj[0], element=obj[1])
        return obj


def _convert_abs_entries(
    entries: _typing.List[
        _typing.Union[Element, _typing.Tuple[float, Element], AbsoluteEntry]
    ]
) -> _typing.List[AbsoluteEntry]:
    return [AbsoluteEntry.from_tuple(obj) for obj in entries]


@_attrs.frozen
class Absolute(Element):
    """An absolute schedule element.

    The child elements are arranged in absolute time. The time of each child
    element is relative to the start of the absolute schedule. The duration of
    the absolute schedule is the maximum end time of the child elements.

    :param elements: Child elements with absolute timing. Each item in the list
        can be either an :class:`Element` or ``(time, element)``. Default
        ``time`` is 0.
    :type elements: list[Element | tuple[float, Element] | Entry]

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 9

    children: _typing.List[AbsoluteEntry] = _attrs.field(
        converter=_convert_abs_entries, factory=list
    )
    """Child elements with absolute timing."""

    def with_children(
        self, *children: _typing.Union[Element, _typing.Tuple[float, Element]]
    ) -> "Absolute":
        """Create a new absolute schedule with different children.

        :param children: The new children.
        :return: The new absolute schedule.
        """
        return _attrs.evolve(self, children=children)


class GridLengthUnit(_enum.Enum):
    """Unit of grid length."""

    SECOND = 0
    """Seconds."""
    AUTO = 1
    """Automatic."""
    STAR = 2
    """Fraction of remaining space."""


@_attrs.frozen
class GridLength(_cts.MsgObject):
    """Length of a grid column.

    :class:`GridLength` is used to specify the length of a grid column. The
    length can be specified in seconds, as a fraction of the remaining space,
    or automatically.

    :param value: The value of the length.
    :param unit: The unit of the length.
    """

    value: float
    """The value of the length."""
    unit: GridLengthUnit
    """The unit of the length."""

    @classmethod
    def auto(cls) -> "GridLength":
        """Create an automatic grid length."""
        return cls(value=_math.nan, unit=GridLengthUnit.AUTO)

    @classmethod
    def star(cls, value: float) -> "GridLength":
        """Create a star grid length."""
        return cls(value=value, unit=GridLengthUnit.STAR)

    @classmethod
    def abs(cls, value: float) -> "GridLength":
        """Create an absolute grid length."""
        return cls(value=value, unit=GridLengthUnit.SECOND)

    @classmethod
    def parse(cls, value: _typing.Union[str, float]) -> "GridLength":
        """Create a grid length from a string or a float.

        The value can be one of the following formats:

        ``"10e-9"`` or 10e-9
            10 nanoseconds

        ``"*"``
            1 star

        ``"10*"``
            10 stars

        ``"auto"``
            Automatic

        :param value: The value to parse.
        """
        if isinstance(value, (float, int)):
            return cls.abs(value)
        if value.lower() == "auto":
            return cls.auto()
        if value.endswith("*"):
            return cls.star(float(value[:-1]))
        return cls.abs(float(value))


@_attrs.frozen
class GridEntry(_cts.MsgObject):
    """An entry in the grid schedule."""

    column: int
    """The column index."""
    span: int
    """The column span."""
    element: Element
    """The child element."""

    @classmethod
    def from_tuple(
        cls,
        obj: _typing.Union[
            Element,
            _typing.Tuple[int, Element],
            _typing.Tuple[int, int, Element],
            "GridEntry",
        ],
    ) -> "GridEntry":
        """Create a grid entry from a tuple.

        :param obj: The tuple to convert.
        """
        if isinstance(obj, Element):
            return cls(column=0, span=1, element=obj)
        if isinstance(obj, tuple):
            if len(obj) == 2:
                return cls(column=obj[0], span=1, element=obj[1])
            return cls(column=obj[0], span=obj[1], element=obj[2])
        return obj


def _convert_grid_entries(
    entries: _typing.List[
        _typing.Union[
            Element,
            _typing.Tuple[int, Element],
            _typing.Tuple[int, int, Element],
            GridEntry,
        ]
    ]
) -> _typing.List[GridEntry]:
    return [GridEntry.from_tuple(obj) for obj in entries]


def _convert_columns(
    columns: _typing.List[_typing.Union[GridLength, str, float]]
) -> _typing.List[GridLength]:
    return [
        GridLength.parse(column) if not isinstance(column, GridLength) else column
        for column in columns
    ]


@_attrs.frozen
class Grid(Element):
    """A grid schedule element.

    :param columns: Definitions of grid columns. The length of the columns can
        be specified as a :class:`GridLength`, a string, or a float. See
        :meth:`GridLength.parse` for details.
    :type columns: list[GridLength | str | float]
    :param elements: Child elements with column index and span. Each item in the
        list can be either :class:`Element`, ``(column, element)`` or
        ``(column, span, element)``. The default column is 0 and the default
        span is 1.
    :type elements: list[Element | tuple[int, Element] | tuple[int, int, Element] | Grid.Entry]

    :param margin: The margin of the element. If a single value is given, it is
        used for both sides.
    :type margin: float | tuple[float, float]
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    TYPE_ID = 10

    children: _typing.List[GridEntry] = _attrs.field(
        converter=_convert_grid_entries, factory=list
    )
    """Child elements with grid positioning."""
    columns: _typing.List[GridLength] = _attrs.field(
        converter=_convert_columns, factory=list
    )
    """Definitions of grid columns."""

    def with_children(
        self,
        *children: _typing.Union[
            Element,
            _typing.Tuple[int, Element],
            _typing.Tuple[int, int, Element],
        ],
    ) -> "Grid":
        """Create a new grid schedule with different children.

        :param children: The new children.
        :return: The new grid schedule.
        """
        return _attrs.evolve(self, children=children)


@_attrs.frozen
class Request(_cts.MsgObject):
    """A schedule request.

    :param channels: Information about the channels used in the schedule.
    :param shapes: Information about the shapes used in the schedule.
    :param schedule: The root element of the schedule.
    :param options: Options for the PulseGen service.
    """

    channels: _typing.List[_cts.ChannelInfo] = _attrs.field(converter=list)
    """Information about the channels used in the schedule."""
    shapes: _typing.List[_shape.ShapeInfo] = _attrs.field(converter=list)
    """Information about the shapes used in the schedule."""
    schedule: Element
    """The root element of the schedule."""
    options: _cts.Options = _attrs.field(factory=_cts.Options)
    """Options for the PulseGen service."""
