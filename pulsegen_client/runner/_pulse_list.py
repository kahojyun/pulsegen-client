import cmath
import math
from typing import Iterable, MutableSequence, Optional

import numpy as np
from attrs import frozen

from pulsegen_client.runner._shape_impl import Envelope


@frozen
class PulseItem:
    time: float
    envelope: Envelope
    amp: complex
    drag_amp: complex
    freq_g: float
    freq_l: float
    delay: float


class PulseList(MutableSequence[PulseItem]):
    def __init__(self, items: Optional[Iterable[PulseItem]] = None) -> None:
        self._items = list(items) if items is not None else []

    def __getitem__(self, index: int) -> PulseItem:
        return self._items[index]

    def __setitem__(self, index: int, value: PulseItem) -> None:
        self._items[index] = value

    def __delitem__(self, index: int) -> None:
        del self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def insert(self, index: int, value: PulseItem) -> None:
        self._items.insert(index, value)

    def add_pulse(
        self,
        env: Envelope,
        freq_g: float,
        freq_l: float,
        time: float,
        phase: float,
        amp: float,
        drag_coef: float,
    ) -> None:
        if amp == 0:
            return
        camp = cmath.rect(amp, math.tau * phase)
        cdrag = 1j * camp * drag_coef
        self._items.append(
            PulseItem(
                time=time,
                envelope=env,
                amp=camp,
                drag_amp=cdrag,
                freq_g=freq_g,
                freq_l=freq_l,
                delay=0,
            )
        )

    def delay(self, delay: float) -> None:
        self._items = [
            PulseItem(
                time=item.time + delay,
                envelope=item.envelope,
                amp=item.amp,
                drag_amp=item.drag_amp,
                freq_g=item.freq_g,
                freq_l=item.freq_l,
                delay=item.delay + delay,
            )
            for item in self._items
        ]

    def __mul__(self, other: complex) -> "PulseList":
        return PulseList(
            PulseItem(
                time=item.time,
                envelope=item.envelope,
                amp=item.amp * other,
                drag_amp=item.drag_amp * other,
                freq_g=item.freq_g,
                freq_l=item.freq_l,
                delay=item.delay,
            )
            for item in self._items
        )

    def __rmul__(self, other: complex) -> "PulseList":
        return self * other

    def __imul__(self, other: complex) -> "PulseList":
        self._items = [
            PulseItem(
                time=item.time,
                envelope=item.envelope,
                amp=item.amp * other,
                drag_amp=item.drag_amp * other,
                freq_g=item.freq_g,
                freq_l=item.freq_l,
                delay=item.delay,
            )
            for item in self._items
        ]
        return self

    def sample(self, length: int, sample_rate: float, align_level: int) -> np.ndarray:
        dt = 1 / sample_rate
        t = np.arange(length) * dt
        y = np.zeros(length, dtype=np.complex128)
        scaled_sample_rate: float = sample_rate * 2 ** (-align_level)
        for item in self._items:
            aligned_time = round(item.time * scaled_sample_rate) / scaled_sample_rate
            i_start = math.floor(aligned_time * sample_rate)
            i_end = math.ceil((aligned_time + item.envelope.duration) * sample_rate)
            item_t = t[i_start:i_end] - aligned_time
            item_y = item.envelope.sample(item_t)
            item_y_drag = np.gradient(item_y) * sample_rate
            phase_shift = math.tau * item.freq_g * (i_start * dt - item.delay)
            phase = math.tau * (item.freq_g + item.freq_l) * item_t + phase_shift
            carrier = np.cos(phase) + 1j * np.sin(phase)
            y[i_start:i_end] += (
                item_y * item.amp + item_y_drag * item.drag_amp
            ) * carrier
        return y
