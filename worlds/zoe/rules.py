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
            lambda state: state.has_all([ZOEITEM.GLOBAL_HUB, ZOEITEM.GLOBAL_FCMD, ZOEITEM.MONITOR_FCMD], world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.FACTORY_1}":
            lambda state: state.has(ZOEITEM.FACTORY_1, world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1_TEMPEST}":
            lambda state: state.has_all([ZOEITEM.GLOBAL_FCMD, ZOEITEM.MONITOR_FCMD, ZOEITEM.TOWN_1], world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1}":
            lambda state: state.has(ZOEITEM.TOWN_1, world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_2}":
            lambda state: state.has(ZOEITEM.TOWN_2, world.player),

        f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.CITY_1}":
            lambda state: state.has(ZOEITEM.CITY_1, world.player),            
    }

    rules_dict: dict[str, Callable] = {

        ZOEENEMYCOUNT.ENEMIES_DESTROYED_15:
            lambda state: state.can_reach_region(ZOEREGION.TOWN_1, world.player),
        ZOEENEMYCOUNT.ENEMIES_DESTROYED_25:
            lambda state: state.can_reach_region(ZOEREGION.TOWN_2, world.player),
        ZOEENEMYCOUNT.ENEMIES_DESTROYED_50:
            lambda state: state.can_reach_region(ZOEREGION.CITY_1, world.player),

        ZOELOCATION.FACTORY_1_FLY_AWAY:
            lambda state: state.has_all([ZOEITEM.GLOBAL_FCMD, ZOEITEM.MONITOR_FCMD], world.player),
        ZOELOCATION.TOWN_1_TEMPEST:
            lambda state: state.has_all([ZOEITEM.GLOBAL_FCMD, ZOEITEM.MONITOR_FCMD], world.player),
        ZOELOCATION.FACTORY_1_ANTILIA_INFO:
            lambda state: state.can_reach_location(ZOELOCATION.TOWN_2_RESCUE_MISSION, world.player),
        ZOELOCATION.ANTILIA_INFO:
            lambda state: state.has(ZOEITEM.ANTILLIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_MISSION:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_RANK_A:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_RANK_B:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_RANK_C:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_RANK_D:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        ZOELOCATION.TOWN_1_RESCUE_RANK_E:
            lambda state: state.can_reach_location(ZOELOCATION.ANTILIA_INFO, world.player),
        #ZOELOCATION.TOWN_1_JAVELIN_AMMO_2:
         #   lambda state: state.can_reach_location(ZOELOCATION.TOWN_1_RESCUE_MISSION, world.player),
        #ZOELOCATION.TOWN_1_PHALANX_AMMO:
        #    lambda state: state.can_reach_location(ZOELOCATION.TOWN_1_RESCUE_MISSION, world.player),
        ZOELOCATION.CITY_1_GEYSER_PASSCODE:
            lambda state: state.has(ZOEITEM.SNIPER, world.player),
        ZOELOCATION.CITY_1_GEYSER:
            lambda state: state.has(ZOEITEM.SNIPER, world.player),
        #ZOELOCATION.TOWN_2_JAVELIN_AMMO_2:
        #    lambda state: state.can_reach_region(ZOEREGION.CITY_1, world.player),
        ZOELOCATION.TOWN_2_PHALANX:
            lambda state: state.can_reach_region(ZOEREGION.CITY_1, world.player),
        ZOELOCATION.TOWN_2_SNIPER:
            lambda state: state.can_reach_region(ZOEREGION.CITY_1, world.player),    
        ZOELOCATION.CITY_1_DESTROY_RELAY_BLOCK:
            lambda state: state.has(ZOEITEM.SNIPER, world.player),
    }

    for region in world.multiworld.get_regions(world.player):
        for entrance in region.entrances:
            add_rule(entrance, region_rules_dict.get(entrance.name, lambda _: True))
    for location in world.get_locations():
        add_rule(location, rules_dict.get(location.name, lambda _: True))

    world.multiworld.completion_condition[world.player] = lambda state: state.has(ZOEITEM.VICTORY, world.player)
