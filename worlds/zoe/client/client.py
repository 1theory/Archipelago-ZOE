"""This module provides a launchable client for connecting ZOE running on PCSX2 Emulation to a Multiworld"""
from asyncio import create_task, run, sleep, Task
from multiprocessing import freeze_support
from time import time

import Utils
from CommonClient import get_base_parser, gui_enabled, logger, server_loop
from NetUtils import NetworkItem
from Utils import Any, async_start, init_logging
from worlds.zoe.client.callbacks import pcsx2_sync_task, update
from worlds.zoe.client.message import ClientMessage
from worlds.zoe.client.zoe_interface import ZoeInterface
from worlds.zoe.constants.check_type import CHECKTYPE
from worlds.zoe.constants.data.address import SAVE_DATA
from worlds.zoe.constants.data.item import ZOE_ITEM_DATA_TABLE
from worlds.zoe.constants.data.region import ZOE_REGION_DATA_TABLE
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.region import ZOEREGION

# Load Universal Tracker modules with aliases
tracker_loaded: bool = False
try:
    # noinspection PyUnusedImports
    from worlds.tracker.TrackerClient import (TrackerCommandProcessor as ClientCommandProcessor,
                                              TrackerGameContext as CommonContext, UT_VERSION)

    tracker_loaded = True
except ImportError:
    from CommonClient import ClientCommandProcessor, CommonContext

    print("ERROR: Universal Tracker is not loaded")

class CommandProcessor(ClientCommandProcessor):
    def verify(self, level: int = 4) -> bool:
        """
        Checks various levels of connection before allowing a command.
        Level 1: Client is for ZOE
        Level 2: Client is connected to a multiworld server
        Level 3: Client is connected to the game
        Level 4: Player is in game
        """
        if isinstance(self.ctx, ZoeContext):
            if level == 1:
                return True
            if self.ctx.slot_data:
                if level == 2:
                    return True
                if self.ctx.is_connected_to_game:
                    if level == 3:
                        return True
                    if not self.ctx.main_menu:
                        return True
                    self.output("Not in game, please load a game file")
                    return False
                self.output(f"No Game Detected, please connect to {ZOEOPTION.GAME_TITLE_FULL}")
                return False
            self.output("No slot data, please connect to a multiworld server")
            return False
        self.output(f"Somehow this client isn't for {ZOEOPTION.GAME_TITLE_FULL}, delete this build and try again")
        return False

    @staticmethod
    def is_development_build() -> bool:
        """Checks if this is a development build by looking for -dev or a subversion."""
        return "-dev" in ZOEOPTION.VERSION_NUMBER or ZOEOPTION.VERSION_NUMBER.count(".") >= 3

    # This is not mandatory for the game. Just a client command implementation.
    def _cmd_kill(self):
        """Kill the player."""
        if not self.verify():
            return
        if isinstance(self.ctx, ZoeContext):
            if self.ctx.death_link:
                self.ctx.on_deathlink({"time": time(), "cause": "Amondo got gaslit", "source": "Amondo"})
            else:
                self.output("Death Link is not enabled. You can toggle Death Link with /deathlink")

    def _cmd_connect_zoe(self):
        """Attempt to connect the client to the emulator"""
        if not self.verify(1):
            return
        if isinstance(self.ctx, ZoeContext):
            if self.ctx.game_interface.get_connection_state():
                self.output("Already Connected to Emulator")
            else:
                self.ctx.game_interface.connect_to_game()

    def _cmd_zoe_info(self):
        """Dump Zoe info for debugging purposes."""
        if not self.verify():
            return
        if isinstance(self.ctx, ZoeContext):
            self.ctx.game_interface.dump_info(self.ctx.slot_data)

class ZoeContext(CommonContext):
    """Class for handling server connection with the game client"""
    # Client variables
    uuid: str
    already_hinted: set[int] = set()
    command_processor = CommandProcessor
    current_area: str = ZOEREGION.MENU
    death_link: bool = False
    game: str = ZOEOPTION.GAME_TITLE_FULL
    game_interface: ZoeInterface
    is_connected_to_game: bool = False
    is_connected_to_server: bool = False
    items_handling: int = 0b111  # This is mandatory
    last_game_message: str | None = None
    last_pine_message: str | None = None
    last_server_message: str | None = None
    main_menu: bool = True
    pcsx2_sync_task: Task | None = None
    processed_item_count: int = 0
    queued_deaths: int = 0
    slot_data: dict[str, Any] | None = None
    last_deathlink_msg: str | None = None
    last_deathlink_sender: str | None = None
    #code_cave_setup: bool = False
    data_package: int = 0
    data_received: bool = False
    save_data: dict[int, tuple[int, int]] = {}

    def __init__(self, server_address: str, password: str):
        super().__init__(server_address, password)
        self.game_interface = ZoeInterface()
        self.uuid = Utils.get_unique_identifier()
        self.save_data = {data.ADDRESS: (data.TYPE, data.VALUE) for data in SAVE_DATA}

    def on_deathlink(self, data: dict[str, Any]) -> None:
        text = data.get("cause", "")
        if text:
            logger.info(f"Death Link: {text}")
        else:
            logger.info(f"Death Link: Received from {data['source']}")
        if self.death_link:
            self.queued_deaths += 1
            self.last_deathlink_msg = text if text else "???"
            self.last_deathlink_sender = data.get("source", "???")

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = f"{ZOEOPTION.GAME_TITLE} Client v{ZOEOPTION.VERSION_NUMBER}"
        if tracker_loaded:
            ui.base_title += f" | Universal Tracker {UT_VERSION}"

        # AP version is added behind this automatically
        ui.base_title += " | Archipelago"
        return ui

    async def server_auth(self, password_requested: bool = False) -> None:
        """Authenticate with the Multiworld server."""
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "Connected":
            self.slot_data: dict[str, Any] = args["slot_data"]
            logger.info(f"Received data: {args}")
            self.game_interface.proc_option(self.slot_data)
            self.locations_scouted = self.server_locations
            self.code_cave_setup = False
            async_start(self.send_msgs([ClientMessage.location_scouts(list(self.server_locations))]))
            async_start(self.send_msgs([{"cmd": "GetDataPackage", "games": [ZOEOPTION.GAME_TITLE_FULL]}]))
            self.data_received = False
            async_start(self.send_msgs([ClientMessage.get_save(self.uuid)]))
            logger.debug(f"Requested Save Data on Connection")
            # Set death link tag if it was requested in options
            if ZOEOPTION.DEATHLINK in self.slot_data:
                if self.slot_data[ZOEOPTION.DEATHLINK]:
                    self.death_link = bool(self.slot_data[ZOEOPTION.DEATHLINK])
                    async_start(self.update_death_link(self.death_link))

        if cmd == "DataPackage":
            logger.debug(f"Data Package received with args {args}")
            if ZOEOPTION.GAME_TITLE_FULL in args["data"]["games"]:
                self.data_package = args["data"]["games"][ZOEOPTION.GAME_TITLE_FULL]
                logger.debug(f"Data Package updated: {self.data_package}")
                async_start(self.send_msgs([{"cmd": "Sync"}]))

        if cmd == "Retrieved":
            logger.debug(f"{cmd} server packet: {args}")
            if args["keys"]:
                if f"{self.uuid}_save_data" in args["keys"]:
                    logger.debug(f"Save Data recieved")
                    self.data_received = True
                    if args["keys"][f"{self.uuid}_save_data"]:
                        logger.debug(f"Valid Save data from Server {args['keys'][f'{self.uuid}_save_data']}")
                        for address, data in args["keys"][f"{self.uuid}_save_data"].items():
                            self.save_data.update({int(address): (CHECKTYPE(data[0]), data[1])})
                        if self.is_connected_to_game and not self.main_menu:
                            self.game_interface.load_save(self.save_data)
                            self.game_interface.process_offline_fillers(self.data_received)

        if cmd == "SetReply":
            logger.debug(f"{cmd} server packet: {args}")
            if args["key"]:
                if f"{self.uuid}_save_data" == args["key"]:
                    logger.debug(f"Save Data recieved by the server")
                    self.data_received = True


def launch_client():
    """Launch an instance of the Zone of the Enders client"""
    init_logging(f"{ZOEOPTION.GAME_TITLE}_Client")

    async def main():
        """The main client process"""
        freeze_support()
        logger.info("main")
        parser = get_base_parser()
        args = parser.parse_args()
        ctx = ZoeContext(args.connect, args.password)

        logger.info("Connecting to server...")
        ctx.server_task = create_task(server_loop(ctx), name="Server Loop")

        # Runs Universal Tracker's internal generator
        if tracker_loaded:
            ctx.run_generator()
            ctx.tags.remove("Tracker")
        else:
            logger.warning("Could not find Universal Tracker.")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        logger.info("Running game...")
        ctx.pcsx2_sync_task = create_task(pcsx2_sync_task(ctx), name="PCSX2 Sync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.pcsx2_sync_task:
            await sleep(3)
            await ctx.pcsx2_sync_task

    import colorama

    colorama.init()

    run(main())
    colorama.deinit()


if __name__ == "__main__":
    launch_client()