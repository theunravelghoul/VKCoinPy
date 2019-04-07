import asyncio
import json
import logging
from queue import Queue

import js2py
import websockets

from core.enums import ResponseMessageTypes, ItemTypes
from core.helpers import calculate_pow
from core.locale import _
from core.message_generators import RequestMessageGenerator
from .logger import Logger

logger = logging.getLogger(__file__)


class BotMessenger(object):
    WAIT_FOR_MESSAGE_TIMEOUT_BEFORE_PLAYER_INIT = 2.0
    WAIT_FOR_MESSAGE_TIMEOUT = 20.0
    QUEUE_SLEEP_TIME = 1.0
    PLAYER_INIT_RETRY_INTERVAL = 1.0
    TICK_MESSAGE_SEND_INTERVAL = 1.0

    def __init__(self, server_url, bot):
        self.server_url = server_url
        self.bot = bot

        self.event_loop = asyncio.get_event_loop()

        self.received_messages_queue = Queue()
        self.pending_messages_queue = Queue()

        self.messages_sent = 0
        self.tick_message_response_received = True
        self.random_id = None
        self.player_initialized = False

        self.on_start_user_output_send = False

        self.disconnect_required = False
        self.reconnect_required = False

        self.connection = None
        self.connected = False

    async def _connect(self) -> None:
        logger.debug("Connecting to the VK Coin app server")
        self.connection = await websockets.connect(self.server_url)
        self.connected = True
        logger.debug("Connection established")

    async def _disconnect(self) -> None:
        logger.debug("Disconnecting from the VK Coin app server")
        await self.connection.close()
        self.connected = False
        logger.debug("Connection closed")

    async def _require_disconnect(self, reconnect=True) -> None:
        self.disconnect_required = True
        self.reconnect_required = reconnect

    async def _wait_for_message(self):
        message = await self.connection.recv()
        self.received_messages_queue.put(message)

    async def send_message(self, message):
        self.pending_messages_queue.put(message)

    async def _player_initialized(self):
        self.player_initialized = True
        self.event_loop.create_task(self._send_tick_messages())
        self.event_loop.create_task(self._run_auto_actions())

    async def _process_received_message(self, message: str) -> None:
        try:
            message_json = json.loads(message)
            message_type = message_json.get('type')
            if message_type:
                if message_type == ResponseMessageTypes.INIT:
                    await self._handle_init_message(message_json)
        except json.JSONDecodeError:
            if ResponseMessageTypes.TRANSFER in message:
                await self._handle_transfer_message(message)
                return
            if message[0] == "C" and "items" in message:
                message_body = ' '.join(message.split(' ')[1::])
                message_body_json = json.loads(message_body)
                await self._handle_item_bought_message(message_body_json)
                return
            if ResponseMessageTypes.BROKEN in message:
                await self._handle_broken_message()
                return
            if ResponseMessageTypes.MISS in message:
                await self._handle_missed_message()
                return
            if ResponseMessageTypes.SELF_DATA in message:
                await self._handle_data_message(message)
                return
            if ResponseMessageTypes.NOT_ENOUGH_COINS in message:
                await self._handle_not_enough_coins_message()
                return

    async def _handle_init_message(self, message: dict) -> None:
        # Wallet data
        self.bot.wallet.set_score(message.get('score'))
        self.bot.wallet.set_place(message.get('place'))
        self.bot.wallet.set_tick(message.get('tick'))
        self.bot.wallet.update_items(message.get('items'))

        # Networking data
        self.random_id = message.get('randomId')
        self.top = message.get('top')

        try:
            c_pow = calculate_pow(message.get('pow'))
            init_message_response = "C1 {} {}".format(self.random_id, c_pow)
            await self.send_message(init_message_response)
        except js2py.PyJsException:
            await self._require_disconnect()
            return

        self.messages_sent = 1
        Logger.log_success(_("User has been loaded"))
        await self._player_initialized()

    async def _handle_item_bought_message(self, message: dict) -> None:
        Logger.log_success(_("Bought an item"))
        self.tick = message.get('tick', self.bot.wallet.tick)
        self.score = message.get('score', self.bot.wallet.score)
        self.bot.wallet.update_items(message.get('items'))

    async def _handle_missed_message(self) -> None:
        self.tick_message_response_received = True

    async def _handle_broken_message(self) -> None:
        Logger.log_error(_("Servers are down, reconnecting"))

    async def _handle_transfer_message(self, message: str) -> None:
        data = message.split(' ')[1::]

        if ResponseMessageTypes.TRANSACTION_IN_PROGRESS in data[0]:
            return

        amount = str(round(int(data[0]) / 1000))
        sender = data[1]
        Logger.log_success(_("Received {} coins from user {}").format(amount, sender))

    async def _handle_data_message(self, message: str) -> None:
        self.tick_message_response_received = True

        data = message.split(' ')[1::]
        self.random_id = data[2]

        self.bot.wallet.set_place(data[0])
        self.bot.wallet.set_score(data[1])

        if not self.on_start_user_output_send:
            await self._send_on_start_user_output()

        score_report = self.bot.wallet.get_player_score_report()
        items_report = self.bot.wallet.get_player_items_report()
        Logger.log_success(score_report)
        Logger.log_success(items_report)

    async def _handle_not_enough_coins_message(self) -> None:
        Logger.log_warning(_("Not enough coins to buy an item"))

    async def _auto_action_buy(self):
        items = self.bot.config.auto_buy_items

        for item in items:
            if hasattr(ItemTypes, item):
                if self.bot.wallet.has_player_enough_coins_to_buy(item):
                    message = RequestMessageGenerator.generate_buy_item_message(
                        item_id=getattr(ItemTypes, item),
                        messages_sent=self.messages_sent
                    )
                    await self.send_message(message)
                    Logger.log_success(_('Auto buying {}').format(item))

    async def _auto_action_transfer(self):
        receiver = self.bot.config.auto_transfer_to
        transfer_when = self.bot.config.auto_transfer_when
        transfer_percent = self.bot.config.auto_transfer_percent

        if self.bot.wallet.score / 1000 > transfer_when:
            transfer_amount = self.bot.wallet.score * (transfer_percent / 100)
            message = RequestMessageGenerator.generate_transfer_message(amount=transfer_amount, user_id=receiver,
                                                                        messages_sent=self.messages_sent)
            await self.send_message(message)

    async def _run_auto_actions(self):
        while not self.disconnect_required:
            if self.bot.config.auto_buy_enabled:
                await self._auto_action_buy()

            if self.bot.config.auto_transfer_enabled:
                await self._auto_action_transfer()

            await asyncio.sleep(self.bot.config.auto_buy_interval)

    async def _serve_received_messages_queue(self):
        logger.debug("Received messages queue are being served")
        while not self.disconnect_required:
            if self.received_messages_queue.empty():
                await asyncio.sleep(self.QUEUE_SLEEP_TIME)
                continue
            message = self.received_messages_queue.get()
            await self._process_received_message(message)

    async def _serve_pending_messages_queue(self):
        logger.debug("Pending messages queue are being served")
        while not self.disconnect_required:
            if self.pending_messages_queue.empty():
                await asyncio.sleep(self.QUEUE_SLEEP_TIME)
                continue
            message = self.pending_messages_queue.get()
            await self.connection.send(message)

            self.messages_sent += 1
            if self.messages_sent > 9:
                self.messages_sent = 1

    async def _send_tick_messages(self):
        while not self.disconnect_required:
            if self.tick_message_response_received:
                message = RequestMessageGenerator.generate_tick_message(random_id=self.random_id,
                                                                        messages_sent=self.messages_sent)
                await self.send_message(message)
                self.tick_message_response_received = False
            await asyncio.sleep(self.TICK_MESSAGE_SEND_INTERVAL)

    async def _create_tasks(self):
        self.event_loop.create_task(self._serve_received_messages_queue())
        self.event_loop.create_task(self._serve_pending_messages_queue())

    async def _listen(self):
        while not self.disconnect_required:
            try:
                connection_timeout = self.WAIT_FOR_MESSAGE_TIMEOUT if self.player_initialized \
                    else self.WAIT_FOR_MESSAGE_TIMEOUT_BEFORE_PLAYER_INIT
                await asyncio.wait_for(self._wait_for_message(), timeout=connection_timeout)
            except websockets.exceptions.ConnectionClosed:
                Logger.log_error(_("Connection closed, reconnecting"))
                await self._require_disconnect(reconnect=True)
            except asyncio.TimeoutError:
                logger.debug("Connection timeout")
                await self._require_disconnect()

    async def _send_on_start_user_output(self):
        if self.bot.config.goal:
            goal_timedelta = self.bot.wallet.calculate_goal_time(self.bot.config.goal)
            if goal_timedelta.total_seconds():
                Logger.log_system(_("Your goal will be reached in {}").format(goal_timedelta))

        option_status_on = _("On")
        option_status_off = _("Off")

        auto_buy_enabled = option_status_on if self.bot.config.auto_buy_enabled else option_status_off
        Logger.log_system(_("Auto buy is {}").format(auto_buy_enabled))
        auto_transfer_enabled = option_status_on if self.bot.config.auto_transfer_enabled else option_status_off
        Logger.log_system(_("Auto transfer is {}").format(auto_transfer_enabled))

        if auto_transfer_enabled == option_status_on:
            auto_transfer_receiver = self.bot.config.auto_transfer_to
            auto_transfer_percent = self.bot.config.auto_transfer_percent
            auto_transfer_when = self.bot.config.auto_transfer_when

            Logger.log_system(_("Auto transfer receiver is user with ID {}").format(auto_transfer_receiver))
            Logger.log_system(
                _("Auto transfer will be executed when balance will be more than {}").format(auto_transfer_when))
            Logger.log_system(_("Auto transfer will send {} percent of your balance").format(auto_transfer_percent))

        self.on_start_user_output_send = True

    async def run(self) -> int:
        await self._connect()
        await self._create_tasks()
        await self._listen()
        await self._disconnect()
        return int(self.reconnect_required)
