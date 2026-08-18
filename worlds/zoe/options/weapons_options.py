"""This module contains options for Weapon items in the item pool"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class Weapons(Choice):
    """
    Determines whether weapons are included in the item pool.
    ------------------------------------------------------------
    Disabled: No weapons will be included in the item pool.
    Enabled:  Weapons will be included in the item pool.
    ------------------------------------------------------------
    """
    display_name = ZOEOPTION.MODULES
    option_disabled = 0
    option_enabled = 1
    default = 1