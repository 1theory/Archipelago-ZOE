"""This module contains options for choosing the way of playing"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class LinearPlay(Choice):
    """
    Determines how the area unlocks will work .
    ------------------------------------------------------------
    Disabled: The area unlocks will work as items.
    Enabled:  The area unlock items will be placed in their vanilla locations.
    ------------------------------------------------------------
    Note: If enabled, you will need just a few items from the multiworld to get to the end of the game by yourself.
    """
    display_name = ZOEOPTION.LINEAR_PLAY
    option_disabled = 0
    option_enabled = 1
    default = 1
