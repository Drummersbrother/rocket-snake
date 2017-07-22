import asyncio
import json
import time
import unittest
from pprint import pprint

import rocket_snake

_time_track_stack = []

_total_reqs = 0


def time_track(text: str = "Time taken: {0} seconds"):
    global _time_track_stack

    if text is None:
        _time_track_stack.append(time.time())
    else:
        last_time = _time_track_stack.pop()
        time_delta = time.time() - last_time
        print(text.format(round(time_delta, 3)))
        return time_delta


async def tester(config: dict):
    print("Doing async tests.")

    my_loop = asyncio.get_event_loop()

    client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

    pprint(await client.search_player("Mike", get_all=False))

    print("\nMe:")
    time_track(None)
    print(str(await client.get_player(config["steam_ids"][0], rocket_snake.STEAM)))
    time_track("Time taken for single player was {0} seconds.")
    print("Loads a people:")
    time_track(None)
    pprint(await client.get_players(list(zip(config["steam_ids"], [rocket_snake.STEAM] * len(config["steam_ids"])))))
    time_track("Time taken for batch players was {0} seconds.")
    print("\nPlaylists:")
    pprint(await client.get_playlists())
    print("\nSeasons:")
    pprint(await client.get_seasons())
    print("\nPlatforms:")
    pprint(await client.get_platforms())
    print("\nTiers:")
    pprint(await client.get_tiers())

    print("\n")
    global _total_reqs
    _total_reqs += 7

    # Testing doing many things

    async def do_multiple(func, times: int = 10, text: str = "Time taken was {0} seconds."):
        time_track(None)

        tasks = [func() for i in range(times)]

        tasks = await asyncio.gather(*tasks, loop=my_loop, return_exceptions=False)

        gather_time = time_track("Time taken for {0} gather tasks was ".format(times) + "{0} seconds.")

        print("That means an average of {0} milliseconds per gather request.".format(
            round(1000 * (gather_time / times), 1)))

        total_series_time = 0

        for i in range(times):
            time_track(None)

            await func()

            total_series_time += time_track(text)

        print("Time taken for {0} series tasks was {1} seconds.".format(times, round(total_series_time, 3)))
        print("That means an average of {0} milliseconds per series request.".format(
            round(1000 * (total_series_time / times), 1)))

        global _total_reqs
        _total_reqs += times * 2

    bigtasks = [do_multiple(client.get_platforms, text="Platforms took {0} seconds."),
                do_multiple(client.get_playlists, text="Playlists took {0} seconds."),
                do_multiple(client.get_seasons, text="Seasons took {0} seconds."),
                do_multiple(client.get_tiers, text="Tiers took {0} seconds.")
                ]

    bigtasks = await asyncio.gather(*bigtasks, loop=my_loop, return_exceptions=False)




class Tester(unittest.TestCase):

    def test_all(self):
        time_track(None)
        print("Outside async. Starting...")

        with open("tests/config.json", "r") as config_file:
            config = json.load(config_file)

        my_loop = asyncio.get_event_loop()

        my_loop.run_until_complete(tester(config))

        print(
            "Done with experiments, {0} requests were executed. \nThat means an average of {1} milliseconds per request."
                .format(_total_reqs,
                        round(1000 * (time_track("Time taken for all experiments was {0} seconds.") / _total_reqs), 1)))
