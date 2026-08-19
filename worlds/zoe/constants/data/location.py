"""This module contains the Location dataclass"""

from dataclasses import dataclass

from worlds.zoe.constants.check_type import CHECKTYPE
from worlds.zoe.constants.data.address import ZOEADDRESSDATA
from worlds.zoe.constants.data.region import ZOE_REGION_DATA_TABLE
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.locations.tags import ZOETAG
from worlds.zoe.constants.progress_flag import ZOEPROGRESSFLAG
from worlds.zoe.constants.region import ZOEREGION
from worlds.zoe.constants.status import ZOESTATUS

_LOCATION_NAME_TO_ID: dict[str, int] = {
    ZOELOCATION.HANGAR_1_FIRST_RAPTOR: 0,
    ZOELOCATION.FACTORY_1_NEITH: 1,
    ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER: 2,
    ZOELOCATION.FACTORY_1_GLOBAL_PASSCODE: 3,
    ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER: 4,
    ZOELOCATION.FACTORY_1_FLY_AWAY: 5,
    ZOELOCATION.TOWN_1_TEMPEST: 6,
}
_LOCATION_NAME_TO_SECTION: dict[str, int] = {
    ZOELOCATION.HANGAR_1_FIRST_RAPTOR: 0,
    ZOELOCATION.FACTORY_1_NEITH: 0,
    ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER: 1,
    ZOELOCATION.FACTORY_1_GLOBAL_PASSCODE: 2,
    ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER: 3,
    ZOELOCATION.FACTORY_1_FLY_AWAY: 3,
    ZOELOCATION.TOWN_1_TEMPEST: 0,
}

_LOCATION_NAME_TO_REGION: dict[str, str] = {
    ZOELOCATION.HANGAR_1_FIRST_RAPTOR: ZOEREGION.HANGAR_1,
    ZOELOCATION.FACTORY_1_NEITH: ZOEREGION.FACTORY_1,
    ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER: ZOEREGION.FACTORY_1,
    ZOELOCATION.FACTORY_1_GLOBAL_PASSCODE: ZOEREGION.FACTORY_1,
    ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER: ZOEREGION.FACTORY_1,
    ZOELOCATION.FACTORY_1_FLY_AWAY: ZOEREGION.FACTORY_1,
    ZOELOCATION.TOWN_1_TEMPEST: ZOEREGION.TOWN_1_TEMPEST,
}
_LOCATION_NAME_TO_TAG: dict[str, set[str]] = {
    ZOELOCATION.HANGAR_1_FIRST_RAPTOR: {ZOETAG.ENEMY},
    ZOELOCATION.FACTORY_1_NEITH: {ZOETAG.MISSIONS},
    ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER: {ZOETAG.LOCAL_SERVERS},
    ZOELOCATION.FACTORY_1_GLOBAL_PASSCODE: {ZOETAG.PASSCODES},
    ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER: {ZOETAG.LOCAL_SERVERS},
    ZOELOCATION.FACTORY_1_FLY_AWAY: {ZOETAG.MISSIONS},
    ZOELOCATION.TOWN_1_TEMPEST: {ZOETAG.ENEMY},
#    ZOELOCATION.HUB_ANUBIS: set(),
}

_LOCATION_NAME_TO_ADDRESS: dict[str, set[tuple[int, CHECKTYPE, int]]] = {
    ZOELOCATION.HANGAR_1_FIRST_RAPTOR: {(ZOESTATUS.TOTAL_ENEMIES_DESTROYED, CHECKTYPE.BYTE, 0x01)},
    ZOELOCATION.FACTORY_1_NEITH: {(0x0048EF10, CHECKTYPE.BYTE_GE, 0x02)},
    ZOELOCATION.FACTORY_1_SCOUTING_MODULE_LOCAL_SERVER: {(0x0048EF25, CHECKTYPE.BIT, 2), (ZOESTATUS.STAND_BY_STATE, CHECKTYPE.BYTE, 0x01)},
    ZOELOCATION.FACTORY_1_GLOBAL_PASSCODE: {(0x0048EF1D, CHECKTYPE.BIT, 2)},
    ZOELOCATION.FACTORY_1_FLIGHT_MODULE_LOCAL_SERVER: {(0x0048EF25, CHECKTYPE.BIT, 3), (ZOESTATUS.STAND_BY_STATE, CHECKTYPE.BYTE, 0x01)},
    ZOELOCATION.FACTORY_1_FLY_AWAY: {(0x0048EF10, CHECKTYPE.BYTE_GE, 0x04)},
    ZOELOCATION.TOWN_1_TEMPEST: {(0x0048EF10, CHECKTYPE.BYTE_GE, 0x05)},
}

UT_MAPPING: dict[str, int] = {}

@dataclass
class ZOELOCATIONDATA:
    """Data class for each location"""
    ID: int = 0
    REGION: str = ZOEREGION.MENU
    CHECK_ADDRESS: list[ZOEADDRESSDATA] = None
    AP_CODE: int = None
    TAGS: set[str] = None

    def __init__(self,
                 idx: int,
                 region: str = ZOEREGION.MENU,
                 check: list[ZOEADDRESSDATA] | None = None,
                 tags: set[str] | None = None):
        self.ID = idx
        self.REGION = region
        self.CHECK_ADDRESS = check if check else []
        self.AP_CODE = idx + ZOESTATUS.APCODE
        self.TAGS = tags if tags else set()

    @staticmethod
    def construct(location_name: str):
        """Construct the given location data for the location data table"""
        area_name: str = _LOCATION_NAME_TO_REGION[location_name]
        area_id: int = ZOE_REGION_DATA_TABLE[area_name].ID
        loc_id: int = _LOCATION_NAME_TO_ID[location_name]
        tags: set[str] = set(_LOCATION_NAME_TO_TAG[location_name])
        if area_id:
            section_id: int = _LOCATION_NAME_TO_SECTION[location_name]
            UT_MAPPING[f"{area_id}/{loc_id}"] = loc_id + ZOESTATUS.APCODE
            UT_MAPPING[f"{section_id}/{loc_id}"] = loc_id + ZOESTATUS.APCODE
            tags.union({area_name})
        check: list[ZOEADDRESSDATA] = []
        for item in _LOCATION_NAME_TO_ADDRESS[location_name]:
            check += [ZOEADDRESSDATA(item)]
        return ZOELOCATIONDATA(loc_id, area_name, check, tags)


ZOE_LOCATION_DATA_TABLE: dict[str, ZOELOCATIONDATA] = {name: ZOELOCATIONDATA.construct(name) for name in
                                                         _LOCATION_NAME_TO_REGION.keys()}
LOCATION_FROM_AP_CODE: dict[int, str] = {kv[1].AP_CODE: kv[0] for kv in ZOE_LOCATION_DATA_TABLE.items()}
