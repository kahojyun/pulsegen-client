from time import perf_counter

import numpy as np
from matplotlib import pyplot as plt

from pulsegen_client.client import PulseGenClient
from pulsegen_client.contracts import RequestBuilder

if __name__ == "__main__":
    t0 = perf_counter()

    builder = RequestBuilder()
    builder.add_channel("ch1", 130e6, 2e9, 0, 100000, -4)
    builder.add_channel("ch2", 210e6, 1e9, 100e-9, 50000, -4)
    for i in range(900):
        builder.play(i * 50e-9, "ch1", "hann", 30e-9, 10e-9, 0, 0, 0.5, 0.5e-9)
        builder.play(i * 50e-9, "ch2", "hann", 30e-9, 10e-9, 0, 0, 0.3, 0.5e-9)
    req = builder.build()

    t1 = perf_counter()

    client = PulseGenClient(port=5249)
    result = client.run(req)

    t2 = perf_counter()

    print(result)
    print(f"Build time: {t1 - t0:.3f}s")
    print(f"Run time: {t2 - t1:.3f}s")

    t1 = np.arange(0, 100000) / 2e-9
    plt.plot(t1, result["ch1"][0])
    plt.plot(t1, result["ch1"][1])
    t2 = np.arange(0, 50000) / 1e-9
    plt.plot(t2, result["ch2"][0])
    plt.plot(t2, result["ch2"][1])
    plt.show()
