"""This module contains UnitTesting for the Goal condition"""

from BaseClasses import CollectionState
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.locations.general import ZOELOCATION
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.region import ZOEREGION
from worlds.zoe.test import ZOETestBase

class TestTempest(ZOETestBase):
    options = {    
    }
    def test_logic(self):
        state: CollectionState = self.multiworld.state
        self.assertTrue(self.can_reach_region(ZOEREGION.HANGAR_1), "Can't start on HANGAR.1")
        self.assertTrue(self.can_reach_region(ZOEREGION.GLOBAL_HUB), "Global Hub not reachable from start")
        self.assertFalse(self.can_reach_region(ZOEREGION.HUB_1), "HUB.1 reachable from HANGAR.1")
        self.assertFalse(self.can_reach_location(ZOELOCATION.FLOWING_DESTINY),
                         "Goal location reachable from Start")
        self.assertBeatable(False)

        state.sweep_for_advancements()
        self.assertFalse(self.can_reach_region(ZOEREGION.HUB_1), "HUB.1 reachable from FACTORY.1")
        self.assertFalse(self.can_reach_location(ZOELOCATION.FLOWING_DESTINY),
                         "Goal location reachable from FACTORY.1")
        self.assertBeatable(False)

        self.collect_by_name(ZOEITEM.MOUNTAIN_1)
        self.assertTrue(self.can_reach_region(ZOEREGION.MOUNTAIN_1), "Can't reach MOUNTAIN.1")
        self.assertFalse(self.can_reach_location(ZOELOCATION.FLOWING_DESTINY),
                         "Goal location reachable with no items")
        self.assertBeatable(False)

        self.collect_by_name([ZOEITEM.MONITOR_FCMD, ZOEITEM.GLOBAL_FCMD, ZOEITEM.SNIPER, ZOEITEM.VACCINE_EXEC, ZOEITEM.RAPTR_CTRL_FCMD, ZOEITEM.DECOY, ZOEITEM.DETECTOR_FCMD])
        self.assertTrue(self.can_reach_location(ZOELOCATION.HUB_1_NOT_DESTINED_TO_MEET_YET),
                        "Goal location not reachable with items")
        self.assertBeatable(True)
        