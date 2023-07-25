import math
from typing import Dict, Tuple

import numpy as np

import pulsegen_client.pulse as pulse
import pulsegen_client.runner.layout as layout
import pulsegen_client.schedule as schedule
from pulsegen_client.runner.phase_tracker import PhaseTracker
from pulsegen_client.runner.shape import Envelope, get_shape


def run_simple(request: pulse.Request) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Run a simple pulse sequence.

    :param request: The request to run.
    :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
    """
    channels = request.channels
    shapes = [get_shape(shape) for shape in request.shapes]
    phase_tracker = PhaseTracker([ch.base_freq for ch in channels])
    for item in request.instructions:
        if isinstance(item, pulse.Play):
            if item.shape_id == -1:
                shape = None
            else:
                shape = shapes[item.shape_id]
            envelope = Envelope(shape, item.width, item.plateau)
            phase_tracker.play(
                item.channel_id,
                envelope,
                item.frequency,
                item.phase,
                item.amplitude,
                item.drag_coef,
                item.time,
            )
        elif isinstance(item, pulse.ShiftFrequency):
            phase_tracker.shift_freq(item.channel_id, item.frequency, item.time)
        elif isinstance(item, pulse.SetFrequency):
            phase_tracker.set_freq(item.channel_id, item.frequency, item.time)
        elif isinstance(item, pulse.ShiftPhase):
            phase_tracker.shift_phase(item.channel_id, item.phase)
        elif isinstance(item, pulse.SetPhase):
            phase_tracker.set_phase(item.channel_id, item.phase, item.time)
        elif isinstance(item, pulse.SwapPhase):
            phase_tracker.swap_phase(item.channel_id1, item.channel_id2, item.time)
        else:
            raise ValueError(f"Unknown instruction type: {type(item)}")
    pulses = phase_tracker.finish()
    waveforms = {}
    for ch, pulse_list in zip(channels, pulses):
        pulse_list.delay(ch.delay)
        y = pulse_list.sample(ch.length, ch.sample_rate, ch.align_level)
        waveforms[ch.name] = (y.real, y.imag)
    return waveforms


def run_schedule(request: schedule.Request) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Run a pulse sequence defined by a schedule.

    :param request: The request to run.
    :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
    """
    channels = request.channels
    shapes = [get_shape(shape) for shape in request.shapes]
    phase_tracker = PhaseTracker([ch.base_freq for ch in channels])
    lm = layout.create_layout_manager(request.schedule)
    lm.measure(math.inf)
    assert lm.desired_duration is not None
    lm.arrange(0.0, lm.desired_duration)
    lm.render(0.0, phase_tracker, shapes)
    pulses = phase_tracker.finish()
    waveforms = {}
    for ch, pulse_list in zip(channels, pulses):
        pulse_list.delay(ch.delay)
        y = pulse_list.sample(ch.length, ch.sample_rate, ch.align_level)
        waveforms[ch.name] = (y.real, y.imag)
    return waveforms
