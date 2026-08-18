"""This module contains functions related to the game client"""
from asyncio import sleep
from time import time
from traceback import format_exc
from typing import TYPE_CHECKING

from CommonClient import logger
from NetUtils import ClientStatus
from worlds.zoe.client.message import ClientMessage
from worlds.zoe.constants.data.location import ZOE_LOCATION_DATA_TABLE
from worlds.zoe.constants.data.region import ZOE_REGION_DATA_TABLE
from worlds.zoe.constants.items import ZOEITEM
from worlds.zoe.constants.options import ZOEOPTION
from worlds.zoe.constants.region import ZOEREGION

if TYPE_CHECKING:
    from worlds.zoe.client.client import ZoeContext as Context

async def pcsx2_sync_task(ctx: "Context"):
    """Connects to PCSX2 and loops through update functions until the connection is closed."""
    logger.info(f"Starting {ZOEOPTION.GAME_TITLE_FULL} Connector")
    version_dots = ZOEOPTION.VERSION_NUMBER.count(".")
    if version_dots >= 3 or "dev" in ZOEOPTION.VERSION_NUMBER:
        logger.warning("\nYou are using a development build of the Zone of the Enders Archipelago Randomizer!\n"
                       "There may be bugs present and features that have not been tested fully.\n"
                       "These builds are meant for testing and bug reporting purposes "
                       "and should not be used for normal play!\n")
    connected_to_game: bool = False
    connection_retry_attempts: int = 0
    correct_version: bool = True
    while not ctx.exit_event.is_set():
        try:
            connected_to_server = (ctx.server is not None) and (ctx.slot is not None)
            if connected_to_server and not ctx.is_connected_to_server:
                if ctx.slot_data:
                    logger.info("Connected to server")
                    ctx.is_connected_to_server = connected_to_server
                    if ctx.slot_data.get(ZOEOPTION.VERSION, "0.0.0") < ZOEOPTION.VERSION_NUMBER:
                        await ctx.disconnect()
                        correct_version = False
                        logger.warning(
                            f"Client is v{ZOEOPTION.VERSION_NUMBER}, please downgrade to v"
                            f"{ctx.slot_data[ZOEOPTION.VERSION]}")
                        await sleep(10)
                        continue
                    if ctx.slot_data[ZOEOPTION.VERSION] > ZOEOPTION.VERSION_NUMBER:
                        await ctx.disconnect()
                        correct_version = False
                        logger.warning(
                            f"Client is v{ZOEOPTION.VERSION_NUMBER}, please upgrade to v"
                            f"{ctx.slot_data[ZOEOPTION.VERSION]}")
                        await sleep(10)
                        continue
                    if connected_to_game:
                        ctx.game_interface.init()
                    else:
                        logger.info("Waiting for game connection...")

            connected_to_game = ctx.game_interface.get_connection_state()
            if connected_to_game and not ctx.is_connected_to_game:
                logger.info(f"Connected to {ZOEOPTION.GAME_TITLE_FULL}")
                ctx.last_pine_message = None
                ctx.is_connected_to_game = connected_to_game
                if connected_to_server:
                    ctx.game_interface.init()
                else:
                    logger.info("Waiting for server connection...")

            if not connected_to_game and not ctx.game_interface.is_connecting:
                if ctx.is_connected_to_game:
                    ctx.game_interface.disconnect_from_game()
                    logger.info("Connection to game lost")
                elif ctx.last_pine_message is None:
                    message = "Not connected to the PCSX2 instance"
                    ctx.game_interface.emulator_connected = False
                    logger.info(message)
                    ctx.last_pine_message = message
                ctx.game_interface.connect_to_game()
                if not ctx.game_interface.get_connection_state():
                    if connection_retry_attempts < 3:
                        connection_retry_attempts += 1

                    retry_wait = connection_retry_attempts * 10
                    if ctx.game_interface.emulator_connected:
                        connection_retry_attempts = 0
                        retry_wait = 10
                        logger.warning(
                            f"Could not connect to Zoe! Will retry connection in {retry_wait} seconds...\nEmulator "
                            f"already connected. Please launch Zoe.")
                    else:
                        logger.warning(
                            f"Could not connect to Zoe! Will retry connection in {retry_wait} seconds...\nPlease "
                            f"check your PINE settings both global and game specific, and restart PCSX2 if you "
                            f"changed them.")
                    await sleep(retry_wait)
                else:
                    connection_retry_attempts = 0

            if not connected_to_server:
                if ctx.server:
                    ctx.last_server_message = None
                elif ctx.last_server_message is None:
                    message = "Waiting for player to connect to server"
                    logger.info(message)
                    ctx.last_server_message = message

            if connected_to_game and connected_to_server and correct_version:
                await _handle_game_ready(ctx)

        except ConnectionError:
            logger.info("ConnectionError")
            ctx.game_interface.disconnect_from_game()
        except Exception as e:
            logger.info("ExceptionError")
            if isinstance(e, RuntimeError):
                logger.error(str(e))
            else:
                logger.error(format_exc())
            # await sleep(3)

        await sleep(0.1)
    logger.info(f"{ZOEOPTION.GAME_TITLE_FULL} Client Shutdown")


async def _handle_game_ready(ctx: "Context") -> None:
    # Quite a lot of stuff ended up in this function, even though it might
    # have fit better in init(). It just didn't work when I put it there,
    # probably because of when the game loads stuff.

    if ctx.slot_data is not None and ctx.slot is not None:
        # Check if exit to main menu
        menu = ctx.main_menu
        ctx.main_menu = ctx.game_interface.check_main_menu()

        if ctx.main_menu:
            if menu:
                ctx.game_interface.main_menu = True
            if ctx.last_game_message is None:
                message = "Currently on Main Menu, please load a file..."
                logger.info(message)
                ctx.last_game_message = message
            await sleep(5)

        if menu is True and ctx.main_menu is False:
            ctx.last_game_message = None
            await ctx.send_msgs([ClientMessage.status_update(ClientStatus.CLIENT_PLAYING)])
            logger.info("Starting game...")
            ctx.game_interface.reset_file()
            logger.info("Old state removed!")
            logger.info("Checking for items...")
            logger.debug(f"Data Package: {ctx.stored_data.get(ZOEOPTION.PROCESSED_LOCATIONS, 'Empty')}")
            logger.info(f"Items Received: {len(ctx.items_received)}")
            items_to_process = ctx.stored_data.get(ZOEOPTION.PROCESSED_LOCATIONS, len(ctx.items_received))
            ctx.game_interface.initial_fillers.clear()
            counter = 0
            for count, item in enumerate(ctx.items_received):
                counter += 1
                logger.debug(f"Processing item {count}: {ctx.item_names.lookup_in_slot(item.item, item.player)}")
                if count > items_to_process:
                    logger.debug("Handle Later")
                    continue
                ctx.game_interface.important_items(item.item, ctx.player_names[ctx.slot], item.location)
                ctx.game_interface.filler_items(item.item)
            ctx.processed_item_count = min(counter, items_to_process)
            await ctx.send_msgs([ClientMessage.set_processed(ctx.processed_item_count)])
            logger.info(f"Items Processed: {ctx.processed_item_count}")
            logger.info("Checking locations...")
            checks = set()
            for loc in ctx.checked_locations:
                logger.debug(f"Collecting location: {ctx.location_names.lookup_in_slot(loc, ctx.slot)}")
                checks.add(ctx.location_names.lookup_in_slot(loc, ctx.slot))
            counter = len(ctx.game_interface.collect_locations(checks))
            logger.info(f"Locations collected: {counter}")
            logger.info("Updating save data...")
            ctx.game_interface.load_save(ctx.save_data)
            ctx.game_interface.init_stored_fillers()
            ctx.game_interface.process_offline_fillers(ctx.data_received)
            ctx.game_interface.reset_death_count()
            ctx.game_interface.setup_settings()
#            logger.info("Setting up codecave...")
#            ctx.code_cave_setup = False
#            await handle_codecave(ctx)
            logger.info("Game READY! Credits to: Taoshi, Myth197 and yuxia228 for putting together the code that I based this client on.")

        if not ctx.main_menu:
            ctx.game_interface.cycle_reads_count = 0
            ctx.game_interface.cycle_writes_count = 0
            ctx.game_interface.cycle_cache.clear()
            current_time = time()
            await update(ctx)
            after_time = time()
            elapsed = after_time - current_time
            logger.debug(f"Update cycle took {elapsed:.5f} seconds (Reads: {ctx.game_interface.cycle_reads_count}, "
                         f"Writes: {ctx.game_interface.cycle_writes_count})")
            # logger.debug(f"Data Package: {ctx.stored_data.get(ZOEOPTION.PROCESSED_LOCATIONS, 'Empty')}")
            ctx.game_interface.cycle_times.append(elapsed)
            if len(ctx.game_interface.cycle_times) > 100:
                ctx.game_interface.cycle_times.pop(0)


##################################################
# Only change point: Change filename/Class name  #
##################################################


# common functions
async def update(ctx: "Context") -> None:
    """Called continuously"""
    ctx.game_interface.early_update()
    # Check codecave and set values if needed
#    await handle_codecave(ctx)
    # Check received items
    await handle_received_items(ctx)
    # Check collected locations
    await handle_checked_locations(ctx)
    # Check player dead or not
    await handle_deathlink(ctx)
    # Check goal is checked or not
    await handle_check_goal(ctx)
    # Check area id
    await handle_area_changed(ctx)
    # Check sequence breaks
    await handle_sequence_break(ctx)
    ctx.game_interface.late_update()
    # Save to the server
    await handle_save(ctx)
    # logger.info(f"Update is called")

async def handle_received_items(ctx: "Context") -> None:
    """Process items received from the AP server"""
    if ctx.slot_data is None or ctx.slot is None:
        return

    # 初回だけ記録用に items_received の長さを記憶しておく
    for item in ctx.items_received[ctx.processed_item_count:]:
        ctx.game_interface.item_received(item.item, ctx.player_names[ctx.slot], ctx.player_names[item.player],
                                         item.location)
        # logger.info(f"Received item: ({item_id})")

    if ctx.processed_item_count != len(ctx.items_received):
        logger.debug(f"Update Data Package to {len(ctx.items_received)}")
        ctx.stored_data[ZOEOPTION.PROCESSED_LOCATIONS] = len(ctx.items_received)
        ctx.processed_item_count = len(ctx.items_received)
        await ctx.send_msgs([ClientMessage.set_processed(ctx.processed_item_count)])


async def handle_checked_locations(ctx: "Context") -> None:
    """Check for new locations collected, send these to the AP server"""
    if ctx.slot_data is None:
        return

    # logger.info(f"{ctx.server_locations}")
    new_checks = []
    for ap_code in ctx.server_locations:
        if ap_code in ctx.checked_locations | ctx.locations_checked:
            continue
        if ctx.game_interface.is_location_checked(ap_code):
            new_checks.append(ap_code)

    if new_checks:
        real_checks = list(await ctx.check_locations(new_checks))
        ctx.locations_checked.update(real_checks)
        for location in real_checks:
            net_item = ctx.locations_info.get(location, None)
            if net_item is not None and net_item.player != ctx.slot:
                return
#                item_to_player_names = get_sent_item_message(ctx, net_item, True)
#                ctx.game_interface.enqueue_notification(item_to_player_names)

    # else:
    #     logger.info("Not found new location")


async def handle_deathlink(ctx: "Context") -> None:
    """Receive and send deathlink"""
    if not ctx.death_link:
        return
    ctx.game_interface.reload_check()
    if time() - ctx.last_death_link > 10:
        alive, message = ctx.game_interface.alive()
        if alive:
            if ctx.queued_deaths > 0:
                logger.debug(f"Deaths requires processing: {ctx.queued_deaths}")
                if ctx.game_interface.kill_player():
                    logger.debug("Deaths processed")
                    ctx.queued_deaths = 0
                    ctx.last_death_link = time()
        else:
            logger.debug(f"Sending Death, queue: {ctx.queued_deaths}")
            await ctx.send_death(message)
            logger.debug(f"Sent Death, queue: {ctx.queued_deaths}")


async def handle_check_goal(ctx: "Context") -> None:
    """Checks if the goal is completed"""
    if ctx.slot_data is None:
        return

    victory_code = ctx.game_interface.get_victory_code()
    if victory_code in ctx.checked_locations and not ctx.finished_game:
        ctx.finished_game = True
        await ctx.send_msgs([ClientMessage.status_update(ClientStatus.CLIENT_GOAL)])


async def handle_area_changed(ctx: "Context") -> None:
    """Checks if the player is changing area"""
    if ctx.slot_data is None:
        return
    # Player visits a new planet/region
    if ctx.game_interface.new_area:
        return
        # Changing planet counts as a reload.


async def handle_sequence_break(ctx: "Context") -> None:
    """Undoes the flags for locations when sequence breaking if you haven't checked the corresponding location
    yet"""
    if ctx.slot_data is None:
        return
    ctx.game_interface.sequence_break()


async def handle_save(ctx: "Context") -> None:
    """Checks if any memory values need to be saved to the server"""
    if ctx.slot_data is None or ctx.slot is None:
        return
    if ctx.data_received:
        local_save = ctx.game_interface.update_save()
        # logger.debug(f"local_save : {local_save}")
        # logger.debug(f"server_save: {ctx.save_data}")
        if not (local_save == ctx.save_data):
            logger.debug("Sending new save data to server")
            ctx.data_received = False
            ctx.save_data = local_save
            await ctx.send_msgs([ClientMessage.update_save(ctx.uuid, local_save)])
    else:
        logger.debug("Waiting for save data from server")