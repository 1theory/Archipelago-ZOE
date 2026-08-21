"""This module provides handling for location regions"""

from typing import TYPE_CHECKING

from BaseClasses import Location, Region
from worlds.zoe.constants.data.location import LOCATION_FROM_AP_CODE, ZOE_LOCATION_DATA_TABLE, ZOELOCATIONDATA
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.locations.tags import ZOETAG
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.region import ZOEREGION, REGIONS_WITH_LOCATIONS
from worlds.zoe.zoeoptions import ZoeOptions

if TYPE_CHECKING:
    from worlds.zoe.world import ZoeWorld


class GameLocation(Location):
    """Zoe game location"""
    game = ZOEOPTION.GAME_TITLE_FULL

def create_regions(world: "ZoeWorld"):
    """Creates each region and connects them together"""
    # ----- Introduction Sequence -----#
    menu = create_region(world, ZOEREGION.MENU)
    hangar_1 = create_region_and_connect(world, ZOEREGION.HANGAR_1, f"{ZOEREGION.MENU} -> {ZOEREGION.HANGAR_1}", menu)
    factory_1 = create_region_and_connect(world, ZOEREGION.FACTORY_1, 
                f"{ZOEREGION.HANGAR_1} -> {ZOEREGION.FACTORY_1}", hangar_1)
    global_hub = create_region_and_connect(world, ZOEREGION.GLOBAL_HUB,
                                           f"{ZOEREGION.FACTORY_1} -> {ZOEREGION.GLOBAL_HUB}", factory_1)

    # ----- Regions within the game -----#   
    create_region_and_connect(world, ZOEREGION.TOWN_1_TEMPEST,
                              f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1_TEMPEST}", global_hub)
    create_region_and_connect(world, ZOEREGION.TOWN_1,
                              f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_1}", global_hub)    
    create_region_and_connect(world, ZOEREGION.TOWN_2,
                              f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.TOWN_2}", global_hub)
    create_region_and_connect(world, ZOEREGION.CITY_1,
                              f"{ZOEREGION.GLOBAL_HUB} -> {ZOEREGION.CITY_1}", global_hub)    

    # ----- Regions for other stuff -----#
    create_region_and_connect(world, ZOEREGION.ENEMYCOUNT, f"{ZOEREGION.MENU} -> {ZOEREGION.ENEMYCOUNT}", menu)

    missing_regions = []
    regions_missing = []
    region_dict = world.multiworld.regions.region_cache[world.player]
    for name in REGIONS_WITH_LOCATIONS:
        if name not in region_dict.keys():
            missing_regions.append(name)
    for name, region in region_dict.items():
        if name not in REGIONS_WITH_LOCATIONS and len(region.locations):
            regions_missing.append(name)
    if missing_regions and regions_missing:
        assert False, (f"Regions: {missing_regions} were declared but not created\nRegions: {regions_missing} were "
                       f"created but not declared.")
    assert missing_regions == [], f"Regions: {missing_regions} were declared but not created."
    assert regions_missing == [], f"Regions: {regions_missing} were created but not declared."

def create_region(world: "ZoeWorld", name: str) -> Region:
    """Returns a new Region object already populated with its item locations"""
    reg = Region(name, world.player, world.multiworld)
    options = world.options
    for key, data in ZOE_LOCATION_DATA_TABLE.items():
        if data.REGION == name and not should_skip_location(data, options):
            location = GameLocation(world.player, key, data.AP_CODE, reg)
            reg.locations.append(location)

    world.multiworld.regions.append(reg)
    return reg

def create_region_and_connect(world: "ZoeWorld", name: str, entrance_name: str, connected_region: Region) -> Region:
    """Returns a new Region, connected to a given region, already populated with its item locations"""
    reg: Region = create_region(world, name)
    connected_region.connect(reg, entrance_name)
    return reg

def should_skip_location(data: ZOELOCATIONDATA, options: type[ZoeOptions]) -> bool:
    """Return False if the location should be skipped based on options."""
    loc = LOCATION_FROM_AP_CODE[data.AP_CODE]
    for tag in data.TAGS:
        match tag:
            case ZOETAG.NOT_IMPLEMENTED:  # Skip all locations not yet implemented
                return True
            case ZOETAG.LOCAL_SERVERS:
                if not options.local_servers.value:  # Skip servers locations if servers are disabled
                    return True
            case ZOETAG.PASSCODES:
                if not options.passcodes_locs.value:
                    return True
            case ZOETAG.VR:
                if not options.vrtraining.value:
                    return True
            case ZOETAG.ENEMYCOUNT:
                if not options.enemy_counter.value:
                    return True
    return False
                
def get_regions() -> set[str]:
    """Returns a set containing the planet names"""
    return {name for name in REGIONS_WITH_LOCATIONS}