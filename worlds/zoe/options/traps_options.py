"""This module contains options for trap items in the item pool"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class EnableTraps(Choice):
    """
    Determines whether trap items are included in the item pool.
    ------------------------------------------------------------
    Disabled: No traps will be included in the item pool.
    Enabled:  Traps will be included in the item pool.
    ------------------------------------------------------------
    """
    display_name = ZOEOPTION.ENABLE_TRAPS
    option_disabled = 0
    option_enabled = 1
    default = 0
