import asyncio

from . import basic_requests, custom_exceptions, data_classes
from .constants import *


class RLS_Client(object):
    """Represents the client, does everything. Initialize with api key and some other settings if you want to."""

    def __init__(self, api_key: str = None, auto_rate_limit: bool = True,
                 event_loop: asyncio.AbstractEventLoop = None, _api_version: int = 1):
        """
        Creates a client, does not execute any requests.
        :param api_key: The key for the https://rocketleaguestats.com api.
                    If not supplied, an InvalidArgumentException will be thrown.
        :param auto_rate_limit: If the api should automatically delay execution of request to satisy the default ratelimiting.
                    Default False. Set to True to enable rate-limiting.
        :param event_loop: The asyncio event loop that should be used.
                    If not supplied, the default one returned by asyncio.get_event_loop() is used.
        :param_api_version: What version endpoint to use.
                    Do not change if you don't know what you're doing. Default is 1.
        """

        if api_key is None:
            raise custom_exceptions.NoAPIKeyError("No api key was supplied to client initialization.")
        else:
            self._api_key = api_key

        self.auto_ratelimit = auto_rate_limit

        if event_loop is None:
            self._event_loop = asyncio.get_event_loop()
        else:
            self._event_loop = event_loop

        self._api_version = _api_version

    async def get_platforms(self):
        """
        :return the supported platforms for the api.
        """

        raw_playlist_data = await basic_requests.get_platforms(api_key=self._api_key, api_version=self._api_version,
                                                               loop=self._event_loop,
                                                               handle_ratelimiting=self.auto_ratelimit)

        return [ID_PLATFORM_LUT.get(plat_id, None) for plat_id in [entry["id"] for entry in raw_playlist_data] if
                ID_PLATFORM_LUT.get(plat_id, None) is not None]

    async def get_playlists(self):
        """
        :return a list of data_classes.Playlists.
        """
        raw_playlist_data = await basic_requests.get_playlists(api_key=self._api_key, api_version=self._api_version,
                                                               loop=self._event_loop,
                                                               handle_ratelimiting=self.auto_ratelimit)

        playlists = []

        for raw_playlist in raw_playlist_data:
            playlists.append(data_classes.Playlist(
                    raw_playlist["id"], raw_playlist["name"], ID_PLATFORM_LUT[raw_playlist["platformId"]],
                    raw_playlist["population"]["players"], raw_playlist["population"]["updatedAt"]
            ))

        return playlists

    async def get_seasons(self):
        """
        :return a list of data_classes.Seasons.
        """
        raw_seasons_data = await basic_requests.get_seasons(api_key=self._api_key, api_version=self._api_version,
                                                            loop=self._event_loop,
                                                            handle_ratelimiting=self.auto_ratelimit)

        seasons = []

        for raw_season in raw_seasons_data:
            seasons.append(data_classes.Season(
                    raw_season["seasonId"], raw_season["endedOn"] is None, raw_season["startedOn"],
                    raw_season["endedOn"]
            ))

        return seasons

    async def get_tiers(self):
        """
        :return a list of data_classes.Tiers.
        """
        raw_tiers_data = await basic_requests.get_tiers(api_key=self._api_key, api_version=self._api_version,
                                                        loop=self._event_loop,
                                                        handle_ratelimiting=self.auto_ratelimit)

        tiers = []

        for raw_tier in raw_tiers_data:
            tiers.append(data_classes.Tier(raw_tier["tierId"], raw_tier["tierName"]))

        return tiers

    async def get_player(self, unique_id: str, platform: str):
        """
        :param unique_id: The string to search for. Depending on the platform parameter,
                this can represent Xbox Gamertag, Xbox user ID, steam 64 ID, or PSN username.
        :param platform: The platform to search on. This should be one of the platforms defined in rocket_snake/constants.py.
        :return A data_classes.Player object. If the player couldn't be found, this raises custom_exceptions.APINotFoundError.
        """

        # If the player couldn't be found, the server returns a 404

        raw_player_data = await basic_requests.get_player(unique_id, PLATFORM_ID_LUT[platform],
                                                          api_key=self._api_key, api_version=self._api_version,
                                                          loop=self._event_loop,
                                                          handle_ratelimiting=self.auto_ratelimit)

        # We have some valid player data
        player = data_classes.Player(raw_player_data["uniqueId"], raw_player_data["displayName"], platform,
                                     avatar_url=raw_player_data["avatar"], profile_url=raw_player_data["profileUrl"],
                                     signature_url=raw_player_data["signatureUrl"], stats=raw_player_data["stats"],
                                     ranked_seasons=raw_player_data["rankedSeasons"])

        return player

    async def get_players(self, unique_id_platform_pairs: list):
        """
        :param unique_id_platform_pairs: A list of pairs of unique ids and platforms, that is:
                [(unique_id1, platform1), (unique_id2, platform2), ...]
        :return A list of data_classes.Player objects.
                 If a player could not be found, the corresponding index in the returned list will be None.
        """

        # We can only request 10 or less players at a time
        if not (10 >= len(unique_id_platform_pairs) >= 1):
            raise ValueError("The list of unique ids and platforms was not between 1 and 10 inclusive. Length was: {0}"
                             .format(len(unique_id_platform_pairs)))

        # We convert the platforms to platform ids
        unique_id_platform_pairs = [(entry[0], PLATFORM_ID_LUT[entry[1]]) for entry in unique_id_platform_pairs]

        # If no player could be found, the server returns a 404
        raw_players_data = await basic_requests.get_player_batch(tuple(unique_id_platform_pairs),
                                                                 api_key=self._api_key, api_version=self._api_version,
                                                                 loop=self._event_loop,
                                                                 handle_ratelimiting=self.auto_ratelimit)

        players = {
        raw_player_data["uniqueId"]: data_classes.Player(raw_player_data["uniqueId"], raw_player_data["displayName"],
                                                         ID_PLATFORM_LUT[req_pair[1]],
                                                         avatar_url=raw_player_data["avatar"],
                                                         profile_url=raw_player_data["profileUrl"],
                                                         signature_url=raw_player_data["signatureUrl"],
                                                         stats=raw_player_data["stats"],
                                                         ranked_seasons=raw_player_data["rankedSeasons"]) for
        raw_player_data, req_pair in
        list(zip(raw_players_data, unique_id_platform_pairs))}

        ordered_players = []

        for unique_id, platform in unique_id_platform_pairs:
            ordered_players.append(players.get(unique_id, None))

        return ordered_players

    # TODO
    async def get_ranked_leaderboard(self, playlist):
        """
        :param playlist: What playlist you want leaderboards for. 
                    Has to be a valid playlist id or data_classes.Playlist object.
        :return The raw leaderboard data.
        """
        return await basic_requests.get_ranked_leaderboard(playlist if isinstance(playlist, int) else playlist.id,
                                                           api_key=self._api_key, api_version=self._api_version,
                                                           loop=self._event_loop,
                                                           handle_ratelimiting=self.auto_ratelimit)
