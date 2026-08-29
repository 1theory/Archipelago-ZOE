"""This module contains the ZOE Option class, containing all adjustable YAML options"""
from dataclasses import dataclass

from Options import Accessibility, DeathLink, OptionGroup, ProgressionBalancing, StartInventoryPool
from worlds.AutoWorld import PerGameCommonOptions
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.options.exclude_options import ZOEExcludeLocations
from worlds.zoe.options.weapons_options import Weapons
from worlds.zoe.options.infos_options import Infos
from worlds.zoe.options.passcodes_items_options import PasscodeItems
from worlds.zoe.options.passcodes_locations_options import PasscodeLocs
from worlds.zoe.options.vrtraining_options import VRTraining
from worlds.zoe.options.local_server_options import LocalServers
from worlds.zoe.options.modules_options import Modules
from worlds.zoe.options.trap_weight_options import TrapWeight
from worlds.zoe.options.traps_options import EnableTraps
from worlds.zoe.options.filler_weight_options import FillerWeight
from worlds.zoe.options.configuration_options import Configuration
from worlds.zoe.options.enemy_counter_options import EnemyCounter
from worlds.zoe.options.linear_play_options import LinearPlay

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
    infos: Infos
    passcodes_locs: PasscodeLocs
    passcodes_items: PasscodeItems
    vrtraining: VRTraining
    filler_weight: FillerWeight
    traps_enabled: EnableTraps
    trap_weight: TrapWeight
    configuration: Configuration
    linear_play : LinearPlay

zoe_option_groups = [
    OptionGroup("Generic Options", [
        ProgressionBalancing,
        Accessibility,
        DeathLink,
    ]),
    OptionGroup("ZOE Item Options", [
        Weapons,
        Modules,
        Infos,
        PasscodeItems,
        LinearPlay,
        EnableTraps,
        TrapWeight,
        FillerWeight,
    ]),
    OptionGroup("ZOE Location Options", [
         EnemyCounter,
         LocalServers,
         PasscodeLocs,
         VRTraining,
#        MetatronOre,
    ]),
    OptionGroup("ZOE QoL Options", [
        Configuration,
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
    ZOEOPTION.INFOS,
    ZOEOPTION.PASSCODES_ITEMS,
    ZOEOPTION.PASSCODES_LOCS,
    ZOEOPTION.LINEAR_PLAY,
    ZOEOPTION.VRTRAINING,
    ZOEOPTION.ENEMY_COUNTER,
    ZOEOPTION.FILLER_WEIGHT,
    ZOEOPTION.ENABLE_TRAPS,
    ZOEOPTION.TRAP_WEIGHT,
    ZOEOPTION.EXCLUDE,
    ZOEOPTION.CONFIGURATION
]
