"""An example of using the client to generate a pulse sequence.

.. note::

    The server must be running for this example to work.
"""

import asyncio
from time import perf_counter

import numpy as np
import requests
from aiohttp import ClientSession
from matplotlib import pyplot as plt

from pulsegen_client import *

PORT = 5000


def run_sync(req: Request):
    with requests.Session() as session:
        client = PulseGenClient(session, port=PORT)
        return client.run_schedule(req)


async def run_async(req: Request):
    async with ClientSession() as session:
        client = PulseGenAsyncClient(session, port=PORT)
        return await client.run_schedule(req)


if __name__ == "__main__":
    t0 = perf_counter()

    channels = [
        ChannelInfo("xy0", 0, 2e9, 0, 100000, -10),
        ChannelInfo("xy1", 0, 2e9, 0, 100000, -10),
        ChannelInfo("u0", 0, 2e9, 0, 100000, -10),
        ChannelInfo("m0", 0, 2e9, 0, 100000, 0),
    ]
    c = {ch.name: i for i, ch in enumerate(channels)}
    halfcos = np.sin(np.linspace(0, np.pi, 10))
    shapes = [
        HannShape(),
        InterpolatedShape(np.linspace(-0.5, 0.5, 10), halfcos),
    ]
    s = {"hann": 0, "rect": -1, "halfcos": 1}

    measure = Absolute().with_children(
        Play(c["m0"], 0.1, s["hann"], 30e-9, plateau=1e-6, frequency=123e6),
        Play(c["m0"], 0.15, s["hann"], 30e-9, plateau=1e-6, frequency=-233e6),
    )
    c01 = Stack().with_children(
        Play(c["u0"], 0.5, s["halfcos"], 50e-9),
        ShiftPhase(c["xy0"], 0.1),
        ShiftPhase(c["xy1"], 0.2),
    )
    x0 = Play(c["xy0"], 0.3, s["hann"], 50e-9, drag_coef=5e-10)
    x1 = Play(c["xy1"], 0.4, s["hann"], 100e-9, drag_coef=3e-10)
    x_group = Grid().with_children(
        Stack([x0], alignment="center"),
        Stack([x1], alignment="center"),
    )

    schedule = Stack(duration=49.9e-6).with_children(
        Repeat(
            Stack().with_children(
                x_group,
                Barrier(duration=15e-9),
                c01,
            ),
            count=200,
            spacing=15e-9,
        ),
        Barrier(duration=15e-9),
        measure,
    )

    job = Request(channels, shapes, schedule)

    t1 = perf_counter()

    # result = run_sync(job)
    # result = asyncio.run(run_async(job))
    result = run_schedule(job)

    t2 = perf_counter()

    print(f"Build time: {t1 - t0:.3f}s")
    print(f"Run time: {t2 - t1:.3f}s")

    t = np.arange(100000) / 2e9
    plt.plot(t, result["xy0"][0])
    plt.plot(t, result["xy0"][1])
    plt.plot(t, result["xy1"][0])
    plt.plot(t, result["xy1"][1])
    plt.plot(t, result["u0"][0])
    plt.plot(t, result["u0"][1])
    plt.plot(t, result["m0"][0])
    plt.plot(t, result["m0"][1])
    plt.show()
