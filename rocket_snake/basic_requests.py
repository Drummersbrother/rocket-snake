"""
   Copyright 2017 Hugo Berg

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import asyncio
import json
import time
import urllib.parse as url_parser
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
                        method: str = "get", handle_ratelimiting: bool = False, _cur_retry: int = 6, **kwargs):
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
        # The least amount of time we allow between requests
        # This is a big optimizer, but the best value depends on a users ping to the api server. The optimal value can be calculated by ((0.5 seconds) - (user_ping in seconds)) + safety_margin
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
                            if _cur_retry == 0:
                                await asyncio.sleep(
                                        _get_int(response.headers.get("retry-after-ms"),
                                                 throughput_time_seconds * 1000) / 1000)
                                ratelimit_key_queue_map[api_key].remove(our_task_num)
                                return await basic_request(loop=loop, api_key=api_key, timeout_seconds=timeout_seconds,
                                                           endpoint=endpoint, *args, method=method,
                                                           handle_ratelimiting=handle_ratelimiting,
                                                           _cur_retry=_cur_retry - 1, **kwargs)
                        raise custom_exceptions.RateLimitError(
                                "The HTTP response code was 429, which means you were rate-limited.")
                    elif response.status == 404:
                        raise custom_exceptions.APINotFoundError(
                                "The requested resource could not be found by the RLS API.")
                    elif response.status == 401:
                        raise custom_exceptions.InvalidAPIKeyError(
                                "The HTTP response code was 401, which means that your API key wasn't valid.")
                    elif response.status >= 300:
                        raise custom_exceptions.APIBadResponseCodeError(
                                "The HTTP response code was {0}, which is not a good one. \n"
                                "The response headers were: \n{6}\n"
                                "The response was: \n{2}\n"
                                "The query headers were: \n{1}\n"
                                "The query was a {3} one, and the endpoint was {4}.\n{5}"
                                    .format(response.status, kwargs["headers"],
                                            "\n\t".join((await response.text()).split("\n")), method.upper(),
                                            api_url + endpoint,
                                            "The json data sent to the endpoint by the API was:\n{0}\n"
                                            .format(kwargs["json"]) if "json" in kwargs else "",
                                            dict(response.headers)))
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
                try:
                    ratelimit_key_queue_map[api_key].remove(our_task_num)
                except ValueError:
                    pass

            # We set the last time this key was used
            ratelimit_key_time_map[api_key] = time.time()


def _add_request_parameters(func):
    """A decorator that adds some parameters to the decorated function, so those can be passed to basic_request."""

    # The function the decorator returns
    async def decorated_func(*args, api_key: str = "", handle_ratelimiting: bool = False, timeout_seconds: float = 15,
                             api_version: int = 1, loop: asyncio.AbstractEventLoop = None, **kwargs):
        return await func(*args, api_key=api_key, loop=loop,
                          handle_ratelimiting=handle_ratelimiting, api_version=api_version,
                          timeout_seconds=timeout_seconds)

    return decorated_func


@_add_request_parameters
async def get_platforms(*args, api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/platforms".format(api_version), *args,
                                **kwargs))[1]


@_add_request_parameters
async def get_playlists(*args, api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return \
        (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/playlists".format(api_version), *args,
                             **kwargs))[1]


@_add_request_parameters
async def get_seasons(*args, api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return \
        (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/seasons".format(api_version), *args,
                             **kwargs))[1]


@_add_request_parameters
async def get_tiers(*args, api_key: str, loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return \
        (await basic_request(loop=loop, api_key=api_key, endpoint="{0}/data/tiers".format(api_version), *args,
                             **kwargs))[1]


@_add_request_parameters
async def get_ranked_leaderboard(playlist_id: int, *args, api_key: str,
                                 loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return (await basic_request(
            loop=loop, api_key=api_key, endpoint="{0}/leaderboard/ranked".format(
                    api_version), *args,
            params={"playlist_id": playlist_id}, **kwargs))[1]


@_add_request_parameters
async def get_stats_leaderboard(stat_type: str, *args, api_key: str,
                                loop: asyncio.AbstractEventLoop, api_version: int = 1, **kwargs):
    return (await basic_request(
            loop=loop, api_key=api_key, endpoint="{0}/leaderboard/stat".format(
                    api_version), *args,
            params={"type": stat_type}, **kwargs))[1]


@_add_request_parameters
async def get_player(unique_id: str, platform_id: int, *args, api_key: str, loop: asyncio.AbstractEventLoop,
                     api_version: int = 1, **kwargs):
    return (await basic_request(
            loop=loop, api_key=api_key, endpoint="{0}/player".format(api_version), *args,
            params={"unique_id": url_parser.quote_plus(unique_id, encoding="utf-8"), "platform_id": platform_id},
            **kwargs))[1]


@_add_request_parameters
async def get_player_batch(unique_id_platform_pairs: tuple, *args, api_key: str, loop: asyncio.AbstractEventLoop,
                           api_version: int = 1, **kwargs):
    # The json we send needs to be in the form [{"uniqueId": str}, {"platformId": str}, ...]
    unique_id_platform_pairs = [{"uniqueId": entry[0], "platformId": str(entry[1])} for entry in
                                unique_id_platform_pairs]

    return (await basic_request(
            loop=loop, api_key=api_key, endpoint="{0}/player/batch".format(api_version),
            *args, method="post", json=unique_id_platform_pairs,
            headers={"Accept": "application/json", "Content-Type": "application/json"}, **kwargs))[1]


@_add_request_parameters
async def search_players(display_name: str, page: int, *args, api_key: str, loop: asyncio.AbstractEventLoop,
                         api_version: int = 1,
                         **kwargs):
    return (await basic_request(
            loop=loop, api_key=api_key, endpoint="{0}/search/players".format(api_version), *args,
            params={"display_name": url_parser.quote_plus(display_name, encoding="utf-8"),
                    "page": page}, **kwargs))[1]
