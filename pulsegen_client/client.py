"""Clients for the pulsegen server.
"""
import typing as _typing

import aiohttp as _aiohttp
import numpy as _np
import requests as _requests

import pulsegen_client.contracts as _cts
import pulsegen_client.pulse as _pulse
import pulsegen_client.schedule as _schedule


class PulseGenClient:
    """Synchronous client for the pulsegen server.

    :param session: The requests session to use.
    :param hostname: The hostname of the server.
    :param port: The port of the server.
    """

    def __init__(
        self, session: _requests.Session, hostname: str = "localhost", port: int = 5200
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    def run(
        self, request: _pulse.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
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
        return _cts.unpack_response(request.channels, response.content)

    def run_schedule(
        self, request: _schedule.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}/schedule"
        headers = {"Content-Type": "application/msgpack"}
        response = self._session.post(url, data=msg, headers=headers)
        response.raise_for_status()
        return _cts.unpack_response(request.channels, response.content)


class PulseGenAsyncClient:
    """Asynchronous client for the pulsegen server.

    :param session: The aiohttp session to use.
    :param hostname: The hostname of the server.
    :param port: The port of the server.
    """

    def __init__(
        self,
        session: _aiohttp.ClientSession,
        hostname: str = "localhost",
        port: int = 5200,
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    async def run(
        self, request: _pulse.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
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
        return _cts.unpack_response(request.channels, content)

    async def run_schedule(
        self, request: _schedule.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}/schedule"
        headers = {"Content-Type": "application/msgpack"}
        async with self._session.post(url, data=msg, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()
        return _cts.unpack_response(request.channels, content)
