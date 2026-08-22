"""This module contains options for chosing your preference for the configuration"""

from Options import OptionCounter
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.configuration import CONFIGURATION

class Configuration(OptionCounter):
    """
    Determines how do you want the game to be configured like by default.
    ------------------------------------------------------------
    Default: Vibration ON (1)/ Caption Demo ON (1) Game ON (1)/ Sound STEREO (1) MONO (0)
    ------------------------------------------------------------
    0 = Disabled, Any other value = Enabled
    """
    min = 0
    display_name = ZOEOPTION.CONFIGURATION
    default = dict.fromkeys(CONFIGURATION, 0)
    valid_keys = CONFIGURATION