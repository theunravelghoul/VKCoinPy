import asyncio
import json
import logging
import random
from typing import Union

import vk_api
import websockets

from helpers import calculate_pow


class ResponseMessageTypes(object):
    INIT = 'INIT'
    NOT_ENOUGH_COINS = 'NOT_ENOUGH_COINS'
    SELF_DATA = 'SELF_DATA'
    MISS = 'MISS'


class RequestMessageTypes(object):
    GET_PLACE = "X"
    GET_SCORE = "GU"
    BUY_ITEM = "B"
    TICK = "TICK"


class Items(object):
    CURSOR = "cursor"
    CPU = "cpu"
    CPU_STACK = "CPU_STACK"
    COMPUTER = "COMPUTER"
    SERVER_VK = "SERVER_VK"
    QUANTUM_PC = "QUANTUM_PC"
    DATACENTER = "DATACENTER"


class RequestMessageGenerator(object):
    @staticmethod
    def generate(message_type, *args, **kwargs) -> Union[str, None]:
        if message_type == RequestMessageTypes.GET_PLACE:
            return RequestMessageGenerator._generate_get_place_message(*args, **kwargs)
        if message_type == RequestMessageTypes.BUY_ITEM:
            return RequestMessageGenerator._generate_buy_item_message(*args, **kwargs)
        if message_type == RequestMessageTypes.GET_SCORE:
            return RequestMessageGenerator._generate_get_score_message(*args, **kwargs)
        if message_type == RequestMessageTypes.TICK:
            return RequestMessageGenerator._generate_tick_message(*args, **kwargs)

        return None

    @staticmethod
    def _generate_get_place_message(*args, **kwargs) -> str:
        messages_sent = kwargs['messages_sent']
        return f"{RequestMessageTypes.GET_PLACE}"

    @staticmethod
    def _generate_get_score_message(*args, **kwargs) -> str:
        messages_sent = kwargs['messages_sent']
        return f"{RequestMessageTypes.GET_SCORE}"

    @staticmethod
    def _generate_buy_item_message(*args, **kwargs) -> str:
        item_id = kwargs['item_id']
        messages_sent = kwargs['messages_sent']
        return f"P{messages_sent} {RequestMessageTypes.BUY_ITEM} {item_id}"

    @staticmethod
    def _generate_tick_message(*args, **kwargs) -> str:
        random_id = kwargs['random_id']
        messages_sent = kwargs['messages_sent']
        return f"C{messages_sent} {random_id} 1"


class VKCoinBot(object):
    def __init__(self, server_url, config=None) -> None:
        self.server_url = server_url
        self.logger = logging.getLogger(__file__)

        self.config = config

        self.get_place_message_interval = self.config.getint(
            'CURRENT_PLACE_MESSAGE_INTERVAL', 10)
        self.autobuy_enabled = self.config.getboolean('AUTOBUY_ENABLED', False)
        self.autobuy_interval = self.config.getint('AUTOBUY_INTERVAL', 10)
        self.autobuy_items = self.config.get("AUTOBUY_ITEMS", None)
        self.missed_messages_limit = self.config.getint(
            "MISSED_MESSAGES_LIMIT", 10)

        self.connected = False
        self.messages_sent = 1
        self.message_queue = []
        self.messages_enqueued = False
        self.missed_messages = 0
        self.successful_messages = 0
        self.restart = False
        self.tick_response_received = True

        self.place = 0
        self.score = 0
        self.top = None
        self.tick = 0
        self.random_id = None

    def report_player_score(self):
        self.logger.info(f'Coins: {round(int(self.score) / 1000, 3)} | Place: {self.place}')

    async def _connect(self) -> None:
        self.connection = await websockets.connect(self.server_url)
        self.connected = True

    async def _disconnect(self) -> None:
        await self.connection.close()
        self.connected = False

    async def _send_message(self, message_content: str) -> None:
        self.logger.debug(f"Sending message: {message_content}")
        await self.connection.send(message_content)
        self.logger.debug(f"Message has been sent: {message_content}")
        self.messages_sent += 1

        if self.messages_sent > 9:
            self.messages_sent = 1

    async def _send_enqueued_messages(self) -> None:
        while not self.restart:
            if len(self.message_queue):
                self.logger.debug("Sending enqueued messages...")
                message = self.message_queue.pop()
                await self._send_message(message)
            else:
                self.logger.debug("No messages in the queue yet")
            await asyncio.sleep(1)

    async def _enqueue_tick_messages(self) -> None:
        while not self.restart:
            if self.tick_response_received:
                self._enqueue_message(RequestMessageGenerator.generate(
                    RequestMessageTypes.TICK, random_id=self.random_id, messages_sent=self.messages_sent))
                tick_response_received = False
            await asyncio.sleep(1)

    async def _enqueue_score_messages(self) -> None:
        while not self.restart:
            self._enqueue_message(RequestMessageGenerator.generate(
                RequestMessageTypes.GET_SCORE, messages_sent=self.messages_sent))
            await asyncio.sleep(10)

    async def _enqueue_buy_messages(self) -> None:
        while not self.restart:
            items = self.autobuy_items.split(",")

            for item in items:
                if hasattr(Items, item):
                    self._enqueue_message(RequestMessageGenerator.generate(
                        RequestMessageTypes.BUY_ITEM, item_id=getattr(
                            Items, item), messages_sent=self.messages_sent
                    ))
                    self.logger.info(f'Trying to buy {item}')

            await asyncio.sleep(self.autobuy_interval)

    def _enqueue_message(self, message: str) -> None:
        self.message_queue.append(message)

    async def _process_message(self, message_string: str) -> None:
        try:
            message = json.loads(message_string)
        except json.JSONDecodeError:
            self.logger.debug(f"Received message: {message_string}")
            if message_string[0] == 'C':
                self._process_place_message(message_string)
            if ResponseMessageTypes.SELF_DATA in message_string:
                self._process_self_data_message(message_string)
            if ResponseMessageTypes.NOT_ENOUGH_COINS in message_string:
                self.logger.info("Not enough coins to buy item")
            if ResponseMessageTypes.MISS in message_string:
                self.successful_messages = 0
                self.missed_messages += 1
                if self.missed_messages > self.missed_messages_limit:
                    self.logger.error("Too many missclicks! Reconnecting...")
                    await self._reconnect(cleanup=True)
            return

        message_type = message.get('type')
        if message_type == ResponseMessageTypes.INIT:
            await self._process_init_message(message)

    def _process_place_message(self, message: str) -> None:
        place = message.split(' ')[-1]
        self.place = place
        self.logger.info(f"Current place: {place}")

    def _process_self_data_message(self, message: str) -> None:
        data = message.split(' ')[1::]
        self.random_id = data[2]
        self.place = data[0]
        self.score = data[1]

        self.report_player_score()
        self.tick_response_received = True
        self.successful_messages += 1
        self.missed_messages = 0

        if not self.messages_enqueued:
            if self.autobuy_enabled and self.autobuy_items:
                asyncio.get_running_loop().create_task(self._enqueue_buy_messages())
            self.messages_enqueued = True

    async def _process_init_message(self, message: str) -> None:
        self.score = message.get('score')
        self.place = message.get('place')
        self.random_id = message.get('randomId')
        self.items = message.get('items')
        self.top = message.get('top')
        self.tick = message.get('tick')
        ccp = message.get('ccp')
        first_time = message.get('firstTime')

        try:
            c_pow = calculate_pow(message.get('pow'))
            init_message_response = f"C1 {self.random_id} {c_pow}"
            await self._send_message(init_message_response)
        except Exception:
            self.logger.debug("Can not load the player, retrying...")
            await asyncio.sleep(2)
            await self._reconnect(cleanup=True)
            return

        self.messages_sent = 1
        self._start_sender()
        self.logger.info("User has been loaded")

    async def _wait_for_message(self) -> None:
        message = await self.connection.recv()
        if message:
            await self._process_message(message)

    async def _listen(self, reconnect: bool = True) -> None:
        self.logger.debug("Listener started...")
        while not self.restart:
            try:
                await asyncio.wait_for(self._wait_for_message(), timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.debug("No messages from the server received")
                continue
            except websockets.exceptions.ConnectionClosed:
                self.logger.debug("Connection closed")
                if not reconnect:
                    asyncio.get_running_loop().stop()
                    return
                self.logger.debug("Listener stopped")
                await asyncio.sleep(1)
                await self._reconnect()
            except Exception:
                self.logger.exception()
                self.logger.debug("Listener stopped")
        self.logger.debug("Listener stopped")

    async def _reconnect(self, cleanup=True) -> None:
        await self._disconnect()
        self.restart = True
        if cleanup:
            self.messages_sent = 1
            self.missed_messages = 0
            self.successful_messages = 0
            self.tick_response_received = True
            self.message_queue.clear()
        await self._connect()
        self.restart = False
        self._start_listener()

    def _start_listener(self) -> None:
        asyncio.get_running_loop().create_task(self._listen())

    def _start_sender(self) -> None:
        self.logger.debug("Starting messaging")
        asyncio.get_running_loop().create_task(self._enqueue_tick_messages())
        asyncio.get_running_loop().create_task(self._send_enqueued_messages())

    async def run(self) -> None:
        self.logger.info(f"Connecting to {self.server_url}")
        await self._connect()
        self.logger.info("VKCoinPy is running...")
        self._start_listener()
        await self._disconnect()
