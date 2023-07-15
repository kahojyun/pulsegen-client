import enum as _enum
import math as _math

import attrs as _attrs

import pulsegen_client.contracts as _cts
import pulsegen_client.pulse as _pulse


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


@_attrs.frozen
class Element(_cts.UnionObject):
    """Base class for schedule elements.

    :param margin: The margin of the element.
    :param alignment: The alignment of the element.
    :param visibility: Whether the element has effect on the output.
    :param duration: Requested duration of the element.
    :param max_duration: Maximum duration of the element.
    :param min_duration: Minimum duration of the element.
    """

    @staticmethod
    def _convert_margin(margin: float | tuple[float, float]) -> tuple[float, float]:
        if not isinstance(margin, tuple):
            margin = (margin, margin)
        return margin

    margin: tuple[float, float] = _attrs.field(
        kw_only=True, default=(0, 0), converter=_convert_margin
    )
    """The margin of the element."""
    alignment: Alignment = _attrs.field(kw_only=True, default=Alignment.END)
    """The alignment of the element."""
    visibility: bool = _attrs.field(kw_only=True, default=True)
    """Whether the element has effect on the output."""
    duration: float | None = _attrs.field(kw_only=True, default=None)
    """Requested duration of the element."""
    max_duration: float = _attrs.field(kw_only=True, default=_math.inf)
    """Maximum duration of the element."""
    min_duration: float = _attrs.field(kw_only=True, default=0)
    """Minimum duration of the element."""


@_attrs.frozen
class Play(Element):
    """A pulse play element."""

    TYPE_ID = 0

    flexible: bool = _attrs.field(kw_only=True, default=False)
    """Whether the plateau can be shortened or extended."""
    channel_id: int
    """Target channel ID."""
    shape_id: int
    """The shape ID of the pulse."""
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
class ShiftPhase(Element):
    """A phase shift element."""

    TYPE_ID = 1

    channel_id: int
    """Target channel ID."""
    phase: float
    """Delta phase."""


@_attrs.frozen
class SetPhase(Element):
    """A phase set element."""

    TYPE_ID = 2

    channel_id: int
    """Target channel ID."""
    phase: float
    """Target phase."""


@_attrs.frozen
class ShiftFrequency(Element):
    """A frequency shift element."""

    TYPE_ID = 3

    channel_id: int
    """Target channel ID."""
    frequency: float
    """Delta frequency."""


@_attrs.frozen
class SetFrequency(Element):
    """A frequency set element."""

    TYPE_ID = 4

    channel_id: int
    """Target channel ID."""
    frequency: float
    """Target frequency."""


@_attrs.frozen
class SwapPhase(Element):
    """A phase swap element."""

    TYPE_ID = 5

    channel_id1: int
    """Target channel ID 1."""
    channel_id2: int
    """Target channel ID 2."""


@_attrs.frozen
class Barrier(Element):
    """A barrier element."""

    TYPE_ID = 6

    channel_ids: list[int] = _attrs.field(converter=list[int])
    """Target channel IDs."""


class ArrangeDirection(_enum.Enum):
    """Direction of arrangement."""

    BACKWARDS = 0
    """Arrange from the end of the schedule."""
    FORWARDS = 1
    """Arrange from the start of the schedule."""


@_attrs.frozen
class Stack(Element):
    """Layout child elements in one direction.

    The child elements are arranged in one direction. The direction can be
    forwards or backwards. :class:`Barrier` can be used to synchronize
    multiple channels.

    :param direction: The direction of arrangement.
    :param elements: Child elements.
    """

    TYPE_ID = 7

    direction: ArrangeDirection = _attrs.field(
        kw_only=True, default=ArrangeDirection.BACKWARDS
    )
    """The direction of arrangement."""
    elements: list[Element] = _attrs.field(converter=list[Element])
    """Child elements."""


@_attrs.frozen
class Repeat(Element):
    """A repeated schedule element."""

    TYPE_ID = 8

    spacing: float = _attrs.field(kw_only=True, default=0)
    """The spacing between repeated elements."""
    element: Element
    """The repeated element."""
    count: int
    """The number of repetitions."""


@_attrs.frozen
class Absolute(Element):
    """An absolute schedule element."""

    @_attrs.frozen
    class Entry(_cts.MsgObject):
        """An entry in the absolute schedule."""

        time: float
        """Time relative to the start of the absolute schedule."""
        element: Element
        """The child element."""

    @staticmethod
    def _as_entry(obj: Element | tuple[float, Element] | Entry) -> Entry:
        if isinstance(obj, Element):
            return Absolute.Entry(time=0, element=obj)
        if isinstance(obj, tuple):
            return Absolute.Entry(time=obj[0], element=obj[1])
        return obj

    @staticmethod
    def _convert_entries(
        entries: list[Element | tuple[float, Element] | Entry]
    ) -> list[Entry]:
        return [Absolute._as_entry(obj) for obj in entries]

    TYPE_ID = 9

    elements: list[Entry] = _attrs.field(converter=_convert_entries)
    """Child elements with absolute timing."""


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
    or automatically. Can be parsed from a string following formats like

    ``"10e-9"``
        10 nanoseconds

    ``"*"``
        1 star

    ``"10*"``
        10 stars

    ``"auto"``
        Automatic

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
    def parse(cls, value: str | float) -> "GridLength":
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
class Grid(Element):
    """A grid schedule element.

    :param columns: Definitions of grid columns. The length of the columns can
        be specified as a :class:`GridLength`, a string, or a float. See
        :meth:`GridLength.parse` for details.
    :type columns: list[GridLength | str | float]
    :param elements: Child elements. Each child element has a column index, a
        span, and an element.
    :type elements: list[Element | tuple[int, Element] | tuple[int, int, Element] | Grid.Entry]
    """

    @_attrs.frozen
    class Entry(_cts.MsgObject):
        """An entry in the grid schedule."""

        column: int
        span: int
        element: Element

    @staticmethod
    def _as_entry(
        obj: Element | tuple[int, Element] | tuple[int, int, Element] | Entry
    ) -> Entry:
        if isinstance(obj, Element):
            return Grid.Entry(column=0, span=1, element=obj)
        if isinstance(obj, tuple):
            if len(obj) == 2:
                return Grid.Entry(column=obj[0], span=1, element=obj[1])
            return Grid.Entry(column=obj[0], span=obj[1], element=obj[2])
        return obj

    @staticmethod
    def _convert_entries(
        entries: list[Element | tuple[int, Element] | tuple[int, int, Element] | Entry]
    ) -> list[Entry]:
        return [Grid._as_entry(obj) for obj in entries]

    @staticmethod
    def _convert_columns(columns: list[GridLength | str | float]) -> list[GridLength]:
        return [
            GridLength.parse(column) if not isinstance(column, GridLength) else column
            for column in columns
        ]

    TYPE_ID = 10

    columns: list[GridLength] = _attrs.field(converter=_convert_columns)
    """Definitions of grid columns."""
    elements: list[Entry] = _attrs.field(converter=_convert_entries)
    """Child elements with grid positioning."""


@_attrs.frozen
class Request(_cts.MsgObject):
    """A schedule request."""

    channels: list[_cts.ChannelInfo] = _attrs.field(converter=list[_cts.ChannelInfo])
    """Channels used in the schedule."""
    shapes: list[_pulse.ShapeInfo] = _attrs.field(converter=list[_pulse.ShapeInfo])
    """Shapes used in the schedule."""
    schedule: Element
    """The root element of the schedule."""
