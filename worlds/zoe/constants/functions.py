"""This module contains the constant base addresses used when reading in game functions"""

#from worlds.zoe.constants.version import ZOEVERSION

class ZOEFUNCTION:
    """Constant addresses for functions"""

    READ_BLOCKED_MODULES_NTSC = 0x0036BD68
    READ_PASSCODES_NTSC = 0x0036BDC4
    READ_OPEN_MODULES_NTSC = 0x0036BCF8
    WRITE_MODULES_BITFLAG_NTSC = 0x0036C128
    WRITE_MODULES_ADDRESS_NTSC = 0x00282FA4
    WRITE_PASSCODES_TO_UNUSED_NTSC = 0x002843B4
    WRITE_PASSCODES_BITFLAG_NTSC = 0x002843B0