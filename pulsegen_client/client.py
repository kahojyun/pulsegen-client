"""Clients for the pulsegen server.
"""

import numpy as np
from aiohttp import ClientSession
from requests import Session

from pulsegen_client.contracts import PulseGenRequest, unpack_response


class PulseGenClient:
    """Synchronous client for the pulsegen server.

    :param session: The requests session to use.
    :param hostname: The hostname of the server.
    :param port: The port of the server.
    """

    def __init__(self, session: Session, hostname="localhost", port=5200) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    def run(self, request: PulseGenRequest) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}/run"
        headers = {"Content-Type": "application/msgpack"}
        response = self._session.post(url, data=msg, headers=headers)
        response.raise_for_status()
        return unpack_response(request.channels, response.content)


class PulseGenAsyncClient:
    """Asynchronous client for the pulsegen server.

    :param session: The aiohttp session to use.
    :param hostname: The hostname of the server.
    :param port: The port of the server.
    """

    def __init__(self, session: ClientSession, hostname="localhost", port=5200) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    async def run(
        self, request: PulseGenRequest
    ) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}/run"
        headers = {"Content-Type": "application/msgpack"}
        async with self._session.post(url, data=msg, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()
        return unpack_response(request.channels, content)
