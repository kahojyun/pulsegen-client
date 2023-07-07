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

from pulsegen_client import PulseGenAsyncClient, PulseGenClient, RequestBuilder

PORT = 5200


def run_sync(req):
    session = requests.Session()
    client = PulseGenClient(session, port=PORT)
    return client.run(req)


async def run_async(req):
    async with ClientSession() as session:
        client = PulseGenAsyncClient(session, port=PORT)
        return await client.run(req)


if __name__ == "__main__":
    t0 = perf_counter()

    builder = RequestBuilder()
    builder.add_channel("ch1", 0e6, 2e9, 0, 100000, -4)
    builder.add_channel("ch2", 0, 1e9, 100e-9, 50000, -4)
    x = np.linspace(0, np.pi, 11)
    y = np.sin(x)
    xx = np.linspace(-0.5, 0.5, 11)
    builder.add_interpolated_shape("halfcos", xx, y)
    for i in range(900):
        builder.play(i * 50e-9, "ch1", 0.5, "hann", 45e-9, 0, 0.5e-9)
        builder.play(i * 50e-9, "ch2", 0.3, "halfcos", 30e-9)
        builder.shift_phase("ch1", 0.25)
    job = builder.build()

    t1 = perf_counter()

    result = run_sync(job)

    t2 = perf_counter()

    result = asyncio.run(run_async(job))

    t3 = perf_counter()

    print(f"Build time: {t1 - t0:.3f}s")
    print(f"Synchronous run time: {t2 - t1:.3f}s")
    print(f"Asynchronous run time: {t3 - t2:.3f}s")

    t1 = np.arange(0, 100000) / 2e-9
    plt.plot(t1, result["ch1"][0])
    plt.plot(t1, result["ch1"][1])
    t2 = np.arange(0, 50000) / 1e-9
    plt.plot(t2, result["ch2"][0])
    plt.plot(t2, result["ch2"][1])
    plt.show()
