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

# Just some constants that are used
STEAM = "Steam" # Steam platform as a string
PS4 = "PS4" # Playstation 4 platform as a string
XBOX1 = "XboxOne" # Xbox One platform as a string

ALL_PLATFORMS = {STEAM, PS4, XBOX1} # A set of all the platforms, useful for membership tests

STEAM_ID = 1 # Platform id for the Steam platform
PS4_ID = 2 # Platform id for the Playstation 4 platform
XBOX1_ID = 3 # Platform id for the Xbox One platform

ALL_IDS = {STEAM_ID, PS4_ID, XBOX1_ID} # A set of all the platform IDs, useful for membership tests
ID_PLATFORM_LUT = {STEAM_ID: STEAM, PS4_ID: PS4, XBOX1_ID: XBOX1} # A dict with platform IDs as keys as platform strings as values
PLATFORM_ID_LUT = {STEAM: STEAM_ID, PS4: PS4_ID, XBOX1: XBOX1_ID} # A dict with platform strings as keys and platform IDs as values

LEADERBOARD_WINS = "wins" # The stat leaderboard type to filter by number of wins
LEADERBOARD_GOALS = "goals" # The stat leaderboard type to filter by number of goals
LEADERBOARD_MVPS = "mvps" # The stat leaderboard type to filter by number of MVPs
LEADERBOARD_SAVES = "saves" # The stat leaderboard type to filter by number of saves
LEADERBOARD_SHOTS = "shots" # The stat leaderboard type to filter by number of shots
LEADERBOARD_ASSISTS = "assists" # The stat leaderboard type to filter by number of assists

LEADERBOARD_TYPES = {LEADERBOARD_WINS, LEADERBOARD_GOALS, LEADERBOARD_MVPS,
                     LEADERBOARD_SAVES, LEADERBOARD_SHOTS, LEADERBOARD_ASSISTS} # A set of all the types of leaderboards, useful for looping over.

RANKED_DUEL_ID = 10 # The ID of the ranked duels playlist
RANKED_DOUBLES_ID = 11 # The ID of the ranked doubles playlist
RANKED_SOLO_STANDARD_ID = 12 # The ID of the ranked solo standard playlist
RANKED_STANDARD_ID = 13 # The ID of the ranked standard playlist

RANKED_PLAYLISTS_IDS = {RANKED_DUEL_ID, RANKED_DOUBLES_ID, RANKED_SOLO_STANDARD_ID, RANKED_STANDARD_ID} # A set of all the ranked playlist IDs, useful for looping or membership tests
