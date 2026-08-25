"""This module provides an ZOE interface to control the game"""
import time
from dataclasses import dataclass
from random import choice, randint, uniform
from typing import Any

from typing_extensions import deprecated

from BaseClasses import ItemClassification
from CommonClient import logger
from Utils import __version__
from worlds.zoe.client.general_interface import GameInterface
from worlds.zoe.constants.check_type import CHECKTYPE
#from worlds.zoe.constants.cutscene_flag import ZOECUTSCENEFLAG
from worlds.zoe.constants.data.address import ZOEADDRESSDATA, SAVE_DATA
from worlds.zoe.constants.data.item import (passcode_data, info_data, module_data, area_data, PROG_TO_NAME_DICT,
                                             ITEM_FROM_AP_CODE, ITEM_NAME_FROM_ID, weapon_data, ZOE_ITEM_DATA_TABLE, timer_to_status)
from worlds.zoe.constants.data.location import (LOCATION_FROM_AP_CODE, ZOE_LOCATION_DATA_TABLE, ZOELOCATIONDATA,)
from worlds.zoe.constants.data.region import ZOE_REGION_DATA_TABLE
from worlds.zoe.constants.functions import ZOEFUNCTION 
from worlds.zoe.constants.item_tags import ZOEITEMTAG
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.locations.tags import ZOETAG
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.progress_flag import ZOEPROGRESSFLAG
from worlds.zoe.constants.region import ZOEREGION, AREA_NAME_FROM_ID
from worlds.zoe.constants.status import ZOESTATUS
from worlds.zoe.constants.version import GAME_ID_TO_VERSION, ZOEVERSION
from worlds.zoe.constants.configuration import ZOECONFIGURATION

class ZoeInterface(GameInterface):
    """Handles reading and modifying the game memory"""

    @dataclass
    class UnlockData:
        """Data structure for tracking if items should be unlocked and if they are now being unlocked"""
        status: int
        unlock_delay: int

        def __init__(self,
                     status: int = 0,
                     unlock_delay: int = 0):
            self.status = status
            self.unlock_delay = unlock_delay

        def __repr__(self):
            return f"{{ status: {self.status}, unlock_delay: {self.unlock_delay} }}"

    @dataclass
    class Options:
        """Data structure for storing options"""
        start_inventory_from_pool: dict[str, int]
        exclude_locations: set[str]
        deathlink: int
        filler_weight: dict[str, int]
        weapons: int
        enemy_counter: int
        modules: int
        local_server: int
        infos: int
        passcodes_loc: int
        passcodes_items: int
        vrtraining: int
        weapons: int
        traps_enabled: int
        trap_weight: dict[str, int]
        configuration: dict[str, int]

    UnlockItem: dict[str, UnlockData] = None
    options = Options
    timers: dict[str, float] = {}
    area: str = ZOEREGION.GLOBAL_HUB
    new_area: bool = True
    max_health: int = 10
    main_menu: bool = False
    death_count: int = 0
    last_death_count: int = 0
    has_died: bool = False
    player_level: int = 0
    jehuty_exp: int = 0
    checked_locations: set[str] = set()
    unfreeze_packs: bool = False
    stored_fillers: dict[str, int] = {}
    initial_fillers: dict[str, int] = {}
    equipped_weapon: int = 0

    def __init__(self):
        super().__init__()  # GameInterfaceの初期化

    #####################
    # Inherit functions #
    #####################

    def _read8(self, address: int) -> int:
        return super()._read8(self.address_convert(address))

    def _read16(self, address: int) -> int:
        return super()._read16(self.address_convert(address))

    def _read32(self, address: int) -> int:
        return super()._read32(self.address_convert(address))

    def _read_bytes(self, address: int, n: int) -> bytes:
        return super()._read_bytes(self.address_convert(address), n)

    def _read_float(self, address: int) -> float:
        return super()._read_float(self.address_convert(address))

    def _read_string(self, address, n) -> str:
        return super()._read_string(self.address_convert(address), n)

    def _read_bits(self, address: int) -> set[int]:
        bits: set[int] = set()
        value = self._read8(address)
        for i in range(8):
            if value & (1 << i):
                bits.add(i)
        return bits

    def _write8(self, address: int, value: int):
        return super()._write8(self.address_convert(address), value)

    def _write16(self, address: int, value: int):
        return super()._write16(self.address_convert(address), value)

    def _write32(self, address: int, value: int):
        return super()._write32(self.address_convert(address), value)

    def _write_bytes(self, address: int, value: bytes):
        return super()._write_bytes(self.address_convert(address), value)

    def _write_float(self, address: int, value: float):
        return super()._write_float(self.address_convert(address), value)

    def _write_string(self, address: int, value: str):
        return super()._write_string(self.address_convert(address), value)

    def _write_bits(self, address: int, value: set[int]):
        bits = self._read_bits(address)
        if value.issubset(bits):
            return None
        bits |= value
        write: int = 0
        for bit in bits:
            if 0 <= bit <= 7:
                write += 1 << bit
            else:
                raise ValueError(f"Invalid bit position {bit}")

        return self._write8(address, write)

    def _unwrite_bits(self, address: int, value: set[int]):
        bits = self._read_bits(address)
        if value.isdisjoint(bits):
            return None
        bits -= value
        write: int = 0
        for bit in bits:
            if 0 <= bit <= 7:
                write += 1 << bit
            else:
                raise ValueError(f"Invalid bit position {bit}")

        return self._write8(address, write)

    def address_convert(self, address: int):
        """Address conversion from str to int, and for version correction (with US/JP/EU)"""
        _addr = address
        if isinstance(address, str):
            _addr = int(address, 0)
#        if (0x001DC7C0 <= _addr <= 0x00300000
#            and self.current_game == ZOEVERSION.EU_ID):
#            _addr += GAME_ID_TO_OFFSET[ZOEVERSION.EU_ID]
#        if self.current_game == ZOEVERSION.JP_ID:
#            _addr = jp_convert_address(_addr, self.area)
        return _addr

    ###############################
    # Called on Server Connection #
    ###############################

    def proc_option(self, slot_data: dict[str, Any]):
        """Process slot option data received when connecting to the server"""
        logger.debug(f"Processing options: {slot_data}")
        self.options.start_inventory_from_pool = slot_data[ZOEOPTION.START_INVENTORY_FROM_POOL]
        self.options.modules = slot_data[ZOEOPTION.MODULES]
        self.options.infos = slot_data[ZOEOPTION.INFOS]
        self.options.trap_weight = slot_data[ZOEOPTION.TRAP_WEIGHT]
        self.options.traps_enabled = slot_data[ZOEOPTION.ENABLE_TRAPS]
        self.options.weapons = slot_data[ZOEOPTION.WEAPONS]
        self.options.enemy_counter = slot_data[ZOEOPTION.ENEMY_COUNTER]
        self.options.vrtraining = slot_data[ZOEOPTION.VRTRAINING]
        self.options.local_server = slot_data[ZOEOPTION.LOCAL_SERVERS]
        self.options.passcodes_items = slot_data[ZOEOPTION.PASSCODES_ITEMS]
        self.options.passcodes_locs = slot_data[ZOEOPTION.PASSCODES_LOCS]
        self.options.configuration = slot_data[ZOEOPTION.CONFIGURATION]
        self.options.exclude_locations = slot_data[ZOEOPTION.EXCLUDE]
        self.options.deathlink = slot_data[ZOEOPTION.DEATHLINK]
        self.options.filler_weight = slot_data[ZOEOPTION.FILLER_WEIGHT]

    ########################################
    # Called on Game and Server Connection #
    ########################################

    def init(self):
        """Initialise values once the game and server are both connected"""
        self.UnlockItem = {name: self.UnlockData() for name in ITEM_FROM_AP_CODE.values()}
        logger.debug(f"UnlockItem dict:{self.UnlockItem.keys()}")

    def check_main_menu(self):
        """Check if the player is on the main menu, before starting the game"""
        if self._read8(ZOESTATUS.CURRENT_AREA) == 0x00:
            return True
        return False

    def check_pause(self):
        """Check if the player has the game paused"""
        if self._read8(ZOESTATUS.PAUSE_STATE) == 0x01:
            return True
        return False

    ##########################
    # Called on Loading File #
    ##########################

    def reset_file(self):
        """Remove all items and progress on the current file, ready to be set based on current slot progress"""
        self.remove_all_items()
        self.undo_collections()

    def remove_all_items(self):
        """Remove all items from the player's inventory"""
        for item in self.UnlockItem.keys():
            self.UnlockItem[item].status = 0
        self.UnlockItem[ZOEITEM.HANGAR_1].status = 1
        self.UnlockItem[ZOEITEM.FACTORY_1].status = 1
        self.UnlockItem[ZOEITEM.TOWN_1].status = 1
        self.UnlockItem[ZOEITEM.GLOBAL_HUB].status = 1
        self.timers.clear()
        self.checked_locations.clear()
        self.module_cycler()
        self.weapon_cycler()
        self.info_cycler()
        self.passcode_cycler()
        self.timer_cycler()

    def undo_collections(self):
        """Unset flags in the game associated to randomizer locations"""
        checks: dict[int, set[int]] = {}
        for location in ZOE_LOCATION_DATA_TABLE.values():
            for check in location.CHECK_ADDRESS:
                if check.TYPE & CHECKTYPE.SIZE == CHECKTYPE.BIT:
                    checks.setdefault(check.ADDRESS, set()).add(check.VALUE)
        for address, value in checks.items():
            self._unwrite_bits(address, value)

    def important_items(self, item: int, us: str, location: int):
        """Runs when loading into game from the main menu to update the player with important items from the server,
        skips filler and trap items to not flood the player with bolts/xp"""
        if (ZOEITEMTAG.FILLER in ZOE_ITEM_DATA_TABLE[ITEM_FROM_AP_CODE[item]].TAGS or ZOEITEMTAG.TRAP in
            ZOE_ITEM_DATA_TABLE[ITEM_FROM_AP_CODE[item]].TAGS):
            return
        self.item_received(item, us, None, location)

    def filler_items(self, item: int):
        """Runs when loading into game from the main menu to update the player with filler items from the server"""
        if ZOEITEMTAG.FILLER in ZOE_ITEM_DATA_TABLE[ITEM_FROM_AP_CODE[item]].TAGS:
            self.initial_fillers[ITEM_FROM_AP_CODE[item]] = self.initial_fillers.get(ITEM_FROM_AP_CODE[item], 0) + 1
            if self.initial_fillers[ITEM_FROM_AP_CODE[item]] > 255:
                self.initial_fillers[ITEM_FROM_AP_CODE[item]] = 255

    def process_offline_fillers(self, data_received: bool):
        """Process any filler items received while offline"""
        logger.debug(f"Initial filler items: {self.initial_fillers} and data received: {data_received}")
        if not data_received:
            return
        for item, count in self.initial_fillers.items():
            stored_count = self.stored_fillers.get(item, 0)
            if count > stored_count:
                diff = count - stored_count
                logger.debug(f"Processing {diff} offline filler items for {item}")
                for _ in range(diff):
                    self.item_received(ZOE_ITEM_DATA_TABLE[item].AP_CODE, None, None, 0)
            else:
                logger.debug(f"No new offline filler items for {item} (stored: {stored_count}, current: {count})")
        self.stored_fillers = self.initial_fillers.copy()

    def collect_locations(self, locations: set[str]) -> set[str]:
        """Set the in game flags for this location for it to act as if the player has already collected the item here"""
        checks: dict[int, set[int]] = {}
        output: set[str] = set()
        for location in locations:
            self.checked_locations.add(location)
            output.add(location)
            loc_data: ZOELOCATIONDATA = ZOE_LOCATION_DATA_TABLE[location]
            for check in loc_data.CHECK_ADDRESS:
                if check.TYPE & CHECKTYPE.SIZE == CHECKTYPE.BIT:
                    checks.setdefault(check.ADDRESS, set()).add(check.VALUE)
        for address, value in checks.items():
            self._write_bits(address, value)
        return output

    def load_save(self, save: dict[int, tuple[int, int]]):
        """Set the player's current values based on the server's save-data"""
        if self.main_menu:
            return
        logger.debug(f"Save data: {save}")
        defaults: dict[int, tuple[int, int]] = {data.ADDRESS: (data.TYPE, data.VALUE) for data in SAVE_DATA}
        logger.debug(f"Default values: {defaults}")
        for address, data in save.items():
            # Skip writing default values or lingering dev testing values saved on the server
            default = defaults.get(address)
            if default is None or data == default:
                continue

            size, value = data
            match size:
                case CHECKTYPE.BYTE:
                    self._write8(address, value)
                case CHECKTYPE.SHORT:
                    self._write16(address, value)
                case CHECKTYPE.INT:
                    self._write32(address, value)

    def reset_death_count(self):
        """Update the tracked death count to the value in game"""
        self.death_count = self._read32(ZOESTATUS.TOTAL_CONTINUES)
        self.last_death_count = self.death_count

    def setup_settings(self):
        """Update in game settings based on the slot options"""
        if self.options.configuration.get(ZOECONFIGURATION.VIBRATION, False):
            self._unwrite_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {0})
        if self.options.configuration.get(ZOECONFIGURATION.VIBRATION, True):
            self._write_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {0})
        if self.options.configuration.get(ZOECONFIGURATION.CAPTION_DEMO, False):
            self._unwrite_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {1})
        if self.options.configuration.get(ZOECONFIGURATION.CAPTION_DEMO, True):
            self._write_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {1})
        if self.options.configuration.get(ZOECONFIGURATION.CAPTION_GAME, False):
            self._unwrite_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {2})
        if self.options.configuration.get(ZOECONFIGURATION.CAPTION_GAME, True):
            self._write_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {2})
        if self.options.configuration.get(ZOECONFIGURATION.SOUND, False):
            self._unwrite_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {3})
        if self.options.configuration.get(ZOECONFIGURATION.SOUND, True):
            self._write_bits(ZOESTATUS.CONFIGURATION_BITFLAG, {3})

    def init_stored_fillers(self):
        """Read the stored filler items from memory and fill the stored_fillers dictionary"""
        self.stored_fillers[ZOEITEM.JEHUTY_EXP] = self._read8(ZOESTATUS.JEHUTY_EXP_PACKS)
        self.stored_fillers[ZOEITEM.LEVEL_UP] = self._read8(ZOESTATUS.LEVEL_PACKS)
        self.stored_fillers[ZOEITEM.EXTRA_AMMO] = self._read8(ZOESTATUS.AMMO_PACKS)
        logger.debug(f"Stored filler items: {self.stored_fillers}")

    #############################
    # Start of Main Update Loop #
    #############################

    def early_update(self):
        """Ran early in the update cycle, memory reads should happen here before any evaluations begin"""
        new_area = AREA_NAME_FROM_ID[self._read8(ZOESTATUS.CURRENT_AREA)]
        if self.area != new_area:
            self.area = new_area
            self.new_area = True
        else:
            self.new_area = False
        self.health = self._read8(ZOESTATUS.PLAYER_HEALTH)
        self.level = self._read8(ZOESTATUS.PLAYER_LEVEL)
        self.equipped_weapon = self._read8(ZOESTATUS.EQUIPPED_WEAPON)
        self.jehuty_exp = self._read16(ZOESTATUS.PLAYER_EXPERIENCE)

    #################
    # Receive Items #
    #################

    def item_received(self,
                      item_code: int,
                      our_name: str | None,
                      other_player: str | None,
                      location: int):
        """Handle receiving items from the multiworld"""
        name = PROG_TO_NAME_DICT.get(ITEM_FROM_AP_CODE[item_code], ITEM_FROM_AP_CODE[item_code])
        
        logger.info(f"Item received: {ITEM_FROM_AP_CODE[item_code]}, AP code: {item_code}")
        logger.debug(f"Item received: {ITEM_FROM_AP_CODE[item_code]}, AP code: {item_code}")

        self.UnlockItem[name].status += 1

        match name:                    
                case ZOEITEM.JEHUTY_EXP:
                    exp = self._read16(ZOESTATUS.PLAYER_EXPERIENCE)
                    exp_gain = randint(3, 10)
                    new_exp = exp + exp_gain
                    if new_exp > 0xFFFF:
                        new_exp = 0xFFFF
                    self._write16(ZOESTATUS.PLAYER_EXPERIENCE, new_exp)
                    logger.info(f"Experience received: {exp_gain}, experience updated to {exp}")
                    jehuty_exp_packs = self._read8(ZOESTATUS.JEHUTY_EXP_PACKS)
                    if jehuty_exp_packs <= 0xFF:
                        jehuty_exp_packs += 1
                    self._write8(ZOESTATUS.JEHUTY_EXP_PACKS, jehuty_exp_packs)
                case ZOEITEM.LEVEL_UP:
                    player_level = self._read8(ZOESTATUS.PLAYER_LEVEL)
                    new_lvl = player_level + 1
                    level_packs = 0
                    self._read8(ZOESTATUS.LEVEL_PACKS) == level_packs
                    if level_packs < 0x0A:
                        level_packs += 1
                    self._write8(ZOESTATUS.PLAYER_LEVEL, new_lvl)
                    self._write8(ZOESTATUS.LEVEL_PACKS, level_packs)
                case ZOEITEM.EXTRA_AMMO:
                    pass
    #                ammo_pack = self.current_ammo + 5
    #                for weapon_name in weapon_data.keys():
    #                    if self.UnlockItem[weapon_name].status:
    #                        self._write32(weapon_data[weapon_name].AMMO_ADDRESS, ammo_pack)
                case ZOEITEM.ROTATION_TRAP:
                    if self.timers.get(name, False):
                        self.timers[name] += randint(6, 15)
                    else:
                        self.timers[name] = int(time.time() + uniform(6, 15))
                        
        if name in weapon_data.keys():
                    if weapon_data[name].AMMO:
                        self._write8(weapon_data[name].AMMO_ADDRESS, weapon_data[name].AMMO)
        if name in weapon_data.keys() and self.UnlockItem[name].status == 1:
                    self.update_equip(name)

    def update_equip(self, name: str):
            """Equip the most recently collected weapon/gadget, update recent uses"""

            self._write8(ZOESTATUS.EQUIPPED_WEAPON, weapon_data[name].EQUIP)

    ###################
    # Check Locations #
    ###################

    def is_location_checked(self, ap_code: int) -> bool:
        """Reads location data to find what memory check should be done, returns the collection state of the location"""
        location = LOCATION_FROM_AP_CODE[ap_code]
        if location in self.checked_locations:
            return True
        loc_data: ZOELOCATIONDATA = ZOE_LOCATION_DATA_TABLE[location]
        if not loc_data:
            return False
        check_all: bool = True
        for check in loc_data.CHECK_ADDRESS:
            match check.TYPE & CHECKTYPE.SIZE:
                case CHECKTYPE.BIT:
                    check_all &= check.VALUE in self._read_bits(check.ADDRESS)
                case CHECKTYPE.BYTE:
                    value_to_check = self.cycle_cache.get(check.ADDRESS, None)
                    if value_to_check is None:
                        value_to_check = self._read8(check.ADDRESS)
                        self.cycle_cache[check.ADDRESS] = value_to_check
                    check_all &= self.compare(value_to_check, check)
                case CHECKTYPE.SHORT:
                    value_to_check = self.cycle_cache.get(check.ADDRESS, None)
                    if value_to_check is None:
                        value_to_check = self._read16(check.ADDRESS)
                        self.cycle_cache[check.ADDRESS] = value_to_check
                    check_all &= self.compare(value_to_check, check)
                case CHECKTYPE.INT:
                    value_to_check = self.cycle_cache.get(check.ADDRESS, None)
                    if value_to_check is None:
                        value_to_check = self._read32(check.ADDRESS)
                        self.cycle_cache[check.ADDRESS] = value_to_check
                    check_all &= self.compare(value_to_check, check)
        if check_all:
            self.checked_locations.add(location)
        return check_all

    @staticmethod
    def compare(value: int, check: ZOEADDRESSDATA) -> bool:
        """Compares a value using the checktype provided in data"""
        match check.TYPE & CHECKTYPE.SIGN:
            case CHECKTYPE.EQ:
                return value == check.VALUE
            case CHECKTYPE.NEQ:
                return value != check.VALUE
            case CHECKTYPE.GT:
                return value > check.VALUE
            case CHECKTYPE.LT:
                return value < check.VALUE
            case CHECKTYPE.GE:
                return value >= check.VALUE
            case CHECKTYPE.LE:
                return value <= check.VALUE
        return False

    #############
    # Deathlink #
    #############

    def alive(self) -> tuple[bool, str]:
        """Checks the current game state to determine if the player is still alive, and if not then how they died"""
        if self.has_died:
            self.last_death_count = self.death_count
            logger.debug("Death Detected! (death count increased)")
            death = (ZOESTATUS.GAME_OVER == 1)
            return False, f"{death}"

        # logger.debug(f"{self.player_type} is Alive")
        return True, f"is Alive"

    def can_be_killed(self) -> bool:
        """Checks if the player can be killed based on the current game state."""
        if self.main_menu is True or ZOESTATUS.PAUSE_STATE == 0x01:
            return False
        else:
            return True 

    def kill_player(self) -> bool:
        """Checks the current game state to determine if and how to kill the player, returns success/failure"""
        if not self.can_be_killed():
            logger.debug("player unable to be killed")
            return False
        self._write8(ZOESTATUS.GAME_OVER, 1)
        logger.debug("player successfully killed")
        return True

    ##############
    # Check Goal #
    ##############

    @staticmethod
    def get_victory_code():
        """Returns the apcode value of the goal location"""
        return ZOE_LOCATION_DATA_TABLE[ZOELOCATION.CITY_1_DESTROY_RELAY_BLOCK].AP_CODE

    ##################
    # End of Main Loop #
    ##################

    def late_update(self):
        """Ran at the end of the main loop to update any memory values based on collection state"""
        #self.area_cycler()
        self.module_cycler()
        self.weapon_cycler()
        self.info_cycler()
        self.passcode_cycler()
        #self.overflow_fix()
        self.respawn_local_servers()
        self.area_unlock_cycler()
        self.timer_cycler()

    def module_cycler(self):
        """Cycles through each module and updates their state"""
        if self.options.modules:
            READ_MONITOR_MODULE = ZOEFUNCTION.READ_MONITOR_MODULE_NTSC
            READ_FLIGHT_MODULE = ZOEFUNCTION.READ_FLIGHT_MODULE_NTSC
            #logger.info(f"Scouting module received: {self.UnlockItem[ZOEITEM.MONITOR_FCMD].status}")
            if self.UnlockItem[ZOEITEM.MONITOR_FCMD].status == 0:
                self._write32(READ_MONITOR_MODULE, 0x8C820B24) # overwrite the function that reads the module and makes it work to prevent using it while not receiving from the multiworld
            else:
                self._write32(READ_MONITOR_MODULE, 0x8C820024) # reestablish the function if obtained from the multiworld
            if self.UnlockItem[ZOEITEM.GLOBAL_FCMD].status == 0:
                self._write32(READ_FLIGHT_MODULE, 0x8C820B24) # similar to the above
            else:    
                self._write32(READ_FLIGHT_MODULE, 0x8C820024)

            for name in module_data.keys():
                bit = module_data[name].BITSET
                if self.UnlockItem[name].status:
                    if self.UnlockItem[name].unlock_delay:
                        self._write_bits(ZOESTATUS.OBTAINED_MODULES, {bit})
                        self.UnlockItem[name].unlock_delay = 0
                    else:
                        self.UnlockItem[name].unlock_delay += 1
                else:
                    self._unwrite_bits(ZOESTATUS.OBTAINED_MODULES, {bit})

            #TODO: research what the raptor control, anti-stealth and vaccine do (if they trigger game flags) and if they have different read addresses 

    def weapon_cycler(self):
        """Interval update function: Check unlock/lock status of weapons"""
        if self.options.weapons:
            for name in weapon_data.keys():
                bit_set = weapon_data[name].BITSET
                ammo_addr = weapon_data[name].AMMO_ADDRESS
                if self.UnlockItem[name].status:
                    if self.UnlockItem[name].unlock_delay:
                        self._write_bits(ZOESTATUS.OBTAINED_WEAPONS, {bit_set})
                        self.UnlockItem[name].unlock_delay = 0
                    else:
                        self.UnlockItem[name].unlock_delay += 1
                    if name == ZOEITEM.DECOY or ZOEITEM.MUMMY: # the Decoy and the Mummy are both in the modules bitflag, this 'if' manages it
                        if self.UnlockItem[name].unlock_delay:
                            self._write_bits(ZOESTATUS.OBTAINED_MODULES, {bit_set})
                            self.UnlockItem[name].unlock_delay = 0
                        else:
                            self.UnlockItem[name].unlock_delay += 1
                else:
                    # Prevent the player from using locked weapons
                    if name != ZOEITEM.DECOY or ZOEITEM.MUMMY: # if the state is false and the weapon is neither the Decoy or the Mummy, prevent the use of the others
                        self._unwrite_bits(ZOESTATUS.OBTAINED_WEAPONS, {bit_set})
                        self._write8(ammo_addr, 0)
                    if name == ZOEITEM.DECOY or ZOEITEM.MUMMY:
                        if self.UnlockItem[name].status == 0:
                            self._unwrite_bits(ZOESTATUS.OBTAINED_MODULES, {bit_set})
                            self._write8(ammo_addr, 0)

    def info_cycler(self):
        """Cycles through each info (just antilia.info) and updates its state"""
        if self.options.infos:
            for name in info_data.keys():
                bit = info_data[name].BITSET
                if self.UnlockItem[name].status:
                    if self.UnlockItem[name.unlock_delay]:
                        self._write_bits(ZOESTATUS.OBTAINED_INFO, {bit})
                        self.UnlockItem[name].unlock_delay = 0
                    else:
                        self.UnlockItem[name].unlock_delay += 1
                else:
                    self._unwrite_bits(ZOESTATUS.OBTAINED_INFO, {bit})
                    if self._read(ZOESTATUS.STORY_PROGRESS) > 0x08: # prevent unlocking both the cutscene and the EPS.1 and EPS.2 areas without the info
                        self._write8(ZOESTATUS.STORY_PROGRESS, 0x08) 

    def passcode_cycler(self):
        """Cycles through each passcode item and location and updates their state"""
        if self.options.passcodes_items:
            WRITE_PASSCODES = ZOEFUNCTION.WRITE_PASSCODES_NTSC
            self._write32(WRITE_PASSCODES, 0xACA20B1C) # prevent game from reading vanilla-obtained passcodes by writing them somewhere else
            for name in passcode_data.keys():
                bit = passcode_data[name].BITSET
                if self.UnlockItem[name].status:
                    if self.UnlockItem[name.unlock_delay]:
                        self._write_bits(ZOESTATUS.OBTAINED_PASSCODES, {bit}) # write the specified bit to the passcode address
                        self.UnlockItem[name].unlock_delay = 0
                    else:
                        self.UnlockItem[name].unlock_delay += 1
                    if name == (ZOEITEM.PASS_DECOY2 or ZOEITEM.PASS_GLOBAL or
                                ZOEITEM.PASS_CONTROL1 or ZOEITEM.PASS_CONTROL2 or
                                ZOEITEM.PASS_VACCINE or ZOEITEM.PASS_ANTILLIA):
                        if self.UnlockItem[name.unlock_delay]:
                             self._write_bits(ZOESTATUS.OBTAINED_PASSCODES_2, {bit}) # write the specified bit to the SPECIFIC passcode address
                             self.UnlockItem[name].unlock_delay = 0
                        else:
                            self.UnlockItem[name].unlock_delay += 1
                        
                else: # unwrite bits from vanilla-obtained passcodes in case the instruction fails
                    if name == (ZOEITEM.PASS_DECOY2 or ZOEITEM.PASS_GLOBAL or
                                ZOEITEM.PASS_CONTROL1 or ZOEITEM.PASS_CONTROL2 or
                                ZOEITEM.PASS_VACCINE or ZOEITEM.PASS_ANTILLIA):
                        self._unwrite_bits(ZOESTATUS.OBTAINED_PASSCODES_2, {bit})
                    else:
                        self._unwrite_bits(ZOESTATUS.OBTAINED_PASSCODES, {bit})

    def timer_cycler(self):
        """Cycle through the timer dictionary, check their duration, and handle their effects"""
        timers = list(self.timers.items())
        for name, _time in timers:
            if name.endswith(str(_time)):
                _name = name[:-len(str(_time))]
            else:
                _name = name
            if time.time() < _time:
                if _name == name:
                    status = timer_to_status[name]
                    match status:
                        case ZOESTATUS.ROTATION:
                            self._write16(status, 0)
                            self._write8(status + 4, 0)
                            self._write8(ZOESTATUS.ROTATION, 3)

            else:
                self.timers.pop(name)
                match _name:
                    case ZOEITEM.ROTATION_TRAP:
                        self._write8(ZOESTATUS.ROTATION, 0)

    def respawn_local_servers(self):
        """Respawn local servers if the associated location isn't checked but the local server's associated program is unlocked through AP"""
        if self.options.local_server:
            if (self.UnlockItem[ZOEITEM.MONITOR_FCMD].status # if player has the monitor.fcmd but has not checked the local server loc., overwrite the address that reads it
                and ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER not in self.checked_locations
                and self.area == ZOEREGION.FACTORY_1 or ZOEREGION.HANGAR_1 and self._read8(ZOESTATUS.STORY_PROGRESS) <= 0x02): 
                self._write32(ZOEFUNCTION.READ_MODULES_NTSC, 0x8C820C24)

            if (self.UnlockItem[ZOEITEM.GLOBAL_FCMD].status
                and ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER not in self.checked_locations
                and self.area == ZOEREGION.FACTORY_1 or ZOEREGION.HANGAR_1 and self._read8(ZOESTATUS.STORY_PROGRESS) <= 0x02):
                self._write32(ZOEFUNCTION.READ_MODULES_NTSC, 0x8C820C24)
                self._write32(ZOEFUNCTION.READ_BLOCKED_MODULES_NTSC, 0x8C620C24) # in case the player has the global.fcmd without checking its local server while it is blocked

        #TODO: research if it is needed for other servers and find their reading address if it is different

    def area_unlock_cycler(self):
        """Try to prevent the player from accessing locked areas""" # making the player access to unlocked areas is unviable at the moment because area unlocks are directly linked to story progress
        for name in area_data.keys():
            if self.UnlockItem[ZOEITEM.TOWN_1].status == 0 and self._read8(ZOESTATUS.CURRENT_AREA) == ZOEREGION.GLOBAL_HUB:
                self._write32(ZOEFUNCTION.CIRCLE_INPUT, 0x97A60000) # prevent the player from entering TOWN.1
        if (ZOELOCATION.TOWN_1_TEMPEST not in self.checked_locations and self._read8(ZOESTATUS.STORY_PROGRESS) >= 0x05):
            self._write8(ZOESTATUS.STORY_PROGRESS, 0x04) # failsafe in case somehow the player progresses further without destroying Tempest
        if (self.UnlockItem[ZOEITEM.ANTILLIA_INFO].status == 1 and self._read8(ZOESTATUS.STORY_PROGRESS) <= 0x08
            and ZOELOCATION.TOWN_1_TEMPEST in self.self.checked_locations):
            self._write8(ZOESTATUS.STORY_PROGRESS, 0x09) # force the antilia.info use if collected and Tempest is destroyed           

        #TODO: research the loading areas instructions to see if we can overwrite them somehow
        #TODO: use the global.hub barrier to our advantage. we can position and/or activate/deactivate it wherever
        #TODO: add more story progress failsafes for rescue missions
        #TODO: find a way to check the current area while in GLOBAL.HUB to succesfully prevent entering locked areas by checking that and not just globally disabling the circle press

    def update_save(self) -> dict[int, tuple[int, int]]:
        """Check if the game save is different to the server"""
        save: dict[int, tuple[int, int]] = {}
        for data in SAVE_DATA:
            match data.TYPE:
                case CHECKTYPE.BYTE:
                    save[data.ADDRESS] = (data.TYPE, self._read8(data.ADDRESS))
                case CHECKTYPE.SHORT:
                    save[data.ADDRESS] = (data.TYPE, self._read16(data.ADDRESS))
                case CHECKTYPE.INT:
                    save[data.ADDRESS] = (data.TYPE, self._read32(data.ADDRESS))

        return save