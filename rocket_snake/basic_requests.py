import asyncio
import json
import time
from collections import deque
from sys import exc_info
from traceback import format_exception

import aiohttp
import async_timeout

from . import custom_exceptions

# This is used to keep track of the queues for each key, structure: {API_KEY: deque([task1, task2, task3])}
ratelimit_key_queue_map = {}
# This is used to keep track of the last times a key was used, structure: {API_KEY: float (time.time())}
ratelimit_key_time_map = {}


def _get_float(data, default):
    try:
        return float(data)
    except ValueError:
        return default


def _get_int(data, default):
    try:
        return int(data)
    except ValueError:
        return default

async def basic_request(loop: asyncio.AbstractEventLoop, api_key: str, timeout_seconds: float, endpoint: str, *args,
                        method: str = "get", handle_ratelimiting: bool = False, _cur_retry: int = 0, **kwargs):
    """Does a basic request. Not threadsafe for the same api key with multiple clients."""

    global ratelimit_key_queue_map, ratelimit_key_time_map

    api_url = "https://api.rocketleaguestats.com/v"

    if "headers" not in kwargs:
        kwargs["headers"] = {}

    kwargs["headers"]["Authorization"] = api_key

    if handle_ratelimiting:
        key_queue = ratelimit_key_queue_map.get(api_key, None)

        our_task_num = time.time()

        if key_queue is None or len(key_queue) == 0:
            ratelimit_key_queue_map[api_key] = deque([our_task_num])
        else:
            ratelimit_key_queue_map[api_key].append(our_task_num)

        # We wait until it's our turn
        while ratelimit_key_queue_map[api_key][0] != our_task_num:
            # Basically, this shouldn't be too large because that increases latency, but not too small because that increases cpu usage.
            await asyncio.sleep(0.1)

        # Now it's our turn
        # If the last request was less than 2 seconds ago we need to wait
        throughput_time_seconds = 0.5
        if time.time() - ratelimit_key_time_map.get(api_key, 0) < throughput_time_seconds:
            await asyncio.sleep(throughput_time_seconds - (time.time() - ratelimit_key_time_map[api_key]))

    try:
        with async_timeout.timeout(timeout_seconds):
            async with aiohttp.ClientSession(loop=loop) as session:
                async with getattr(session, method)(api_url + endpoint, *args, **kwargs) as response:
                    response_text = await response.text()
                    if response.status == 429:
                        # If we should handle this we wait for the rate-limit period to end
                        if handle_ratelimiting:
                            if _cur_retry < 6:
                                await asyncio.sleep(
                                    _get_int(response.headers.get("retry-after"), throughput_time_seconds))
                                ratelimit_key_queue_map[api_key].popleft()
                                return await basic_request(loop=loop, api_key=api_key, timeout_seconds=timeout_seconds,
                                                           endpoint=endpoint, *args, method=method,
                                                           handle_ratelimiting=handle_ratelimiting,
                                                           _cur_retry=_cur_retry + 1, **kwargs)
                        raise custom_exceptions.RateLimitError(
                            "The HTTP response code was 429, which means you were rate-limited.")
                    elif response.status >= 300:
                        raise custom_exceptions.APIBadResponseCodeError(
                            "The HTTP response code was {0}, which is not a good one.".format(response.status))
                    return response.status, json.loads(response_text)
    except (asyncio.TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as e:
        # We didn't succeed with loading the url
        raise custom_exceptions.APIServerError(
            "Got an error when trying to request {0} from the api. More info:\n\n{1}".format(
                api_url + endpoint, "".join(format_exception(*exc_info()))))

    finally:
        # If we have a task to remove, we do
        if handle_ratelimiting:
            if len(ratelimit_key_queue_map[api_key]) > 0:
                ratelimit_key_queue_map[api_key].popleft()

            # We set the last time this key was used
            ratelimit_key_time_map[api_key] = time.time()


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
async def get_playlists(api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, *args, **kwargs):
    return \
        (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/playlists".format(api_version), *args,
                             **kwargs))[1]
