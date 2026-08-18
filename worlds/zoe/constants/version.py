"""This module contains the constant strings used to determine which version of ZOE is being played"""


class ZOEVERSION:
    """Constant Strings for the ID of each known version of ZOE"""
    US_ID = "SLUS-20148"
    JP_ID = "SLPM-65019"
    JP_PP_ID = "SLPM-65018"
    JP_TB_ID = "SLPM-65237"
    EU_ID = "SLES-50111"

GAME_ID_TO_VERSION: dict[str, str] = {
    ZOEVERSION.US_ID: "US release",
    ZOEVERSION.JP_ID: "Japanese release",
    ZOEVERSION.JP_PP_ID: "Japanese Premium Package release",
    ZOEVERSION.JP_TB_ID: "Japanese The Best release",
    ZOEVERSION.EU_ID: "EU release",
}