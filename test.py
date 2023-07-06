from itertools import product
from time import perf_counter

import msgpack
import numpy as np
import requests


def test(s):
    t0 = perf_counter()
    job = [
        [(f"ch{i}", i * 2e6, 2e9, i * 10e-9, 100000, -4) for i in range(64)],
        [
            (0, tuple()),
            (1, tuple()),
        ],
        [
            (0, (j, i, 0, 40e-9, 0, 0, 0, 0.5, 0.5e-9))
            for i, j in product(range(64), 50e-9 * np.arange(900))
        ],
    ]
    msg = msgpack.packb(job)
    t1 = perf_counter()
    headers = {"Content-Type": "application/msgpack"}
    # r = s.post("http://localhost:5249/run", data=msg, headers=headers, timeout=10)
    r = s.post("http://localhost:5200/run", data=msg, headers=headers, timeout=10)
    t2 = perf_counter()
    result = msgpack.unpackb(r.content)[0]
    t3 = perf_counter()
    i1 = np.frombuffer(result[0][0], dtype=np.float64)
    q1 = np.frombuffer(result[0][1], dtype=np.float64)
    i2 = np.frombuffer(result[-1][0], dtype=np.float64)
    q2 = np.frombuffer(result[-1][1], dtype=np.float64)
    t4 = perf_counter()
    print(i1.shape, q1.shape, i2.shape, q2.shape)
    print(t1 - t0, t2 - t1, t3 - t2, t4 - t3)


if __name__ == "__main__":
    session = requests.Session()
    for _ in range(100):
        test(session)
