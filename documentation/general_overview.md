# Overview of Rocket Snake

## What can I use it for?
|What to import|What it does|
|---|---|
|`rocket_snakes`|It's the library itself.|
|`rocket_snakes.RLS_Client`|It's the client class that you instantiate to use the api.|
|`rocket_snakes.RLS_Constants`|Some constants, like `STEAM` and `ALL_PLATFORMS`. Might be useful.|

## What can't I use it for?
idk, check the code.


# How do?
```python
import asyncio
import rocket_snakes as rs

from pprint import pprint


async def example_function():
    
    client = rs.RLS_Client("API KEY GOES HERE")    
    
    print("\nPlaylists:")
    pprint(await client.get_playlists())
    print("\nSeasons:")
    pprint(await client.get_seasons())
    print("\nPlatforms:")
    pprint(await client.get_platforms())
    print("\nTiers:")
    pprint(await client.get_tiers())


print("Creating and starting an asyncio event loop...")

my_loop = asyncio.get_event_loop()
my_loop.run_until_complete(example_function())

print("The event loop has now exited after executing the example.")

```