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

"""
These are all the pure data classes that are used by the api client.
In general, these should not be instantiated, but created by the api client itself.
"""

from collections import namedtuple

from . import constants


class Tier(namedtuple("Tier", ("id", "name"))):
    """
    Represents a tier. Unless otherwise specified, this will be created with data from the last season.
    Fields:
        id: int; The id for this Tier.
        name: str; The name of this Tier.
    """
    pass


class Season(namedtuple("Season", ("id", "is_current", "time_started", "time_ended"))):
    """
    Represents a season. Each season is time-bounded, and if a season hasn't ended yet, the time_ended field will be None
    Fields:
        id: int; The id for this season. Unique for each season.
        is_current: bool; True if the season is currently active (hasn't ended). False otherwise.
        time_started: int; A timestamp of when the season started (seconds since unix epoch, see output of time.time()).
        time_ended: int; A timestamp of when the season ended (see time_started).
            If the season hasn't ended (is_current is True), this field is None.
    """
    pass


class Playlist(namedtuple("Playlist", ("id", "name", "platform", "population", "last_updated"))):
    """
    Represents a playlist. There is a playlist for each unique combination of platform and gamemode.
    :var id: The id for this playlist. Unique for each gamemode, not for each platform.
    :var name: "Gamemode", such as "Ranked Duels" or "Hoops".
    :var platform: The platform this playlist is on.
            Corresponds to the platforms in the module constants.
    :var population: The number of people currently (see last_updated) playing this playlist.
            Note that this only count people on this playlist's platform.
    :var last_updated: A timestamp (seconds since unix epoch, see output of time.time()) of when the population field was updated.
    """
    pass


class SeasonPlaylistRank(namedtuple("SeasonPlaylistRank", ("rankPoints", "division", "matchesPlayed", "tier"))):
    pass


class RankedSeason(dict):
    """Represents a single ranked season for a single user."""

    def __getitem__(self, item):
        if isinstance(item, Playlist):
            return self[item.id]
        else:
            return self[item]

    def __str__(self):
        return "".join(["\n\tRanked season on playlist {0}: {1}".format(playlist_id, str(rank)) for playlist_id, rank in
                        self.items()])


class RankedSeasons(object):
    """
    Represents the ranked data of a user. These can be subscripted by season id or Season object to get data for a 
    specific season (a RankedSeason object). This object defines some method to be more similar to a dictionary.
    Do not create these yourself.
    :var data: The raw dict to convert into this object.
    """

    def __init__(self, data: dict):

        self.ranked_seasons = {}

        for season_id, ranked_data in data.items():
            self.ranked_seasons[season_id] = RankedSeason({key: SeasonPlaylistRank(val.get("rankPoints", None),
                                                                                   val.get("division", None),
                                                                                   val.get("matchesPlayed", None),
                                                                                   val.get("tier", None)) for key, val
                                                           in ranked_data.items()})

    def __getitem__(self, item):
        if isinstance(item, Season):
            return self.ranked_seasons[item.id]
        else:
            return self.ranked_seasons[item]

    def __contains__(self, item):
        if isinstance(item, Season):
            return item.id in self.ranked_seasons
        else:
            return item in self.ranked_seasons

    def __len__(self):
        return len(self.ranked_seasons)

    def __iter__(self):
        return iter(self.ranked_seasons)

    def __getattr__(self, item):
        regular_functions = {
            "__init__": self.__init__,
            "__getitem__": self.__getitem__,
            "__contains__": self.__contains__,
            "__len__": self.__len__,
            "__iter__": self.__iter__,
        }
        return regular_functions.get(item, getattr(self.ranked_seasons, item))

    def __str__(self):
        return "\n".join(["Season {0}: {1}".format(season_id, str(ranked_season)) for season_id, ranked_season in
                          self.ranked_seasons.items()])


class Player(object):
    """
    Represents a player. Some ways of getting player object might not populate all fields. If a field isn't populated, it will be None.
    """

    def __init__(self, uid: str, display_name: str, platform: str, avatar_url: str = None, profile_url: str = None,
                 signature_url: str = None,
                 stats: dict = None, ranked_seasons: RankedSeasons = None):
        # Our parameters
        self.uid = uid
        self.display_name = display_name
        self.platform = platform
        self.platform_id = constants.PLATFORM_ID_LUT.get(platform, None)
        self.avatar_url = avatar_url
        self.profile_url = profile_url
        self.signature_url = signature_url
        self.stats = stats
        self.ranked_seasons = ranked_seasons

    def __str__(self):
        return ("Rocket League player \'{0}\' with unique id {1}:\n\t"
                "Platform: {2}, id {3}\n\t"
                "Avatar url: {4}\n\t"
                "Profile url: {5}\n\t"
                "Signature url: {6}\n\t"
                "Stats: {7}\n\t"
                "Ranked data: \n\t{8}".format(self.display_name, self.uid, self.platform, self.platform_id,
                                              self.avatar_url,
                                              self.profile_url, self.signature_url, self.stats,
                                              "\n\t".join(str(self.ranked_seasons).split("\n"))))

    def __repr__(self):
        return str(self)
