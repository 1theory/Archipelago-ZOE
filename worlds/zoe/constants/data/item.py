"""This module contains the Items dataclass"""
from dataclasses import dataclass

from BaseClasses import ItemClassification
from worlds.zoe.constants.item_tags import ZOEITEMTAG
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.status import ZOESTATUS

@dataclass
class ZOEITEMDATA:
    """Data class for each item"""
    ID: int
    UNLOCK_ADDRESS: int
    UNLOCK_ADDRESS_2: int
    AMMO_ADDRESS: int
    AMMO: int
    AP_CODE: int
    AP_CLASSIFICATION: ItemClassification
    TAGS: list[str]

    def __init__(self,
                 idx: int,
                 address: int = 0,
                 address_2: int = 0,
                 ammo_address: int = 0,
                 ammo: int = 0,
                 ap_classification: ItemClassification = ItemClassification.filler,
                 tags: list[str] | None = None):
        self.ID = idx
        self.AP_CODE = idx + 50000000
        self.AP_CLASSIFICATION = ap_classification
        self.UNLOCK_ADDRESS = address
        self.UNLOCK_ADDRESS_2 = address_2
        self.AMMO_ADDRESS = ammo_address 
        self.AMMO = ammo
        self.TAGS = tags if tags else []

    @staticmethod
    def construct_unused(idx: int,
                         ammo: int = 0,
                         tags: list[str] | None = None):
        """Construct an unused item"""
        all_tags: list[str] = [ZOEITEMTAG.UNUSED]
        if tags is not None:
            all_tags.extend(tags)
        return ZOEITEMDATA(idx, ammo=ammo, tags=all_tags)

    @staticmethod
    def construct_weapon(idx: int,
                         ammo: int = 0,
                         ap_classification: ItemClassification = ItemClassification.progression_skip_balancing,
                         tags: list[str] | None = None):
        """Construct a weapon item"""
        address: int = ZOESTATUS.OBTAINED_WEAPONS
        all_tags: list[str] = [ZOEITEMTAG.WEAPON]
        if tags is not None:
            all_tags.extend(tags)
        return ZOEITEMDATA(idx, address, ammo, ap_classification=ap_classification, tags=all_tags)

    @staticmethod
    def construct_module(idx: int,
                         ammo: int = 0,
                         ap_classification: ItemClassification = ItemClassification.progression_skip_balancing,
                         tags: list[str] | None = None):
        """Construct a weapon item"""
        address: int = ZOESTATUS.OBTAINED_MODULES
        all_tags: list[str] = [ZOEITEMTAG.MODULE]
        if tags is not None:
            all_tags.extend(tags)
        return ZOEITEMDATA(idx, address, ap_classification=ap_classification, tags=all_tags)

    @staticmethod
    def construct_passcode(idx: int,
                         ammo: int = 0,
                         ap_classification: ItemClassification = ItemClassification.progression_skip_balancing,
                         tags: list[str] | None = None):
        """Construct a weapon item"""
        address: int = ZOESTATUS.OBTAINED_PASSCODES
        all_tags: list[str] = [ZOEITEMTAG.PASSCODE]
        if tags is not None:
            all_tags.extend(tags)
        return ZOEITEMDATA(idx, address, ap_classification=ap_classification, tags=all_tags)

    @staticmethod
    def construct_info(idx: int,
                         ammo: int = 0,
                         ap_classification: ItemClassification = ItemClassification.progression_skip_balancing,
                         tags: list[str] | None = None):
        """Construct an info item"""
        address: int = ZOESTATUS.OBTAINED_INFO
        all_tags: list[str] = [ZOEITEMTAG.INFO]
        if tags is not None:
            all_tags.extend(tags)
        return ZOEITEMDATA(idx, address, ap_classification=ap_classification, tags=all_tags)


    @staticmethod
    def construct_trap(idx: int,
                       address: int = 0):
        """Construct a trap item"""
        return ZOEITEMDATA(idx, address, ap_classification=ItemClassification.trap, tags=[ZOEITEMTAG.TRAP])

    @staticmethod
    def construct_other(idx: int,
                        address: int = 0):
        """Construct some filler item"""
        return ZOEITEMDATA(idx, address, tags=[ZOEITEMTAG.FILLER])

    @staticmethod
    def construct_goal(idx: int):
        """Construct the goal item"""
        return ZOEITEMDATA(idx, ap_classification=ItemClassification.progression, tags=[ZOEITEMTAG.GOAL])

ZOE_ITEM_DATA_TABLE: dict[str, ZOEITEMDATA] = {
    # Items
    ZOEITEM.JAVELIN: ZOEITEMDATA.construct_weapon(0x00, 15, ItemClassification.useful),
    ZOEITEM.GEYSER: ZOEITEMDATA.construct_weapon(0x01, 15, ItemClassification.useful),
    ZOEITEM.BOUNDER: ZOEITEMDATA.construct_weapon(0x02, 15, ItemClassification.useful),
    ZOEITEM.PHALANX: ZOEITEMDATA.construct_weapon(0x03, 150, ItemClassification.useful),
    ZOEITEM.HALBERD: ZOEITEMDATA.construct_weapon(0x04, 15, ItemClassification.useful),
    ZOEITEM.COMET: ZOEITEMDATA.construct_weapon(0x05, 15, ItemClassification.progression),
    ZOEITEM.GAUNTLET: ZOEITEMDATA.construct_weapon(0x06, 15, ItemClassification.progression),
    ZOEITEM.SNIPER: ZOEITEMDATA.construct_weapon(0x07, 15, ItemClassification.progression),
    ZOEITEM.DECOY: ZOEITEMDATA.construct_weapon(0x08, 15, ItemClassification.progression),
    ZOEITEM.MUMMY: ZOEITEMDATA.construct_weapon(0x09, 15, ItemClassification.useful),
    # Passcodes
    ZOEITEM.PASS_JAVELIN: ZOEITEMDATA.construct_passcode(0x10),
    ZOEITEM.PASS_GEYSER: ZOEITEMDATA.construct_passcode(0x11),
    ZOEITEM.PASS_BOUNDER: ZOEITEMDATA.construct_passcode(0x12),
    ZOEITEM.PASS_PHALANX: ZOEITEMDATA.construct_passcode(0x13),
    ZOEITEM.PASS_HALBERD: ZOEITEMDATA.construct_passcode(0x14),
    ZOEITEM.PASS_COMET: ZOEITEMDATA.construct_passcode(0x15),
    ZOEITEM.PASS_GAUNTLET: ZOEITEMDATA.construct_passcode(0x16),
    ZOEITEM.PASS_SNIPER: ZOEITEMDATA.construct_unused(0x17),
    ZOEITEM.PASS_DECOY1: ZOEITEMDATA.construct_passcode(0x18, ItemClassification.progression),
    ZOEITEM.PASS_DECOY2: ZOEITEMDATA.construct_passcode(0x19, ItemClassification.progression),
    ZOEITEM.PASS_MUMMY: ZOEITEMDATA.construct_unused(0x1A),
    ZOEITEM.PASS_GLOBAL: ZOEITEMDATA.construct_passcode(0x1B, ItemClassification.progression),
    ZOEITEM.PASS_CONTROL1: ZOEITEMDATA.construct_passcode(0x1C, ItemClassification.progression),
    ZOEITEM.PASS_CONTROL2: ZOEITEMDATA.construct_passcode(0x1D, ItemClassification.progression),    
    ZOEITEM.PASS_VACCINE: ZOEITEMDATA.construct_passcode(0x1E, ItemClassification.progression),
    ZOEITEM.PASS_ANTILLIA: ZOEITEMDATA.construct_passcode(0x1F, ItemClassification.progression),
    ZOEITEM.PASS_UNUSED: ZOEITEMDATA.construct_unused(0x32),
    # Modules
    ZOEITEM.MONITOR_FCMD: ZOEITEMDATA.construct_module(0x20, ItemClassification.progression),
    ZOEITEM.GLOBAL_FCMD: ZOEITEMDATA.construct_module(0x21, ItemClassification.progression),
    ZOEITEM.RAPTR_CTRL_FCMD: ZOEITEMDATA.construct_module(0x22, ItemClassification.progression),
    ZOEITEM.DETECTOR_FCMD: ZOEITEMDATA.construct_module(0x23, ItemClassification.progression),
    ZOEITEM.VIRUS_XXXX: ZOEITEMDATA.construct_unused(0x24),
    ZOEITEM.VACCINE_EXEC: ZOEITEMDATA.construct_module(0x25, ItemClassification.progression),
    # Info 
    ZOEITEM.ANTILLIA_INFO: ZOEITEMDATA.construct_info(0x26, ItemClassification.progression),
    ZOEITEM.INFO_B_INF: ZOEITEMDATA.construct_unused(0x27),
    ZOEITEM.INFO_C_INF: ZOEITEMDATA.construct_unused(0x28),
    ZOEITEM.INFO_D_INF: ZOEITEMDATA.construct_unused(0x29),
    ZOEITEM.INFO_E_INF: ZOEITEMDATA.construct_unused(0x2A),
    ZOEITEM.INFO_F_INF: ZOEITEMDATA.construct_unused(0x2B),
    ZOEITEM.INFO_G_INF: ZOEITEMDATA.construct_unused(0x2C),
    ZOEITEM.INFO_H_INF: ZOEITEMDATA.construct_unused(0x2D),
    # Areas
    # Filler
    ZOEITEM.JEHUTY_EXP: ZOEITEMDATA.construct_other(0x2E),
    ZOEITEM.LEVEL_UP: ZOEITEMDATA.construct_other(0x2F),
    ZOEITEM.EXTRA_AMMO: ZOEITEMDATA.construct_unused(0x30),
    # Traps
    ZOEITEM.ROTATION_TRAP: ZOEITEMDATA.construct_unused(0x31),
    # Goal
    ZOEITEM.VICTORY: ZOEITEMDATA.construct_goal(0x33),
}

def from_prop(prop: str) -> filter:
    """Return a filtered item data table from a given property"""
    return filter(lambda data_kv: getattr(data_kv[1], prop) is not None, ZOE_ITEM_DATA_TABLE.items())


ITEM_FROM_AP_CODE: dict[int, str] = {kv[1].AP_CODE: kv[0] for kv in from_prop("AP_CODE")}
ITEM_NAME_FROM_ID: dict[int, str] = {kv[1].ID: kv[0] for kv in from_prop("ID")}
ITEM_NAME_FROM_ADDRESS: dict[int, str] = {kv[1].UNLOCK_ADDRESS: kv[0] for kv in from_prop("UNLOCK_ADDRESS")}


def from_tag(tag: str) -> dict[str, ZOEITEMDATA]:
    """Return a filtered item data table from a given tag"""
    return dict(filter(lambda data_kv: tag in data_kv[1].TAGS, ZOE_ITEM_DATA_TABLE.items()))

filler_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.FILLER)
goal_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.GOAL)
area_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.AREA)
passcode_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.PASSCODE)
module_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.MODULE)
info_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.INFO)
weapon_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.WEAPON)
trap_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.TRAP)
unused_data: dict[str, ZOEITEMDATA] = from_tag(ZOEITEMTAG.UNUSED)

item_counts: dict[str, int] = {
    **dict.fromkeys(weapon_data.keys(), 1),
    **dict.fromkeys(passcode_data.keys(), 1),
    **dict.fromkeys(module_data.keys(), 1),
    **dict.fromkeys(area_data.keys(), 1),
    **dict.fromkeys(info_data.keys(), 1),
    ZOEITEM.VICTORY: 0,
}
item_table: dict[str, ZOEITEMDATA] = {
    **weapon_data,
    **passcode_data,
    **module_data,
    **area_data,
    **info_data,
    **filler_data,
    **trap_data,
    **unused_data
}

item_groups: dict[str, set[str]] = {
    ZOEITEMTAG.FILLER: set(filler_data.keys()),
    ZOEITEMTAG.MODULE: set(module_data.keys()),
    ZOEITEMTAG.PASSCODE: set(passcode_data.keys()),
    ZOEITEMTAG.GOAL: set(goal_data.keys()),
    ZOEITEMTAG.INFO: set(info_data.keys()),
    ZOEITEMTAG.TRAP: set(trap_data.keys()),
    ZOEITEMTAG.UNUSED: set(unused_data.keys()),
    ZOEITEMTAG.WEAPON: set(weapon_data.keys()),
}
