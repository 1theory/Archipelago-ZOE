"""This package provides UnitTesting for the Zoe apworld"""

from test.bases import WorldTestBase
from worlds.zoe.constants.options import ZOEOPTION
from ..world import ZoeWorld


class ZOETestBase(WorldTestBase):
    game = ZOEOPTION.GAME_TITLE_FULL
    world: ZoeWorld
