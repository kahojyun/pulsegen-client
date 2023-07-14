"""This module provides a client for the pulsegen service.

The client can be used to send requests to the pulsegen server and receive the
result. There are two clients available: a synchronous client and an asynchronous
client.

.. note::
    All phase values are in number of cycles. For example, a phase of 0.25 means
    pi/2 radians.

.. warning::
    This package is still in development and the API may change in the future.
"""

from .client import PulseGenAsyncClient, PulseGenClient
from .contracts import PulseGenRequest, RequestBuilder

__all__ = ["PulseGenClient", "PulseGenAsyncClient", "PulseGenRequest", "RequestBuilder"]
