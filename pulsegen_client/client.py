"""Clients for the pulsegen server.
"""
import typing as _typing

import aiohttp as _aiohttp
import msgpack as _msgpack
import numpy as _np
import requests as _requests

import pulsegen_client.contracts as _cts
import pulsegen_client.schedule as _schedule

SCHEDULE_ENDPOINT = "/api/schedule"
MIME_TYPE = "application/msgpack"


def _unpack_response(
    channels: _typing.Iterable[_cts.ChannelInfo], content: bytes
) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
    """Unpack the binary response from the server.

    :param channels: Channel information from the corresponding request.
    :param content: The binary response.
    :return: The unpacked response. The keys are the channel names and the
        values are tuples of (I, Q) arrays.
    """
    response_obj = _msgpack.unpackb(content)[0]
    result = {}
    for i, channel in enumerate(channels):
        result[channel.name] = (
            _np.frombuffer(response_obj[i][0], dtype=_np.float64),
            _np.frombuffer(response_obj[i][1], dtype=_np.float64),
        )
    return result


class PulseGenClient:
    """Synchronous client for the pulsegen server.

    :param session: The requests session to use.
    :param hostname: The hostname of the server.
    :param port: The port of the server.
    """

    def __init__(
        self, session: _requests.Session, hostname: str = "localhost", port: int = 5000
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    def run_schedule(
        self, request: _schedule.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}{SCHEDULE_ENDPOINT}"
        headers = {"Content-Type": MIME_TYPE}
        response = self._session.post(url, data=msg, headers=headers)
        response.raise_for_status()
        return _unpack_response(request.channels, response.content)


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
        port: int = 5000,
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._session = session

    async def run_schedule(
        self, request: _schedule.Request
    ) -> _typing.Dict[str, _typing.Tuple[_np.ndarray, _np.ndarray]]:
        """Run the pulsegen server with the given request.

        :param request: The request to send to the server.
        :return: The result of the request. The keys are the channel names and the
            values are tuples of (I, Q) arrays.
        """
        msg = request.packb()
        url = f"http://{self._hostname}:{self._port}{SCHEDULE_ENDPOINT}"
        headers = {"Content-Type": MIME_TYPE}
        async with self._session.post(url, data=msg, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()
        return _unpack_response(request.channels, content)
