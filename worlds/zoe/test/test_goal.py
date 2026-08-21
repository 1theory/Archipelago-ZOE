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
        self.assertFalse(self.can_reach_region(ZOEREGION.TOWN_1_TEMPEST), "TOWN.1.TEMPEST reachable from HANGAR.1")
        self.assertFalse(self.can_reach_location(ZOELOCATION.TOWN_1_TEMPEST),
                         "Goal location reachable from Start")
        self.assertBeatable(False)

        state.sweep_for_advancements()
        self.assertFalse(self.can_reach_region(ZOEREGION.TOWN_1_TEMPEST), "TOWN.1.TEMPEST reachable from FACTORY.1")
        self.assertFalse(self.can_reach_location(ZOELOCATION.TOWN_1_TEMPEST),
                         "Goal location reachable from FACTORY.1")
        self.assertBeatable(False)

        self.collect_by_name(ZOEITEM.TOWN_1)
        self.assertTrue(self.can_reach_region(ZOEREGION.TOWN_1_TEMPEST), "Can't reach TOWN.1.TEMPEST")
        self.assertFalse(self.can_reach_location(ZOELOCATION.TOWN_1_TEMPEST),
                         "Goal location reachable with no items")
        self.assertBeatable(False)