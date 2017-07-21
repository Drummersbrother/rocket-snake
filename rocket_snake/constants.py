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
STEAM = "Steam"
PS4 = "PS4"
XBOX1 = "XboxOne"

ALL_PLATFORMS = {STEAM, PS4, XBOX1}

STEAM_ID = 1
PS4_ID = 2
XBOX1_ID = 3

ALL_IDS = {STEAM_ID, PS4_ID, XBOX1_ID}
ID_PLATFORM_LUT = {STEAM_ID: STEAM, PS4_ID: PS4, XBOX1_ID: XBOX1}
PLATFORM_ID_LUT = {STEAM: STEAM_ID, PS4: PS4_ID, XBOX1: XBOX1_ID}

LEADERBOARD_WINS = "wins"
LEADERBOARD_GOALS = "goals"
LEADERBOARD_MVPS = "mvps"
LEADERBOARD_SAVES = "saves"
LEADERBOARD_SHOTS = "shots"
LEADERBOARD_ASSISTS = "assists"

LEADERBOARD_TYPES = {LEADERBOARD_WINS, LEADERBOARD_GOALS, LEADERBOARD_MVPS,
                     LEADERBOARD_SAVES, LEADERBOARD_SHOTS, LEADERBOARD_ASSISTS}

RANKED_DUEL_ID = 10
RANKED_DOUBLES_ID = 11
RANKED_SOLO_STANDARD_ID = 12
RANKED_STANDARD_ID = 13

RANKED_PLAYLISTS_IDS = {RANKED_DUEL_ID, RANKED_DOUBLES_ID, RANKED_SOLO_STANDARD_ID, RANKED_STANDARD_ID}