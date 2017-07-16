import asyncio
import json
from sys import exc_info
from traceback import format_exception

import aiohttp
import async_timeout

from . import custom_exceptions


async def basic_request(loop: asyncio.AbstractEventLoop, api_key: str, timeout_seconds: float, endpoint: str, *args,
                        method: str = "get", handle_ratelimiting: bool = False, **kwargs):
    """Does a basic request."""

    api_url = "https://api.rocketleaguestats.com/v"

    if "headers" not in kwargs:
        kwargs["headers"] = {}

    kwargs["headers"]["Authorization"] = api_key

    if handle_ratelimiting:
        raise NotImplementedError("Ratelimiting is not implemented.")
    else:
        try:
            with async_timeout.timeout(timeout_seconds):
                async with aiohttp.ClientSession(loop=loop) as session:
                    async with getattr(session, method)(api_url + endpoint, *args, **kwargs) as response:
                        response_text = await response.text()
                        return response.status, json.loads(response_text)
        except (asyncio.TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as e:
            # We didn't succeed with loading the url
            raise custom_exceptions.APIServerError(
                "Got an error when trying to request {0} from the api. More info:\n\n{1}".format(api_url + endpoint,
                                                                                                 "".join(
                                                                                                     format_exception(
                                                                                                         *exc_info()))))


def _add_request_parameters(func):
    """A decorator that adds some parameters to the decorated function, so those can be passed to basic_request."""

    # The function the decorator returns
    async def decorated_func(api_key: str, *args, handle_ratelimiting: bool = False, timeout_seconds: float = 5,
                             loop: asyncio.AbstractEventLoop, **kwargs):
        return await func(api_key, *args, handle_ratelimiting=handle_ratelimiting,
                          timeout_seconds=timeout_seconds, loop=loop, **kwargs)

    return decorated_func


@_add_request_parameters
async def get_platforms(api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, *args, **kwargs):
    return (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/platforms".format(api_version), *args,
                                **kwargs))[1]


@_add_request_parameters
async def get_seasons(api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, *args, **kwargs):
    return \
    (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/seasons".format(api_version), *args, **kwargs))[
        1]
