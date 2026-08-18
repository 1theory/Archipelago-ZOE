"""This module provides a list of Excluded locations for the Zoe apworld"""

from Options import ExcludeLocations
from worlds.zoe.constants.locations.tags import ZOETAG


class ZOEExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important item."""
    default = frozenset({ZOETAG.UNSTABLE})