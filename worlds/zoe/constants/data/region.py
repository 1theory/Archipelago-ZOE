"""This module contains the dataclass for levels in the game and exportable constants"""
from dataclasses import dataclass

from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.region import ZOEREGION, AREA_NAME_FROM_ID
from worlds.zoe.constants.status import ZOESTATUS

@dataclass
class ZOEREGIONDATA:
    """Data class for each level of the game"""
    ID: int

    def __init__(self,
                 idx: int):
        self.ID: int = idx

    @staticmethod
    def construct_area(idx: int):
        """
        Generic area constructor, makes each area into region data given the data in the ZOE_REGION_DATA_TABLE
        """
        name = AREA_NAME_FROM_ID[idx]
        return ZOEREGIONDATA(idx)

ZOE_REGION_DATA_TABLE: dict[str, ZOEREGIONDATA] = {
    # Regions
    ZOEREGION.GLOBAL_HUB: ZOEREGIONDATA.construct_area(0x01),
    ZOEREGION.HANGAR_1: ZOEREGIONDATA.construct_area(0x02),
    ZOEREGION.FACTORY_1: ZOEREGIONDATA.construct_area(0x03),
    ZOEREGION.TOWN_1_TEMPEST: ZOEREGIONDATA.construct_area(0x04),
    ZOEREGION.TOWN_1: ZOEREGIONDATA.construct_area(0x05),
    ZOEREGION.TOWN_2: ZOEREGIONDATA.construct_area(0x06),
    ZOEREGION.CITY_1: ZOEREGIONDATA.construct_area(0x07),
    ZOEREGION.EPS_1: ZOEREGIONDATA.construct_area(0x08),
    ZOEREGION.EPS_2: ZOEREGIONDATA.construct_area(0x09),
    ZOEREGION.CITY_2: ZOEREGIONDATA.construct_area(0x0A),
    ZOEREGION.FACTORY_2: ZOEREGIONDATA.construct_area(0x0B),
    ZOEREGION.TOWN_3: ZOEREGIONDATA.construct_area(0x0C),
    ZOEREGION.PARK_1: ZOEREGIONDATA.construct_area(0x0D),
    ZOEREGION.MOUNTAIN_1: ZOEREGIONDATA.construct_area(0x0E),
    ZOEREGION.MOUNTAIN_1_NEBULA: ZOEREGIONDATA.construct_area(0x0F),
    ZOEREGION.WAREHOUSE_1: ZOEREGIONDATA.construct_area(0x10),
    ZOEREGION.TUNNEL_1: ZOEREGIONDATA.construct_area(0x11),
    ZOEREGION.HUB_1: ZOEREGIONDATA.construct_area(0x12),
    ZOEREGION.VR_TRAINING: ZOEREGIONDATA.construct_area(0x13),
    ZOEREGION.ATLANTIS_1: ZOEREGIONDATA.construct_area(0x14),
    ZOEREGION.MENU: ZOEREGIONDATA(0x00),
    ZOEREGION.ENEMYCOUNT: ZOEREGIONDATA(0x00),
    ZOEREGION.SQUAD: ZOEREGIONDATA(0x00),
}
AREA_FROM_ITEM: dict[str, str] = {
    ZOEITEM.GLOBAL_HUB: ZOEREGION.GLOBAL_HUB,
    ZOEITEM.HANGAR_1: ZOEREGION.HANGAR_1,
    ZOEITEM.FACTORY_1: ZOEREGION.FACTORY_1,
    ZOEITEM.TOWN_1: (ZOEREGION.TOWN_1, ZOEREGION.TOWN_1_TEMPEST),
    ZOEITEM.TOWN_2: ZOEREGION.TOWN_2,
    ZOEITEM.CITY_1: ZOEREGION.CITY_1,
    ZOEITEM.EPS_1: ZOEREGION.EPS_1,
    ZOEITEM.EPS_2: ZOEREGION.EPS_2,
    ZOEITEM.CITY_2: ZOEREGION.CITY_2,
    ZOEITEM.FACTORY_2: ZOEREGION.FACTORY_2,
    ZOEITEM.TOWN_3: ZOEREGION.TOWN_3,
    ZOEITEM.PARK_1: ZOEREGION.PARK_1,
    ZOEITEM.MOUNTAIN_1: (ZOEREGION.MOUNTAIN_1, ZOEREGION.MOUNTAIN_1_NEBULA, ZOEREGION.WAREHOUSE_1, ZOEREGION.TUNNEL_1, ZOEREGION.HUB_1),
 #   ZOEITEM.WAREHOUSE_1: ZOEREGION.WAREHOUSE_1,
 #   ZOEITEM.TUNNEL_1: ZOEREGION.TUNNEL_1,
 #   ZOEITEM.HUB_1: ZOEREGION.HUB_1,
}