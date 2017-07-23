.. currentmodule:: rocket_snake

API Reference
*************

The following section outlines the API of Rocket Snake.

The Client
==========

.. autoclass:: RLS_Client
    :members:

The Exceptions
==============

This module (``rocket_snake.exceptions``) defines the exceptions that are specific to Rocket Snake.
All of them are subclasses of some ``builtins`` exception, but not all of them are direct subclasses.

.. class:: exceptions.NoAPIKeyError
A subclass of :class:`ValueError`, and is raised when an API key isn't provided to the :class:`RLS_Client`.

.. class:: exceptions.APIServerError
A subclass of :class:`ConnectionError`, and is raised when the client gets an error when trying to request something
from the API server.

.. class:: exceptions.APINotFoundError
A subclass of :class:`ConnectionError`, and is raised when the API server can't find what was requested
(e.g. if a player with the requested displayname doesn't exists)

.. class:: exceptions.APIBadResponseCodeError
A subclass of :class:`ConnectionError`, and is raised when the API returns a response code that isn't successfull,
but can't be identified as a more specific error.

.. class:: exceptions.RatelimitError
A subclass of :class:`APIBadResponseCodeError`, and is raised when the :class:`RLS_Client` gets ratelimited by the API
server but didn't handle ratelimiting at all or not properly.

.. class:: exceptions.InvalidAPIKeyError
A subclass of :class:`APIBadResponseCodeError`, and is raised when the :class:`RLS_Client` has been initialised with
an invalid API key and tries to execute a request to the API server.


The Constants
=============

.. module:: rocket_snake.constants

This module (``rocket_snake.constants``) defines constants that are used when requesting information from the API.

.. note:: The value of these should not be hardcoded in your code, since these might change at any time.

These constants are all uppercase.
Here is the rundown:

=================== ========================================================================================================
Platform related constants
----------------------------------------------------------------------------------------------------------------------------
Name                Description
=================== ========================================================================================================
``STEAM``           This is the string that represents Steam as a platform.
``PS4``             ^ But for Playstation 4.
``XBOX1``           ^ But for Xbox One.
``ALL_PLATFORMS``   A :class:`set` of the previous platform strings.
``STEAM_ID``        This is the ID of the steam platform string.
``PS4_ID``          ^ But for Playstation 4.
``XBOX1_ID``        ^ But for Xbox One.
``ALL_IDS``         A :class:`set` of the previous platform IDs.
``ID_PLATFORM_LUT`` A :class:`dict` with the members of ``ALL_IDS`` as keys and the members of ``ALL_PLATFORMS`` as values.
``PLATFORM_ID_LUT`` The inverse of ``ID_PLATFORM_LUT``, that is, platforms as keys and IDs as values.
=================== ========================================================================================================

======================= ===================================================================================
Leaderboard related constants
-----------------------------------------------------------------------------------------------------------
Name                    Description
======================= ===================================================================================
``LEADERBOARD_WINS``    This is the string that represents a leaderboard based/filtered on number of wins.
``LEADERBOARD_GOALS``   ^ But for number of goals.
``LEADERBOARD_MVPS``    ^ But for number of MVPs.
``LEADERBOARD_SAVES``   ^ But for number of saves.
``LEADERBOARD_SHOTS``   ^ But for number of shots.
``LEADERBOARD_ASSISTS`` ^ But for number of assists
``LEADERBOARD_TYPES``   A :class:`set` of all the previous leaderboard filter types.
======================= ===================================================================================

=========================== =====================================================
Platform related constants
---------------------------------------------------------------------------------
Name                        Description
=========================== =====================================================
``RANKED_DUEL_ID``          This is the ID of the ranked duels playlist.
``RANKED_DOUBLES_ID``       ^ But for the ranked doubles playlist.
``RANKED_SOLO_STANDARD_ID`` ^ But for the ranked solo standard playlist.
``RANKED_STANDARD_ID``      ^ But for the ranked standard playlist.
``RANKED_PLAYLISTS_IDS``    A :class:`set` of all the previous playlist IDs.
=========================== =====================================================
