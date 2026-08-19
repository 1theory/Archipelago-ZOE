"""This module provides handling of location objects"""

from typing import TYPE_CHECKING

from worlds.zoe.constants.data.location import ZOE_LOCATION_DATA_TABLE
from worlds.zoe.constants.locations.tags import ZOETAG
from worlds.zoe.constants.region import ZOEREGION

if TYPE_CHECKING:
    from worlds.zoe.world import ZoeWorld


def get_total_locations(world: "ZoeWorld") -> int:
    """Returns the total number of locations in the apworld"""
    locations = [loc for loc in world.multiworld.get_locations() if loc.player == world.player]
    return len(locations)


def get_location_names() -> dict[str, int]:
    """Returns a dictionary mapping location names to their apcodes"""
    return {name: data.AP_CODE for name, data in ZOE_LOCATION_DATA_TABLE.items()}


def get_from_tag(tag) -> set[str]:
    """Return a set of location names that match the given tag"""
    return {loc for loc in ZOE_LOCATION_DATA_TABLE.keys() if tag in ZOE_LOCATION_DATA_TABLE[loc].TAGS}