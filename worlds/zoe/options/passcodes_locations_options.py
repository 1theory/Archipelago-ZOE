"""This module contains options for Local Server locations"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class PasscodeLocs(Choice):
    """
    Determines whether passcodes are locations in the world.
    -----------------------------------------------------------------------------------------------
    Disabled: No passcodes are locations.
    Enabled:  Passcodes are added as locations. 
    -----------------------------------------------------------------------------------------------
    """
    display_name = ZOEOPTION.PASSCODES_LOCS
    option_disabled = 0
    option_enabled = 1
    default = 1
