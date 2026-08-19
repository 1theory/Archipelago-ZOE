"""This module contains options for Local Server locations"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class LocalServers(Choice):
    """
    Determines whether Local Server are locations in the world.
    -----------------------------------------------------------------------------------------------
    Disabled: No Local Servers are locations.
    Enabled:  Local Servers are added as locations. 
    -----------------------------------------------------------------------------------------------
    """
    display_name = ZOEOPTION.LOCAL_SERVERS
    option_disabled = 0
    option_enabled = 1
    default = 1
