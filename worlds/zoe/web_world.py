"""This module contains the Webpage World class for Ratchet and Clank 3"""
from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.zoeoptions import zoe_option_groups


class ZoeWeb(WebWorld):
    theme = "ocean"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        f"A guide to setting up {ZOEOPTION.GAME_TITLE_FULL} for Archipelago. "
        "This guide covers single-player, multiworld, and related software.",
        "English",
        "setup_en.md",
        "setup/en",
        ["1theory"]
    )]
    bug_report_page = "https://github.com/1theory/Archipelago-ZOE/issues"
    rich_text_options_doc = True
    option_groups = zoe_option_groups
