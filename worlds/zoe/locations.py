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

all_tags: list[str] = [
    ZOETAG.ENEMY,
    ZOETAG.ENEMYCOUNT,
    ZOETAG.MISSIONS,
    ZOETAG.HARD_ENEMY,
    ZOETAG.LOCAL_SERVERS,
    ZOETAG.PASSCODES,
    ZOETAG.VR,
    ZOETAG.VISIT,
    ZOETAG.SQUADS_ENGAGED,
    ZOETAG.UNSTABLE,
    ZOETAG.WEAPONS,
    ZOETAG.LEVEL,
]

location_groups: dict[str, set[str]] = {
    ZOEREGION.HANGAR_1: get_from_tag(ZOEREGION.HANGAR_1),
    ZOEREGION.FACTORY_1: get_from_tag(ZOEREGION.FACTORY_1),
    ZOEREGION.TOWN_1_TEMPEST: get_from_tag(ZOEREGION.TOWN_1_TEMPEST),
    ZOEREGION.TOWN_1: get_from_tag(ZOEREGION.TOWN_1),
    ZOETAG.ENEMY: get_from_tag(ZOETAG.ENEMY),
    ZOETAG.ENEMYCOUNT: get_from_tag(ZOETAG.ENEMYCOUNT),
    ZOETAG.SQUADS_ENGAGED: get_from_tag(ZOETAG.SQUADS_ENGAGED),
    ZOETAG.MISSIONS: get_from_tag(ZOETAG.MISSIONS),
    ZOETAG.HARD_ENEMY: get_from_tag(ZOETAG.HARD_ENEMY),
    ZOETAG.LOCAL_SERVERS: get_from_tag(ZOETAG.LOCAL_SERVERS),
    ZOETAG.PASSCODES: get_from_tag(ZOETAG.PASSCODES),
    ZOETAG.VR: get_from_tag(ZOETAG.VR),
    ZOETAG.VISIT: get_from_tag(ZOETAG.VISIT),
    ZOETAG.UNSTABLE: get_from_tag(ZOETAG.UNSTABLE),
    ZOETAG.WEAPONS: get_from_tag(ZOETAG.WEAPONS),
    ZOETAG.LEVEL: get_from_tag(ZOETAG.LEVEL)
    }

def get_level_locations(region: str) -> set[str]:
    """Returns a set of location names for a given region"""
    return set(level[0] for level in get_level_location_data(region))


def get_level_location_data(region: str) -> filter:
    """Returns the location data table filtered to a specific region"""
    return filter(lambda level: level[1].REGION == region, ZOE_LOCATION_DATA_TABLE.items())
