"""This module contains options for adding enemy counter locations"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class EnemyCounter(Choice):
    """
    Determines whether Enemy Counter Locations are included.
    ------------------------------------------------------------
    Disabled: No enemy counter locations will be included.
    Enabled:  Enemy counter locations are included.
    The locations are the following:  5 - 10 - 15 - 20 - 25 - 30
    More locations and options, such as the frequency, will be available in future updates.
    ------------------------------------------------------------
    """
    display_name = ZOEOPTION.ENEMY_COUNTER
    option_disabled = 0
    option_enabled = 1
    default = 1
