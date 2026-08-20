"""This module contains options for VR Training locations"""

from Options import Choice
from worlds.zoe.constants.options import ZOEOPTION


class VRTraining(Choice):
    """
    Determines whether VR Training lessons are locations in the world.
    -----------------------------------------------------------------------------------------------
    Disabled: No lessons are locations.
    Enabled:  Lessons are added as locations. 
    -----------------------------------------------------------------------------------------------
    Note: Softblock warning. You can only enter the VR Training twice for now. 
    """
    display_name = ZOEOPTION.VRTRAINING
    option_disabled = 0
    option_enabled = 1
    default = 1
