import asyncio

from . import basic_requests, custom_exceptions
from .constants import *


class RLS_Client(object):
    """Represents the client, does everything. Initialize with api key and some other settings if you want to."""

    def __init__(self, api_key: str = None, auto_rate_limit: bool = False,
                 event_loop: asyncio.AbstractEventLoop = None, _api_version: int = 1):
        """Create a client, does not execute any requests.
        Parameters:
            api_key: str; The key for the https://rocketleaguestats.com api. If not supplied, an InvalidArgumentException will be thrown.
            auto_rate_limit: bool; If the api should automatically delay execution of request to satisy the default ratelimiting. Default False. Set to True to enable rate-limiting.
            event_loop: asyncio.AbstractEventloop; the asyncio event loop that should be used. If not supplied, the default one returned by asyncio.get_event_loop() is used.
            _api_version: int; What version endpoint to use. Do not change if you don't know what you're doing. Default is 1.
            """

        if api_key is None:
            raise custom_exceptions.NoAPIKeyException("No api key was supplied to client initialization.")
        else:
            self._api_key = api_key

        self.auto_ratelimit = auto_rate_limit

        if event_loop is None:
            self._event_loop = asyncio.get_event_loop()
        else:
            self._event_loop = event_loop

        self._api_version = _api_version

    async def get_platforms(self):
        """Returns the supported platforms for the api."""

        raw_season_data = await basic_requests.get_platforms(api_key=self._api_key, api_version=self._api_version,
                                                             loop=self._event_loop,
                                                             handle_ratelimiting=self.auto_ratelimit)

        return [ID_PLATFORM_LUT.get(plat_id, None) for plat_id in [entry["id"] for entry in raw_season_data] if
                ID_PLATFORM_LUT.get(plat_id, None) is not None]
