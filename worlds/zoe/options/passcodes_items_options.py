"""This module contains options for Passcode items in the item pool"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class PasscodeItems(Choice):
    """
    Determines whether Passcode items are included in the item pool.
    ------------------------------------------------------------
    Disabled: No passcodes will be included in the item pool.
    Enabled:  Passcodes will be included in the item pool.
    ------------------------------------------------------------
    Note: In the future, passcodes are going to have an option that makes it so you need to have them
    in order to use obtained modules/weapons.
    """
    display_name = ZOEOPTION.PASSCODES_ITEMS
    option_disabled = 0
    option_enabled = 1
    default = 0
