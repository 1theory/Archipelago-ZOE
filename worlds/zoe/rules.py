"""This module contains the logic implementation for zoe"""
from collections.abc import Callable
from logging import DEBUG, getLogger
import math
from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule
from worlds.zoe.constants.data.item import area_data, weapon_data
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.locations.enemy_count import ZOEENEMYCOUNT
from worlds.zoe.constants.locations.tags import ZOETAG
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.region import ZOEREGION
from worlds.zoe.locations import location_groups

if TYPE_CHECKING:
    from worlds.zoe.world import ZoeWorld

zoe_logger = getLogger(ZOEOPTION.GAME_TITLE_FULL)
zoe_logger.setLevel(DEBUG)

def all_locations(state: CollectionState, world: "ZoeWorld", tag: str, skip: str):
    """check if all locations with this tag can be reached"""
    check: bool = True
    for loc in world.get_locations():
        if loc.name in location_groups[tag] and loc.name != skip:
            check &= state.can_reach_location(loc.name, world.player)
    return check

# Todo: Rule Builder
def set_rules(world: "ZoeWorld"):
    """Apply logic rules to each location"""

    region_rules_dict: dict[str, Callable] = {

        # Intro Hangar.1
        f"{ZOEREGION.HANGAR_1} -> {ZOEREGION.FACTORY_1}":
            lambda state: state.has(ZOEITEM.FACTORY_1, world.player),

        # Intro Factory.1
        f"{ZOEREGION.FACTORY_1} -> {ZOEREGION.GLOBAL_HUB}":
            lambda state: state.has_all(ZOEITEM.GLOBAL_FCMD, world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1_TEMPEST}":
            lambda state: state.has(ZOEITEM.TOWN_1, world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1}":
            lambda state: state.has(ZOEITEM.TOWN_1, world.player),

    }

    rules_dict: dict[str, Callable] = {

        ZOELOCATION.FACTORY_1_FLY_AWAY:
            lambda state: state.has_all([ZOEITEM.GLOBAL_FCMD, ZOEITEM.PASS_GLOBAL], world.player),
        ZOELOCATION.TOWN_1_TEMPEST:
            lambda state: state.has_all([ZOEITEM.GLOBAL_FCMD, ZOEITEM.PASS_GLOBAL], world.player)
    }

    for region in world.multiworld.get_regions(world.player):
        for entrance in region.entrances:
            add_rule(entrance, region_rules_dict.get(entrance.name, lambda _: True))
    for location in world.get_locations():
        add_rule(location, rules_dict.get(location.name, lambda _: True))

    world.multiworld.completion_condition[world.player] = lambda state: state.has(ZOEITEM.VICTORY, world.player)
