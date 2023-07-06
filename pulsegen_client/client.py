import msgpack
import numpy as np
import requests

from pulsegen_client.contracts import PulseGenRequest


class PulseGenClient:
    def __init__(self, hostname="localhost", port=5200) -> None:
        self._hostname = hostname
        self._port = port
        self._session = requests.Session()

    def run(self, request: PulseGenRequest):
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}/run"
        headers = {"Content-Type": "application/msgpack"}
        response = self._session.post(url, data=msg, headers=headers)
        response.raise_for_status()
        response_obj = msgpack.unpackb(response.content)[0]
        result = {}
        for i, channel in enumerate(request.channels):
            result[channel.name] = (
                np.frombuffer(response_obj[i][0], dtype=np.float64),
                np.frombuffer(response_obj[i][1], dtype=np.float64),
            )
        return result
