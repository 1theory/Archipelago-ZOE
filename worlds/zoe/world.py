"""This module contains the World class for Ratchet and Clank 3"""
from logging import DEBUG, getLogger
from typing import Any, ClassVar, TYPE_CHECKING

from BaseClasses import CollectionState, Item, MultiWorld
from Options import OptionError
from worlds.AutoWorld import World
from worlds.zoe.constants.data.item import item_groups, ZOE_ITEM_DATA_TABLE
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.items import (create_item, create_itempool, get_filler_selection, process_start_inventory,
                               starting_areas, starting_weapons)
from worlds.zoe.locations import get_level_locations, get_location_names, get_total_locations, location_groups
from worlds.zoe.zoeoptions import ZoeOptions
from worlds.zoe.regions import create_regions, get_regions
from worlds.zoe.rules import set_rules
from worlds.zoe.universal_tracker import setup_options_from_slot_data, tracker_world
from worlds.zoe.web_world import ZoeWeb

zoe_logger = getLogger(ZOEOPTION.GAME_TITLE_FULL)
zoe_logger.setLevel(DEBUG)


class ZoeWorld(World):
    f"""
    {ZOEOPTION.GAME_TITLE_FULL} is a hack-and-slash mecha game.
    Save your colony from total destruction.
    """

    game = ZOEOPTION.GAME_TITLE_FULL
    item_name_to_id = {name: data.AP_CODE for name, data in ZOE_ITEM_DATA_TABLE.items()}
    location_name_to_id = get_location_names()
    location_name_groups = location_groups
    item_name_groups = item_groups
    preplaced_items: list[str] = []
    filler_items: list[str] = []
    # Config for Universal Tracker

    using_ut: bool  # so we can check if we're using UT only once
    passthrough: dict[str, Any]
    ut_can_gen_without_yaml: bool = True
    disable_ut: bool = False
    tracker_world: ClassVar = tracker_world

    for region in get_regions():
        location_name_groups[region] = get_level_locations(region)

    options_dataclass = ZoeOptions
    web = ZoeWeb()
    if TYPE_CHECKING:
        options = ZoeOptions

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)

    def generate_early(self):
        # count number of . in the version number to determine if dev build
        version_dots = ZOEOPTION.VERSION_NUMBER.count(".")
        if version_dots >= 3 or "dev" in ZOEOPTION.VERSION_NUMBER:
            zoe_logger.warning("\nYou are using a development build of the Zoe Archipelago Randomizer!\n"
                                "There may be bugs present and features that have not been tested fully.\n"
                                "These builds are meant for testing and bug reporting purposes "
                                "and should not be used for normal play!\n")
        # implement .yaml-less Universal Tracker support
        setup_options_from_slot_data(self)
        create_regions(self)

        starting_weapon_list, starting_area_list = self.generate_starting_items()
        #self.handle_option_errors(starting_area_list, starting_weapon_list)
        #self.dead_seed_check(starting_area_list, starting_weapon_list)
        #self.place_starting_items(starting_area_list, starting_weapon_list)

    #def place_starting_items(self, starting_planet_list: list[str], starting_weapon_list: list[str]):
    #    """Take the list of starting planets and starting weapons and place them on locations or as precollected"""

    #def handle_option_errors(self, starting_planet_list: list[str], starting_weapon_list: list[str]):
    #    """Check for option combinations that will never result in successful seed generation and warn the player"""
    #    raise OptionError("Options selected do not allow Ratchet to collect a Clank Pack and advance past Florana")

    #def dead_seed_check(self, starting_planet_list: list[str], starting_weapon_list: list[str]):
    #    """Check for option combinations that will result in a dead seed and raise an OptionError to warn the player"""
    #    raise OptionError("Options selected do not allow Ratchet to advance past Starship Phoenix")

    def generate_starting_items(self):
        """Process player options to generate a list of early placed items, ensuring successful seed generation"""
        self.preplaced_items = [ZOEITEM.METATRON]
        for item in self.preplaced_items:
            self.push_precollected(self.create_item(item))
        process_start_inventory(self)
        return starting_weapons(self), starting_area(self)

    def create_items(self):
        itempool = create_itempool(self)
        own_location_count = len(self.multiworld.get_unfilled_locations(self.player))
        total_location_count = len(self.multiworld.get_unfilled_locations())
        existing_item_count = len(self.multiworld.itempool)
        item_count = len(itempool)
        placement_location_count = total_location_count - existing_item_count if self.multiworld.players > 1 else (
            own_location_count)
        excluded_count = self.get_excluded_count()
        filler_count = own_location_count - item_count
        if item_count > placement_location_count:
            self.handle_not_enough_locations(item_count - placement_location_count)

        self.multiworld.itempool.extend(itempool)

        if excluded_count > filler_count and (self.multiworld.players == 1 and not self.using_ut):
            self.handle_not_enough_locations(excluded_count - filler_count)

        if filler_count >= 0:
            filler = [self.create_filler() for _ in range(filler_count)]
            self.multiworld.itempool.extend(filler)
        elif self.multiworld.players == 1 and not self.using_ut:
            self.handle_not_enough_locations(-filler_count)

    def get_excluded_count(self) -> int:
        """Get the number of unique excluded locations for this player"""
        excluded_options = self.options.exclude_locations.value
        excluded_locations = set()
        for option in excluded_options:
            if option in location_groups:
                excluded_locations.update(location_groups[option])
            else:
                excluded_locations.add(option)
        return len(excluded_locations)

    def handle_not_enough_locations(self, count):
        """Check the available location and items counts, raise OptionErrors to warn the player of too few locations"""
        excluded_count = self.get_excluded_count()
        option_list: list[str] = []
        if self.options.modules.value == 0:
            option_list.append(ZOEOPTION.MODULES)
        if excluded_count > 30:
            option_list.append(ZOEOPTION.EXCLUDE)
        if not option_list:
            option_list: str = "dunno"  # ¯\_(''/)_/¯
        message = f"Not enough location options enabled! {count} items have nowhere to be placed."
        if count <= 10 and sum(self.options.start_inventory_from_pool.value.values()) <= 10:
            message += "\nConsider adding some items to your starting_items_from_pool or "
        else:
            message += "\nConsider "
        message += f"adjusting some of the following options: {option_list}"
        raise OptionError(message)

    def get_filler_item_name(self) -> str:
        if not len(self.filler_items):
            self.filler_items = get_filler_selection(self)
        return self.random.choice(self.filler_items)

    def set_rules(self):
        set_rules(self)

    def create_item(self, name: str) -> Item:
        return create_item(self, name)

    def fill_slot_data(self) -> dict[str, Any]:
        slot_data: dict[str, Any] = {
            ZOEOPTION.VERSION: ZOEOPTION.VERSION_NUMBER,
            ZOEOPTION.START_INVENTORY_FROM_POOL: self.options.start_inventory_from_pool.value,
            ZOEOPTION.STARTING_WEAPONS: self.options.starting_weapons.value,
            ZOEOPTION.MODULES: self.options.modules.value,
            ZOEOPTION.TOTAL_LOCATIONS: get_total_locations(self),
        }

        return slot_data

    def collect(self, state: "CollectionState", item: "Item") -> bool:
        return super().collect(state, item)

    def remove(self, state: "CollectionState", item: "Item") -> bool:
        return super().remove(state, item)

    # For Universal Tracker integration
    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        """Trigger a regen in UT"""
        return slot_data

