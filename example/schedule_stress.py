"""An example of using the client to generate a pulse sequence.

.. note::

    The server must be running for this example to work.
"""

import asyncio
from itertools import cycle

from aiohttp import ClientSession

from pulsegen_client import PulseGenAsyncClient
from pulsegen_client.contracts import ChannelInfo
from pulsegen_client.pulse import HannShape
from pulsegen_client.schedule import (
    Absolute,
    Alignment,
    Barrier,
    Grid,
    Play,
    Repeat,
    Request,
    Stack,
)

PORT = 5000


async def gen_n(n: int, client: PulseGenAsyncClient):
    channels = [
        ChannelInfo("xy0", 0, 2e9, 0, 100000, -10),
        ChannelInfo("xy1", 0, 2e9, 0, 100000, -10),
        ChannelInfo("m0", 0, 2e9, 0, 100000, 0),
    ]
    c = {ch.name: i for i, ch in enumerate(channels)}
    shapes = [
        HannShape(),
    ]
    s = {"hann": 0, "rect": -1}

    measure = Absolute(
        [
            Play(c["m0"], 0.1, s["hann"], 30e-9, plateau=1e-6, frequency=123e6),
            Play(c["m0"], 0.15, s["hann"], 30e-9, plateau=1e-6, frequency=-233e6),
        ]
    )

    x0 = Play(c["xy0"], 0.3, s["hann"], 50e-9, drag_coef=5e-10)
    x1 = Play(c["xy1"], 0.4, s["hann"], 100e-9, drag_coef=3e-10)
    x_group = Grid(
        [
            Stack([x0], alignment=Alignment.CENTER),
            Stack([x1], alignment=Alignment.CENTER),
        ]
    )

    schedule = Stack(
        [
            Repeat(x_group, n, spacing=100e-9),
            Barrier([c["xy0"], c["xy1"]], duration=15e-9),
            x_group,
            Barrier([c["xy0"], c["xy1"]], duration=15e-9),
            x0,
            x1,
            Barrier([c["xy0"], c["xy1"], c["m0"]], duration=15e-9),
            measure,
        ],
        duration=49.9e-6,
    )

    job = Request(channels, shapes, schedule)

    await client.run_schedule(job)


async def main():
    async with ClientSession() as session:
        client = PulseGenAsyncClient(session, port=PORT)
        for i in cycle(range(1, 100)):
            print(i)
            await gen_n(i, client)
            # await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
