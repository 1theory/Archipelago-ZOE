"""This module contains options for Module items in the item pool"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class Modules(Choice):
    """
    Determines whether Module items are included in the item pool.
    ------------------------------------------------------------
    Disabled: No modules will be included in the item pool.
    Enabled:  Modules will be included in the item pool.
    ------------------------------------------------------------
    """
    display_name = ZOEOPTION.MODULES
    option_disabled = 0
    option_enabled = 1
    default = 1
