from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import numpy.typing as npt
import scipy.interpolate as interp
from attrs import frozen

import pulsegen_client.shape as shape


class PulseShape(ABC):
    @abstractmethod
    def sample(self, x: np.ndarray) -> np.ndarray:
        ...


class HannShape(PulseShape):
    def sample(self, x: np.ndarray) -> np.ndarray:
        return np.piecewise(
            x,
            [(-0.5 < x) & (x < 0.5)],
            [lambda x: 0.5 * (1 + np.cos(2 * np.pi * x))],
        )


class TriangleShape(PulseShape):
    def sample(self, x: np.ndarray) -> np.ndarray:
        return np.piecewise(
            x,
            [(-0.5 < x) & (x < 0.5)],
            [lambda x: 1 - 2 * np.abs(x)],
        )


class InterpolatedShape(PulseShape):
    def __init__(self, x: npt.ArrayLike, y: npt.ArrayLike) -> None:
        self.interpolator = interp.BarycentricInterpolator(x, y)

    def sample(self, x: np.ndarray) -> np.ndarray:
        return np.piecewise(
            x,
            [(-0.5 < x) & (x < 0.5)],
            [self.interpolator],
        )


@frozen
class Envelope:
    shape: Optional[PulseShape]
    width: float
    plateau: float = 0.0

    @property
    def duration(self) -> float:
        return self.width + self.plateau

    def sample(self, t: np.ndarray) -> np.ndarray:
        shape = self.shape
        if shape is None:
            return np.ones_like(t)
        t1 = self.width / 2
        t2 = self.width / 2 + self.plateau
        t3 = self.width + self.plateau
        return np.piecewise(
            t,
            [
                (0 <= t) & (t < t1),
                (t1 <= t) & (t < t2),
                (t2 <= t) & (t < t3),
            ],
            [
                lambda t: shape.sample((t - t1) / self.width),
                1,
                lambda t: shape.sample((t - t2) / self.width),
            ],
        )


def get_shape(info: shape.ShapeInfo) -> PulseShape:
    if isinstance(info, shape.HannShape):
        return HannShape()
    if isinstance(info, shape.TriangleShape):
        return TriangleShape()
    if isinstance(info, shape.InterpolatedShape):
        return InterpolatedShape(info.x_array, info.y_array)
    raise ValueError(f"Unknown shape type: {type(info)}")
