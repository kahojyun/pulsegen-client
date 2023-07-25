import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterator, List, Optional, Set, Tuple

import pulsegen_client.schedule as schedule
from pulsegen_client.runner._phase_tracker import PhaseTracker
from pulsegen_client.runner._shape_impl import Envelope, PulseShape


class LayoutManager(ABC):
    def __init__(self, element: schedule.Element) -> None:
        self.element = element
        self.desired_duration: Optional[float] = None
        self.unclipped_duration: Optional[float] = None
        self.actual_time: Optional[float] = None
        self.actual_duration: Optional[float] = None
        self.channels: Set[int] = set()

    @abstractmethod
    def measure_override(self, available_duration: float) -> float:
        ...

    @abstractmethod
    def arrange_override(self, time: float, final_duration: float) -> float:
        ...

    @abstractmethod
    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        ...

    def measure(self, available_duration: float) -> None:
        margin = self.element.margin[0] + self.element.margin[1]
        min_duration, max_duration = self._minmax()
        content_duration = max(available_duration - margin, 0)
        content_duration = max(min(content_duration, max_duration), min_duration)
        measured_duration = self.measure_override(content_duration)
        desired_duration = (
            max(min(measured_duration, max_duration), min_duration) + margin
        )
        self.desired_duration = max(min(desired_duration, available_duration), 0)
        self.unclipped_duration = max(measured_duration + margin, 0)

    def arrange(self, time: float, final_duration: float) -> None:
        assert self.desired_duration is not None
        assert self.unclipped_duration is not None
        margin = self.element.margin[0] + self.element.margin[1]
        min_duration, max_duration = self._minmax()
        content_time = time + self.element.margin[0]
        content_duration = max(final_duration - margin, 0)
        content_duration = max(min(content_duration, max_duration), min_duration)
        actual_duration = self.arrange_override(content_time, content_duration)
        self.actual_duration = actual_duration
        self.actual_time = content_time

    def render(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        if not self.element.visibility:
            return
        assert self.actual_time is not None
        assert self.actual_duration is not None
        content_time = time + self.actual_time
        self.render_override(content_time, tracker, shapes)

    def _minmax(self) -> Tuple[float, float]:
        max_duration = self.element.duration or math.inf
        max_duration = max(
            min(max_duration, self.element.max_duration), self.element.min_duration
        )
        min_duration = self.element.duration or 0
        min_duration = max(
            min(min_duration, self.element.max_duration), self.element.min_duration
        )
        return min_duration, max_duration


def create_layout_manager(element: schedule.Element) -> LayoutManager:
    if isinstance(element, schedule.Repeat):
        return RepeatLayoutManager(element)
    if isinstance(element, schedule.Stack):
        return StackLayoutManager(element)
    if isinstance(element, schedule.Absolute):
        return AbsoluteLayoutManager(element)
    if isinstance(element, schedule.Grid):
        return GridLayoutManager(element)
    if isinstance(element, schedule.Play):
        return SimpleLayoutManager(
            element, element.width + element.plateau, {element.channel_id}
        )
    if isinstance(
        element,
        (
            schedule.ShiftFrequency,
            schedule.SetFrequency,
            schedule.ShiftPhase,
            schedule.SetPhase,
        ),
    ):
        return SimpleLayoutManager(element, 0, {element.channel_id})
    if isinstance(element, schedule.SwapPhase):
        return SimpleLayoutManager(
            element, 0, {element.channel_id1, element.channel_id2}
        )
    if isinstance(element, schedule.Barrier):
        return SimpleLayoutManager(element, 0, set(element.channel_ids))
    raise ValueError(f"Unknown element type: {type(element)}")


class SimpleLayoutManager(LayoutManager):
    def __init__(
        self, element: schedule.Element, duration: float, channels: Set[int]
    ) -> None:
        super().__init__(element)
        self._duration = duration
        self.channels = channels

    def measure_override(self, available_duration: float) -> float:
        if isinstance(self.element, schedule.Play) and self.element.flexible:
            return self.element.width
        return self._duration

    def arrange_override(self, time: float, final_duration: float) -> float:
        if isinstance(self.element, schedule.Play) and self.element.flexible:
            return final_duration
        return self._duration

    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        element = self.element
        if isinstance(element, schedule.Play):
            shape = None if element.shape_id == -1 else shapes[element.shape_id]
            assert self.actual_duration is not None
            plateau = (
                self.actual_duration - element.width
                if element.flexible
                else element.plateau
            )
            envelope = Envelope(shape, element.width, plateau)
            tracker.play(
                element.channel_id,
                envelope,
                element.frequency,
                element.phase,
                element.amplitude,
                element.drag_coef,
                time,
            )
        elif isinstance(element, schedule.ShiftFrequency):
            tracker.shift_freq(element.channel_id, element.frequency, time)
        elif isinstance(element, schedule.SetFrequency):
            tracker.set_freq(element.channel_id, element.frequency, time)
        elif isinstance(element, schedule.ShiftPhase):
            tracker.shift_phase(element.channel_id, element.phase)
        elif isinstance(element, schedule.SetPhase):
            tracker.set_phase(element.channel_id, element.phase, time)
        elif isinstance(element, schedule.SwapPhase):
            tracker.swap_phase(element.channel_id1, element.channel_id2, time)
        elif isinstance(element, schedule.Barrier):
            pass
        else:
            raise ValueError(f"Unknown instruction type: {type(element)}")


class RepeatLayoutManager(LayoutManager):
    def __init__(
        self,
        element: schedule.Repeat,
    ) -> None:
        super().__init__(element)
        self.element: schedule.Repeat
        self.child_layout = create_layout_manager(element.child)
        self.channels = self.child_layout.channels

    def measure_override(self, available_duration: float) -> float:
        n = self.element.count
        if n == 0:
            return 0
        child_available = (available_duration - self.element.spacing * (n - 1)) / n
        self.child_layout.measure(child_available)
        assert self.child_layout.desired_duration is not None
        return self.child_layout.desired_duration * n + self.element.spacing * (n - 1)

    def arrange_override(self, time: float, final_duration: float) -> float:
        n = self.element.count
        if n == 0:
            return 0
        child_available = (final_duration - self.element.spacing * (n - 1)) / n
        self.child_layout.arrange(0, child_available)
        return final_duration

    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        n = self.element.count
        if n == 0:
            return
        child_time = time
        assert self.child_layout.actual_duration is not None
        for _ in range(n):
            self.child_layout.render(child_time, tracker, shapes)
            child_time += self.child_layout.actual_duration + self.element.spacing


class StackLayoutManager(LayoutManager):
    def __init__(
        self,
        element: schedule.Stack,
    ) -> None:
        super().__init__(element)
        self.element: schedule.Stack
        self.child_layouts = [create_layout_manager(e) for e in element.children]
        self.channels = set().union(*(c.channels for c in self.child_layouts))

    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        for child in self.child_layouts:
            child.render(time, tracker, shapes)

    def measure_override(self, available_duration: float) -> float:
        helper = self.LayoutHelper(self)
        for child in helper:
            child_channels = child.channels
            used = helper.used_time(child_channels)
            left = available_duration - used
            child.measure(left)
            assert child.desired_duration is not None
            new_used = child.desired_duration + used
            helper.update_used(child_channels, new_used)
        return helper.total_time()

    def arrange_override(self, time: float, final_duration: float) -> float:
        helper = self.LayoutHelper(self)
        for child in helper:
            child_channels = child.channels
            used = helper.used_time(child_channels)
            assert child.desired_duration is not None
            child_duration = child.desired_duration
            child_time = helper.arrange_time(used, child_duration, final_duration)
            child.arrange(child_time, child_duration)
            new_used = child_duration + used
            helper.update_used(child_channels, new_used)
        return final_duration

    class LayoutHelper:
        def __init__(self, layout: "StackLayoutManager") -> None:
            self._channels = layout.channels
            self._durations = 0.0 if not self._channels else defaultdict(float)
            self._childs = layout.child_layouts
            self._direction = layout.element.direction

        def __iter__(self) -> Iterator[LayoutManager]:
            if self._direction == schedule.ArrangeDirection.BACKWARDS:
                elements = reversed(self._childs)
            else:
                elements = self._childs
            return iter(elements)

        def used_time(self, channels: Set[int]) -> float:
            if isinstance(self._durations, float):
                return self._durations
            if not channels:
                return max(self._durations.values())
            return max(self._durations[channel] for channel in channels)

        def total_time(self) -> float:
            if isinstance(self._durations, float):
                return self._durations
            return max(self._durations.values())

        def arrange_time(
            self, used: float, child_duration: float, total: float
        ) -> float:
            if self._direction == schedule.ArrangeDirection.BACKWARDS:
                return total - used - child_duration
            return used

        def update_used(self, channels: Set[int], duration: float) -> None:
            if isinstance(self._durations, float):
                self._durations = duration
            else:
                target_channels = channels or self._channels
                for channel in target_channels:
                    self._durations[channel] = duration


class AbsoluteLayoutManager(LayoutManager):
    def __init__(self, element: schedule.Absolute) -> None:
        super().__init__(element)
        self.element: schedule.Absolute
        self.child_layouts = [
            create_layout_manager(e.element) for e in element.children
        ]
        self.channels = set().union(*(c.channels for c in self.child_layouts))

    def measure_override(self, available_duration: float) -> float:
        max_time = 0.0
        child_times = (e.time for e in self.element.children)
        for child_time, child in zip(child_times, self.child_layouts):
            child.measure(available_duration)
            assert child.desired_duration is not None
            max_time = max(max_time, child.desired_duration + child_time)
        return max_time

    def arrange_override(self, time: float, final_duration: float) -> float:
        child_times = (e.time for e in self.element.children)
        for child_time, child in zip(child_times, self.child_layouts):
            assert child.desired_duration is not None
            child.arrange(child_time, child.desired_duration)
        return final_duration

    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        for child in self.child_layouts:
            child.render(time, tracker, shapes)


class GridLayoutManager(LayoutManager):
    def __init__(self, element: schedule.Grid) -> None:
        super().__init__(element)
        self.element: schedule.Grid
        self.child_layouts = [
            create_layout_manager(e.element) for e in element.children
        ]
        self.channels = set().union(*(c.channels for c in self.child_layouts))
        self._min_column_width: Optional[List[float]] = None
        self._columns = element.columns

    def render_override(
        self, time: float, tracker: PhaseTracker, shapes: List[PulseShape]
    ) -> None:
        for child in self.child_layouts:
            child.render(time, tracker, shapes)

    def measure_override(self, available_duration: float) -> float:
        if len(self._columns) == 0:
            self._columns.append(schedule.GridLength.star(1))
        for child in self.child_layouts:
            child.measure(available_duration)
        colsizes = [
            c.value if c.unit == schedule.GridLengthUnit.SECOND else 0.0
            for c in self._columns
        ]
        for child, (column, span) in zip(
            self.child_layouts, ((e.column, e.span) for e in self.element.children)
        ):
            actual_column = min(column, len(colsizes) - 1)
            actual_span = min(span, len(colsizes) - actual_column)
            if actual_span > 1:
                continue
            if self._columns[actual_column].unit == schedule.GridLengthUnit.SECOND:
                continue
            assert child.desired_duration is not None
            colsizes[actual_column] = max(
                colsizes[actual_column], child.desired_duration
            )
        for child, (column, span) in zip(
            self.child_layouts, ((e.column, e.span) for e in self.element.children)
        ):
            actual_column = min(column, len(colsizes) - 1)
            actual_span = min(span, len(colsizes) - actual_column)
            if actual_span == 1:
                continue
            assert child.desired_duration is not None
            colsize = sum(colsizes[actual_column : actual_column + actual_span])
            if colsize > child.desired_duration:
                continue
            n_star = sum(
                1
                for i in range(actual_column, actual_column + actual_span)
                if self._columns[i].unit == schedule.GridLengthUnit.STAR
            )
            if n_star == 0:
                n_auto = sum(
                    1
                    for i in range(actual_column, actual_column + actual_span)
                    if self._columns[i].unit == schedule.GridLengthUnit.AUTO
                )
                if n_auto == 0:
                    continue
                inc = (child.desired_duration - colsize) / n_auto
                for i in range(actual_column, actual_column + actual_span):
                    if self._columns[i].unit == schedule.GridLengthUnit.AUTO:
                        colsizes[i] += inc
            else:
                self._expand_column_width(
                    colsizes,
                    actual_column,
                    actual_span,
                    child.desired_duration - colsize,
                )
        self._min_column_width = colsizes
        return sum(colsizes)

    def arrange_override(self, time: float, final_duration: float) -> float:
        assert self._min_column_width is not None
        colsizes = self._min_column_width.copy()
        min_duration = sum(colsizes)
        self._expand_column_width(
            colsizes, 0, len(colsizes), final_duration - min_duration
        )
        colstarts = [0.0]
        for i in range(len(colsizes) - 1):
            colstarts.append(colstarts[-1] + colsizes[i])
        for child, (column, span, align) in zip(
            self.child_layouts,
            ((e.column, e.span, e.element.alignment) for e in self.element.children),
        ):
            actual_column = min(column, len(colsizes) - 1)
            actual_span = min(span, len(colsizes) - actual_column)
            assert child.desired_duration is not None
            span_duration = sum(colsizes[actual_column : actual_column + actual_span])
            child_duration = (
                child.desired_duration
                if align != schedule.Alignment.STRETCH
                else span_duration
            )
            actual_duration = min(child_duration, span_duration)
            if align == schedule.Alignment.START:
                child_time = colstarts[actual_column]
            elif align == schedule.Alignment.END:
                child_time = colstarts[actual_column] + span_duration - actual_duration
            elif align == schedule.Alignment.CENTER:
                child_time = (
                    colstarts[actual_column] + (span_duration - actual_duration) / 2
                )
            else:
                child_time = colstarts[actual_column]
            child.arrange(child_time, actual_duration)
        return final_duration

    def _expand_column_width(
        self, column_width: List[float], column: int, span: int, remaining: float
    ) -> None:
        columns = self._columns
        cols = []
        for i in range(column, column + span):
            if i >= len(column_width):
                break
            if columns[i].unit != schedule.GridLengthUnit.STAR:
                continue
            cols.append((i, column_width[i] / columns[i].value))
        cols = sorted(cols, key=lambda x: x[1])
        stars = 0.0
        for i in range(len(cols)):
            next_ratio = cols[i + 1][1] if i + 1 < len(cols) else math.inf
            index = cols[i][0]
            stars += columns[index].value
            remaining += column_width[index]
            new_ratio = remaining / stars
            if new_ratio < next_ratio:
                for j in range(i + 1):
                    index = cols[j][0]
                    column_width[index] = new_ratio * columns[index].value
                break
