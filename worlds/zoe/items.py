"""This module provides handling for Item objects"""

from logging import DEBUG, getLogger
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from worlds.zoe.constants.data.item import (goal_data, area_data, item_counts, item_table, ZOEITEMDATA,
                                            PROG_TO_NAME_DICT,)
from worlds.zoe.constants.item_tags import ZOEITEMTAG
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.zoeoptions import ZoeOptions

if TYPE_CHECKING:
    from worlds.zoe.world import ZoeWorld


class GameItem(Item):
    """Zone of the Enders Items"""
    game = ZOEOPTION.GAME_TITLE_FULL


zoe_logger = getLogger(ZOEOPTION.GAME_TITLE_FULL)
zoe_logger.setLevel(DEBUG)


def create_itempool(world: "ZoeWorld") -> list[Item]:
    """Returns a list of items to be added to the item pool after checking options"""
    itempool: list[Item] = []
    options: type[ZoeOptions] = world.options

    for name, entry in item_table.items():
        item_type: ItemClassification = entry.AP_CLASSIFICATION
        item_tags: list[str] = entry.TAGS
        if item_type in [ItemClassification.filler, ItemClassification.trap]:
            continue
        if ZOEITEMTAG.UNUSED in item_tags:
            continue
        # Already placed items (Starting items and vanilla)
        if name in world.preplaced_items:
            count = world.preplaced_items.count(name)
            if item_amount <= count:
                continue
            item_amount -= count  # remove one from the pool as it has already been placed

        if ZOEITEMTAG.INFO in item_tags and not options.infos.value:
            continue
        if ZOEITEMTAG.WEAPON in item_tags and not options.weapons.value:
            continue
        if ZOEITEMTAG.MODULE in item_tags and not options.modules.value:
            continue
        if ZOEITEMTAG.PASSCODE in item_tags and not options.passcodes_items.value:
            continue
        # Catch accidental duplicates
        #if item_amount is None:
        #    zoe_logger.warning(f"{name} has an incorrect amount count")
        #else:
        #    if item_amount > 1:
        #        zoe_logger.warning(f"multiple copies of {name} added to the item pool")
        itempool += create_multiple_items(world, name, item_type)

    victory = create_item(world, ZOEITEM.VICTORY)
    world.multiworld.get_location(ZOELOCATION.TOWN_1_TEMPEST, world.player).place_locked_item(victory)
    return itempool


def create_multiple_items(world: "ZoeWorld", name: str, count: int = 1,
                          item_type: ItemClassification = ItemClassification.progression) -> list[Item]:
    """Returns a list containing multiple copies of an item requested"""
    data: ZOEITEMDATA = item_table[name]
    itemlist: list[Item] = []

    for _ in range(count):
        itemlist += [GameItem(name, item_type, data.AP_CODE, world.player)]

    return itemlist


def create_item(world: "ZoeWorld", name: str) -> Item:
    """Returns a new instance of an Item"""
    data = item_table.get(name, goal_data.get(name))
    if data is None:
        raise KeyError(f"{name} not found in item_table")
    return GameItem(name, data.AP_CLASSIFICATION, data.AP_CODE, world.player)


def get_filler_selection(world: "ZoeWorld") -> list[str]:
    """Returns a list of item names to be used when choosing filler"""
    frequencies = world.options.filler_weight.value
    if world.options.traps_enabled.value:
        traps = world.options.trap_weight.value
        frequencies.update(traps)
    if not frequencies or all(count == 0 for count in frequencies.values()):
        frequencies[ZOEITEM.JEHUTY_EXP] = 1  # set bolts to be the only filler if the filler weights are empty
    return [name for name, count in frequencies.items() for _ in range(count)]


def process_start_inventory(world: "ZoeWorld"):
    """Process the player's starting inventory options to account settings and convert items if needed"""
    world.options.start_inventory_from_pool.value.pop(ZOEITEM.HANGAR_1, None)
    world.options.start_inventory.value.pop(ZOEITEM.HANGAR_1, None)


#def starting_areas(world: "ZoeWorld") -> list[str]:
#    """Returns the areas randomly selected for the player to start with"""
#    area_list: list[str] = [area for area in area_data.keys() if
#                              area not in world.options.start_inventory_from_pool.value]
#    if len(area_list) > 1:  
#        world.random.shuffle(area_list)
#    return area_list
