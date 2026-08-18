"""This module contains options for which weapons it is possible to start with"""

from Options import ItemDict
from worlds.zoe.constants.data.item import default_starting_weapons
from worlds.zoe.constants.options import RAC3OPTION


class StartingWeapons(ItemDict):
    """
    Determines which weapons you will be starting the game with,
    provide a count of the weapons you want to be picked between.
    """
    display_name = ZOEOPTION.STARTING_WEAPONS
    min = 0
    max = 5
    default = default_starting_weapons
    valid_keys = default_starting_weapons.keys()
