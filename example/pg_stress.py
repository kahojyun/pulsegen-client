"""An example of using the client to generate a pulse sequence.

.. note::

    The server must be running for this example to work.
"""

import asyncio
from time import perf_counter

import numpy as np
from aiohttp import ClientSession

from pulsegen_client import PulseGenAsyncClient, RequestBuilder

PORT = 5000


async def gen(client: PulseGenAsyncClient):
    t0 = perf_counter()
    builder = RequestBuilder()
    for i in range(50):
        builder.add_channel(f"ch{i}", i * 5e6, 2e9, 0, 100000, -10)
    x = np.linspace(0, np.pi, 11)
    y = np.sin(x)
    xx = np.linspace(-0.5, 0.5, 11)
    builder.add_interpolated_shape("halfcos", xx, y)
    for i in range(900):
        for j in range(50):
            builder.play(i * 50e-9, f"ch{j}", 0.3, "halfcos", 30e-9)
            builder.shift_phase(f"ch{j}", 0.25)
    job = builder.build()
    t1 = perf_counter()
    await client.run(job)
    t2 = perf_counter()
    print(f"Build time: {t1 - t0:.3f}s, run time: {t2 - t1:.3f}s")


async def main():
    async with ClientSession() as session:
        client = PulseGenAsyncClient(session, port=PORT)
        while True:
            await gen(client)


if __name__ == "__main__":
    asyncio.run(main())
