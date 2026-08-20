"""This module contains options for Module items in the item pool"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class Infos(Choice):
    """
    Determines whether Info items are included in the item pool.
    ------------------------------------------------------------
    Disabled: No info will be included in the item pool.
    Enabled:  Infos will be included in the item pool.
    ------------------------------------------------------------
    """
    display_name = ZOEOPTION.INFOS
    option_disabled = 0
    option_enabled = 1
    default = 1
