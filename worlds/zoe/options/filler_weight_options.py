"""This module provides weighting options for filler items"""

from Options import ItemDict
from worlds.zoe.constants.data.item import filler_data
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.options import ZOEOPTION


class FillerWeight(ItemDict):
    """
    Sets the relative weights of filler items in the item pool.
    A higher value increases the likelihood of a particular filler item to appear in the item pool.
    """
    display_name = ZOEOPTION.FILLER_WEIGHT
    min = 0
    max = 100
    valid_keys = filler_data.keys()
    default = {
        ZOEITEM.JEHUTY_EXP: 5,
        ZOEITEM.LEVEL_UP: 5,
        #ZOEITEM.EXTRA_AMMO: 10,
    }
