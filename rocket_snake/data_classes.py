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
    Fields:
        id: int; The id for this playlist. Unique for each gamemode, not for each platform.
        name: str; "Gamemode", such as "Ranked Duels" or "Hoops".
        platform: int; The platform this playlist is on.
            Corresponds to the platforms in the module constants.
        population: int; The number of people currently (see last_updated) playing this playlist.
            Note that this only count people on this playlist's platform.
        last_updated: int; A timestamp (seconds since unix epoch, see output of time.time()) of when the population field was updated.
    """
    pass


class Player(object):
    """
    Represents a player. Some ways of getting player object might not populate all fields. If a field isn't populated, it will be None.
    """

    def __init__(self, uid: str, display_name: str, platform: str, avatar_url: str = None, profile_url: str = None,
                 signature_url: str = None,
                 stats: dict = None, ranked_seasons: dict = None):
        # Our parameters
        self.uid = uid
        self.display_name = display_name
        self.platform = platform
        self.platform_id = constants.PLATFORM_ID_LUT.get(platform, None)
        self.avatar_url = avatar_url
        self.profile_url = profile_url
        self.signature_url = signature_url
        self.stats = stats

        # The way ranked_seasons is structured by default is kind of janky since json doesn't support integer keys
        # We convert all the seasonId and playlistId keys of ranked_seasons into real ints
        processed_ranked_seasons = {int(season_id):
                                        {int(playlist_id): playlist_data for playlist_id, playlist_data in
                                         season_data.items()}
                                    for season_id, season_data in ranked_seasons.items()}
        self.ranked_seasons = processed_ranked_seasons

    def __str__(self):
        return ("Player \'{0}\' with unique id {1}:\n\t"
                "Platform: {2}, id {3}\n\t"
                "Avatar url: {4}\n\t"
                "Profile url: {5}\n\t"
                "Signature url: {6}\n\t"
                "Stats: {7}".format(self.display_name, self.uid, self.platform, self.platform_id, self.avatar_url,
                                    self.profile_url, self.signature_url, self.stats))
