import math
from typing import Dict, Tuple

import numpy as np

import pulsegen_client.runner._layout as _layout
import pulsegen_client.schedule as schedule
from pulsegen_client.runner._phase_tracker import PhaseTracker
from pulsegen_client.runner._shape_impl import get_shape


def run_schedule(request: schedule.Request) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Run a pulse sequence defined by a schedule.

    :param request: The request to run.
    :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
    """
    channels = request.channels
    shapes = [get_shape(shape) for shape in request.shapes]
    phase_tracker = PhaseTracker([ch.base_freq for ch in channels])
    lm = _layout.create_layout_manager(request.schedule)
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
