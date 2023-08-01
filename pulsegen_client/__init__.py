"""This module provides a client for the pulsegen service.

The client can be used to send requests to the pulsegen server and receive the
result. There are two clients available: a synchronous client and an asynchronous
client.

.. note::
    All phase values are in number of cycles. For example, a phase of 0.25 means
    pi/2 radians.

.. warning::
    This package is still in development and the API may change in the future.
"""

from .client import PulseGenAsyncClient, PulseGenClient
from .contracts import Biquad, ChannelInfo, IqCalibration
from .runner import run_schedule
from .schedule import (
    Absolute,
    Alignment,
    Barrier,
    Grid,
    Play,
    Repeat,
    Request,
    SetFrequency,
    SetPhase,
    ShiftFrequency,
    ShiftPhase,
    Stack,
    SwapPhase,
)
from .shape import HannShape, InterpolatedShape, TriangleShape

__all__ = [
    "PulseGenAsyncClient",
    "PulseGenClient",
    "ChannelInfo",
    "Biquad",
    "IqCalibration",
    "run_schedule",
    "Absolute",
    "Alignment",
    "Barrier",
    "Grid",
    "Play",
    "Repeat",
    "Request",
    "SetFrequency",
    "SetPhase",
    "ShiftFrequency",
    "ShiftPhase",
    "Stack",
    "SwapPhase",
    "HannShape",
    "InterpolatedShape",
    "TriangleShape",
]
