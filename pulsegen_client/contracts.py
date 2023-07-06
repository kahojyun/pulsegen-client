from typing import Iterable

import msgpack


class MsgObject:
    def __init__(self, data) -> None:
        self._data = data

    @property
    def data(self):
        return self._data

    def packb(self):
        def encode(obj: MsgObject):
            return obj.data

        return msgpack.packb(self, default=encode)


class UnionObject(MsgObject):
    def __init__(self, key: int, data):
        super().__init__([key, data])


class ChannelInfo(MsgObject):
    def __init__(
        self,
        name: str,
        base_freq: float,
        sample_rate: float,
        delay: float,
        length: int,
        align_level: int,
    ):
        super().__init__(
            [
                name,
                base_freq,
                sample_rate,
                delay,
                length,
                align_level,
            ]
        )
        self.name = name


class ShapeInfo(UnionObject):
    pass


class HannShape(ShapeInfo):
    def __init__(self):
        super().__init__(0, [])


class TriangleShape(ShapeInfo):
    def __init__(self):
        super().__init__(1, [])


class InterpolatedShape(ShapeInfo):
    def __init__(self, x: Iterable[float], y: Iterable[float]):
        super().__init__(2, [list(x), list(y)])


class Instruction(UnionObject):
    pass


class Play(Instruction):
    def __init__(
        self,
        time: float,
        channel_id: int,
        shape_id: int,
        width: float,
        plateau: float,
        frequency: float,
        phase: float,
        amplitude: float,
        drag_coef: float,
    ):
        super().__init__(
            0,
            [
                time,
                channel_id,
                shape_id,
                width,
                plateau,
                frequency,
                phase,
                amplitude,
                drag_coef,
            ],
        )


class ShiftPhase(Instruction):
    def __init__(self, channel_id: int, phase: float):
        super().__init__(1, [channel_id, phase])


class SetPhase(Instruction):
    def __init__(self, time: float, channel_id: int, phase: float):
        super().__init__(2, [time, channel_id, phase])


class ShiftFrequency(Instruction):
    def __init__(self, time: float, channel_id: int, frequency: float):
        super().__init__(3, [time, channel_id, frequency])


class SetFrequency(Instruction):
    def __init__(self, time: float, channel_id: int, frequency: float):
        super().__init__(4, [time, channel_id, frequency])


class SwapPhase(Instruction):
    def __init__(self, time: float, channel_id1: int, channel_id2: int):
        super().__init__(5, [time, channel_id1, channel_id2])


class PulseGenRequest(MsgObject):
    def __init__(
        self,
        channels: Iterable[ChannelInfo],
        shapes: Iterable[ShapeInfo],
        instructions: Iterable[Instruction],
    ):
        self.channels = list(channels)
        super().__init__([self.channels, list(shapes), list(instructions)])


class RequestBuilder:
    def __init__(self):
        self._channels: list[ChannelInfo] = []
        self._channel_ids: dict[str, int] = {}
        self._shapes: list[ShapeInfo] = [HannShape(), TriangleShape()]
        self._shape_ids = {
            "rect": -1,
            "hann": 0,
            "triangle": 1,
        }
        self._instructions: list[Instruction] = []

    def add_channel(
        self,
        name: str,
        base_freq: float,
        sample_rate: float,
        delay: float,
        length: int,
        align_level: int,
    ):
        if name in self._channel_ids:
            raise ValueError(f"Channel name {name} already exists")
        channel_id = len(self._channels)
        self._channels.append(
            ChannelInfo(
                name,
                base_freq,
                sample_rate,
                delay,
                length,
                align_level,
            )
        )
        self._channel_ids[name] = channel_id

    def play(
        self,
        time: float,
        channel_name: str,
        shape_name: str,
        width: float,
        plateau: float,
        frequency: float,
        phase: float,
        amplitude: float,
        drag_coef: float,
    ):
        channel_id = self._channel_ids[channel_name]
        shape_id = self._shape_ids[shape_name]
        self._instructions.append(
            Play(
                time,
                channel_id,
                shape_id,
                width,
                plateau,
                frequency,
                phase,
                amplitude,
                drag_coef,
            )
        )

    def shift_phase(self, channel_name: str, phase: float):
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftPhase(channel_id, phase))

    def set_phase(self, time: float, channel_name: str, phase: float):
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetPhase(time, channel_id, phase))

    def shift_frequency(self, time: float, channel_name: str, frequency: float):
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(ShiftFrequency(time, channel_id, frequency))

    def set_frequency(self, time: float, channel_name: str, frequency: float):
        channel_id = self._channel_ids[channel_name]
        self._instructions.append(SetFrequency(time, channel_id, frequency))

    def swap_phase(self, time: float, channel_name1: str, channel_name2: str):
        channel_id1 = self._channel_ids[channel_name1]
        channel_id2 = self._channel_ids[channel_name2]
        self._instructions.append(SwapPhase(time, channel_id1, channel_id2))

    def build(self):
        return PulseGenRequest(self._channels, self._shapes, self._instructions)
