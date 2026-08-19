"""This module contains the ZOE Option class, containing all adjustable YAML options"""
from dataclasses import dataclass

from Options import Accessibility, DeathLink, OptionGroup, ProgressionBalancing, StartInventoryPool
from worlds.AutoWorld import PerGameCommonOptions
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.options.exclude_options import ZOEExcludeLocations
from worlds.zoe.options.weapons_options import Weapons
from worlds.zoe.options.local_server_options import LocalServers
from worlds.zoe.options.modules_options import Modules
from worlds.zoe.options.enemy_counter_options import EnemyCounter

def create_option_groups() -> list[OptionGroup]:
    """Return the list of option groups for this world"""
    option_group_list: list[OptionGroup] = []
    for name, options in zoe_option_groups:
        option_group_list.append(OptionGroup(name=name, options=options))

    return option_group_list

@dataclass
class ZoeOptions(PerGameCommonOptions):
    """YAML Options for ZOE"""
    deathlink: DeathLink
    start_inventory_from_pool: StartInventoryPool
    exclude_locations: ZOEExcludeLocations
    weapons: Weapons
    enemy_counter: EnemyCounter
    modules: Modules
    local_server: LocalServers

zoe_option_groups = [
    OptionGroup("Generic Options", [
        ProgressionBalancing,
        Accessibility,
        DeathLink,
    ]),
    OptionGroup("RAC3 Item Options", [
        Weapons,
        Modules,
    ]),
    OptionGroup("RAC3 Location Options", [
         EnemyCounter,
         LocalServers,
#        MetatronOre,
    ]),
    OptionGroup("Item & Location Options", [
        ZOEExcludeLocations,
    ]),
]

slot_data_options: list[str] = [
    ZOEOPTION.DEATHLINK,
    ZOEOPTION.START_INVENTORY_FROM_POOL,
    ZOEOPTION.WEAPONS,
    ZOEOPTION.MODULES,
    ZOEOPTION.LOCAL_SERVERS,
    ZOEOPTION.ENEMY_COUNTER,
    ZOEOPTION.EXCLUDE,
]
