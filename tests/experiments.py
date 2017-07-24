import asyncio
import json
import time
import unittest
from pprint import pprint

import rocket_snake

with open("tests/config.json", "r") as config_file:
    config = json.load(config_file)

def async_test(f):
    def wrapper(*args, **kwargs):
        future = f(*args, **kwargs)
        loop = args[0].running_loop
        loop.run_until_complete(future)
    return wrapper

class AsyncTester(unittest.TestCase):
    """Test async code easily by inheriting from this."""

    @staticmethod
    def _do_async_code(coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def setUp(self, *args, **kwargs):
        super().setUp()

        self.running_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.running_loop)

        self.time_track_stack = []


    def tearDown(self, *args, **kwargs):
        super().setUp()

        if not self.running_loop.is_closed():
            self.running_loop.close()

    def time_track(self, text: object="Time taken was {0} seconds."):

        if text is None:
            self.time_track_stack.append(time.time())
        else:
            last_time = self.time_track_stack.pop()
            time_delta = time.time() - last_time
            print(text.format(round(time_delta, 3)))
            return time_delta


class Tester(AsyncTester):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.executed_requests = 0

    async def do_multiple(self, func, times: int = 10, text: str = "Time taken was {0} seconds."):
        self.time_track(None)

        tasks = [func() for i in range(times)]

        tasks = await asyncio.gather(*tasks, loop=asyncio.get_event_loop(), return_exceptions=False)

        gather_time = self.time_track("Time taken for {0} gather tasks was ".format(times) + "{0} seconds.")

        print("That means an average of {0} milliseconds per gather request.".format(
            round(1000 * (gather_time / times), 1)))

        total_series_time = 0

        for i in range(times):
            self.time_track(None)

            await func()

            total_series_time += self.time_track(text)

        print("Time taken for {0} series tasks was {1} seconds.".format(times, round(total_series_time, 3)))
        print("That means an average of {0} milliseconds per series request.".format(
            round(1000 * (total_series_time / times), 1)))

        return times * 2

    @async_test
    async def test_data_endpoints(self):
        self.time_track(None)
        print("Testing data endpoints.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        print("Playlists:")
        pprint(await client.get_playlists())
        print("\nSeasons:")
        pprint(await client.get_seasons())
        print("\nPlatforms:")
        pprint(await client.get_platforms())
        print("\nTiers:")
        pprint(await client.get_tiers())

        print("\n")
        self.executed_requests += 7

        print("Done with testing data endpoints. Time taken was {0} seconds.".format(self.time_track("Time taken for data endpoints was {0} seconds.")))

    @async_test
    async def test_player_search(self):
        self.time_track(None)
        print("Testing player search.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        pprint(await client.search_player("Mike", get_all=False))

        print("Done with testing player search. Time taken was {0} seconds.".format(self.time_track("Time taken for player search was {0} seconds.")))

    @async_test
    async def test_player_endpoints(self):
        self.time_track(None)
        print("Testing player endpoints.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        pprint(await client.search_player("Mike", get_all=False))

        print("Me:")
        self.time_track(None)
        print(str(await client.get_player(config["steam_ids"][0], rocket_snake.constants.STEAM)))
        self.time_track("Time taken for single player was {0} seconds.")
        print("Loads a people:")
        self.time_track(None)
        pprint(await client.get_players(
            list(zip(config["steam_ids"], [rocket_snake.constants.STEAM] * len(config["steam_ids"])))))
        self.time_track("Time taken for batch players was {0} seconds.")

        print("Done with testing player endpoints. Time taken was {0} seconds.§".format(self.time_track("Time taken for player endpoints was {0} seconds.")))

    @async_test
    async def test_platforms_throughput(self):
        self.time_track(None)
        print("Testing platforms data throughput.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        done_requests = await self.do_multiple(client.get_platforms, text="Platforms took {0} seconds.")

        print("Done with platforms data throughput testing, {0} requests were executed. \nThat means an average of {1} milliseconds per request."
                .format(done_requests, round(1000 * (self.time_track("Time taken for platforms data throughput was {0} seconds.") / done_requests), 1)))

    @async_test
    async def test_tiers_throughput(self):
        self.time_track(None)
        print("Testing tiers data throughput.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        done_requests = await self.do_multiple(client.get_tiers, text="tiers took {0} seconds.")

        print("Done with tiers data throughput testing, {0} requests were executed. \nThat means an average of {1} milliseconds per request."
                .format(done_requests, round(1000 * (self.time_track("Time taken for tiers data throughput was {0} seconds.") / done_requests), 1)))

    @async_test
    async def test_seasons_throughput(self):
        self.time_track(None)
        print("Testing seasons data throughput.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        done_requests = await self.do_multiple(client.get_seasons, text="seasons took {0} seconds.")

        print("Done with seasons data throughput testing, {0} requests were executed. \nThat means an average of {1} milliseconds per request."
                .format(done_requests, round(1000 * (self.time_track("Time taken for seasons data throughput was {0} seconds.") / done_requests), 1)))

    @async_test
    async def test_playlists_throughput(self):
        self.time_track(None)
        print("Testing playlists data throughput.")

        client = rocket_snake.RLS_Client(api_key=config["key"], auto_rate_limit=True)

        done_requests = await self.do_multiple(client.get_playlists, text="playlists took {0} seconds.")

        print("Done with playlists data throughput testing, {0} requests were executed. \nThat means an average of {1} milliseconds per request."
                .format(done_requests, round(1000 * (self.time_track("Time taken for playlists data throughput was {0} seconds.") / done_requests), 1)))
