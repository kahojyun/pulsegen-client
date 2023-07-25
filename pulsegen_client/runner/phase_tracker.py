from typing import List

from attrs import define, field

from pulsegen_client.runner.pulse_list import PulseList
from pulsegen_client.runner.shape import Envelope


@define
class _ChannelStatus:
    base_freq: float
    delta_freq: float = 0.0
    phase: float = 0.0
    pulses: PulseList = field(factory=PulseList)

    @property
    def total_freq(self) -> float:
        return self.base_freq + self.delta_freq

    def shift_freq(self, delta: float, time: float) -> None:
        self.phase -= delta * time
        self.delta_freq += delta

    def set_freq(self, freq: float, time: float) -> None:
        self.phase -= (freq - self.delta_freq) * time
        self.delta_freq = freq

    def shift_phase(self, delta: float) -> None:
        self.phase += delta

    def set_phase(self, phase: float, time: float) -> None:
        self.phase = phase - self.delta_freq * time

    @staticmethod
    def swap_phase(a: "_ChannelStatus", b: "_ChannelStatus", time: float) -> None:
        diff = a.total_freq - b.total_freq
        a.phase, b.phase = b.phase - diff * time, a.phase + diff * time


class PhaseTracker:
    def __init__(self, base_freqs: List[float]) -> None:
        self.channels = [_ChannelStatus(base_freq) for base_freq in base_freqs]

    def shift_freq(self, channel: int, delta: float, time: float) -> None:
        self.channels[channel].shift_freq(delta, time)

    def set_freq(self, channel: int, freq: float, time: float) -> None:
        self.channels[channel].set_freq(freq, time)

    def shift_phase(self, channel: int, delta: float) -> None:
        self.channels[channel].shift_phase(delta)

    def set_phase(self, channel: int, phase: float, time: float) -> None:
        self.channels[channel].set_phase(phase, time)

    def swap_phase(self, a: int, b: int, time: float) -> None:
        _ChannelStatus.swap_phase(self.channels[a], self.channels[b], time)

    def play(
        self,
        channel: int,
        env: Envelope,
        freq: float,
        phase: float,
        amp: float,
        drag_coef: float,
        time: float,
    ):
        freq_g = self.channels[channel].total_freq
        total_phase = self.channels[channel].phase + phase
        self.channels[channel].pulses.add_pulse(
            env, freq_g, freq, time, total_phase, amp, drag_coef
        )

    def finish(self) -> List[PulseList]:
        return [ch.pulses for ch in self.channels]
