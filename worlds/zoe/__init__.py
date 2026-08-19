"""This package contains the apworld implementation for Zone of the Enders for the PlayStation 2"""
from logging import DEBUG, getLogger
from typing import Optional

from worlds.LauncherComponents import Component, components, icon_paths, launch_subprocess, SuffixIdentifier, Type
from worlds.zoe.constants.options import ZOEOPTION
# noinspection PyUnusedImports
from worlds.zoe.world import ZoeWorld


def run_client(_url: Optional[str] = None):
    """Launch the client for connecting to Zoe"""
    from worlds.zoe.client.client import launch_client
    launch_subprocess(launch_client, name=f"{ZOEOPTION.GAME_TITLE}Client")


components.append(Component(f"{ZOEOPTION.GAME_TITLE_FULL} Client",
                            func=run_client,
                            component_type=Type.CLIENT,
                            file_identifier=SuffixIdentifier(".apzoe"),
                            icon="zoe_icon",
                            description="Launch the Client for connecting to Zone of the Enders [PlayStation 2]",
                            ))

icon_paths["zoe_icon"] = f"ap:{__name__}/images/zoe_icon.png"

zoe_logger = getLogger(ZOEOPTION.GAME_TITLE_FULL)
zoe_logger.setLevel(DEBUG)
