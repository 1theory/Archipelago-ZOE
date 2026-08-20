"""This module contains options for weighting traps in the item pool"""

from Options import ItemDict
from worlds.zoe.constants.data.item import trap_data
from worlds.zoe.constants.options import ZOEOPTION


class TrapWeight(ItemDict):
    """
    Sets the relative weights of trap items in the item pool.
    A higher value increases the likelihood of a particular trap to appear in the item pool.
    This option has no effect when traps are disabled.
    """
    display_name = ZOEOPTION.TRAP_WEIGHT
    min = 0
    max = 100
    valid_keys = trap_data.keys()
    default = dict.fromkeys(trap_data.keys(), 1)
