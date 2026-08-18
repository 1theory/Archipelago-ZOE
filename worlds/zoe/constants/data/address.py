"""This module contains the data class for Memory Address data"""
from dataclasses import dataclass

from worlds.zoe.constants.check_type import CHECKTYPE
from worlds.zoe.constants.data.item import weapon_data
from worlds.zoe.constants.status import ZOESTATUS


@dataclass
class ZOEADDRESSDATA:
    """Memory Address data"""
    ADDRESS: int
    TYPE: CHECKTYPE
    VALUE: int

    def __init__(self, data: tuple[int, CHECKTYPE, int]):
        self.ADDRESS, self.TYPE, self.VALUE = data


SAVE_DATA: list[ZOEADDRESSDATA] = [
    # Player Stats
    ZOEADDRESSDATA((ZOESTATUS.PLAYER_HEALTH, CHECKTYPE.BYTE, 10)),
    ZOEADDRESSDATA((ZOESTATUS.PLAYER_EXPERIENCE, CHECKTYPE.INT, 0)),
    ZOEADDRESSDATA((ZOESTATUS.PLAYER_LEVEL, CHECKTYPE.BYTE, 0)),
    *[ZOEADDRESSDATA((weapon.AMMO_ADDRESS, CHECKTYPE.INT, weapon.AMMO)) for weapon in weapon_data.values()],
    # Stored Fillers
    ZOEADDRESSDATA((ZOESTATUS.AMMO_PACKS, CHECKTYPE.INT, 0)),
    ZOEADDRESSDATA((ZOESTATUS.JEHUTY_EXP_PACKS, CHECKTYPE.INT, 0)),
    ZOEADDRESSDATA((ZOESTATUS.LEVEL_PACKS, CHECKTYPE.INT, 0)),
    # Gameplay Progress
    ZOEADDRESSDATA((ZOESTATUS.STORY_PROGRESS, CHECKTYPE.BYTE, 0)),
]