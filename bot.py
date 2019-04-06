import asyncio
import json
import logging

import vk_api
import websockets

from helpers import JSCodeExecutor


class ResponseMessageTypes(object):
    INIT = 'INIT'


class RequestMessageTypes(object):
    GET_PLACE = "X"
    GET_SCORE = "GU"
    BUY_ITEM = "B"


class RequestMessageGenerator(object):
    @staticmethod
    def generate(message_type, *args, **kwargs):
        if message_type == RequestMessageTypes.GET_PLACE:
            return RequestMessageGenerator._generate_get_place_message(*args, **kwargs)

        return None

    @staticmethod
    def _generate_get_place_message(*args, **kwargs):
        return f"{RequestMessageTypes.GET_PLACE}"

    @staticmethod
    def _generate_get_score_message(*args, **kwargs):
        return f"{RequestMessageTypes.GET_SCORE}"

    @staticmethod
    def _generate_buy_item_message(*args, **kwargs):
        item_id = kwargs.get('item_id')
        return f"{RequestMessageTypes.BUY_ITEM} {item_id}"


class VKCoinBot(object):
    def __init__(self, server_url, config=None):
        self.server_url = server_url
        self.logger = logging.getLogger(__file__)

        self.config = config

        self.get_place_message_interval = self.config.getint('CURRENT_PLACE_MESSAGE_INTERVAL', 10)

        self.connected = False
        self.messages_sent = 0
        self.message_queue = []

        self.place = 0

    async def _connect(self):
        self.connection = await websockets.connect(self.server_url)
        self.connected = True

    def _disconnect(self):
        self.connection.close()
        self.connected = False

    async def _send_message(self, message_content: str):
        message = f"P{self.messages_sent} {message_content}"
        await self.connection.send(message)
        self.logger.debug(f"Message has been sent: {message}")
        self.messages_sent += 1

    async def _send_enqueued_messages(self):
        while True:
            if len(self.message_queue):
                self.logger.debug("Sending enqueued messages...")
                message = self.message_queue.pop()
                await self._send_message(message)
            await asyncio.sleep(1)

    async def _enqueue_tick_messages(self):
        while True:
            self._enqueue_message(RequestMessageGenerator.generate(
                RequestMessageTypes.GET_PLACE))
            await asyncio.sleep(self.get_place_message_interval)

    async def _enqueue_score_messages(self):
        while True:
            self._enqueue_message(RequestMessageGenerator.generate(
                RequestMessageTypes.GET_SCORE))
            await asyncio.sleep(10)

    def _enqueue_message(self, message: str):
        self.message_queue.append(message)

    async def _process_message(self, message_string):
        try:
            message = json.loads(message_string)
        except json.JSONDecodeError:
            if message_string[0] == 'C':
                self._process_place_message(message_string)

            self.logger.debug(f"Received message: {message_string}")
            return
        message_type = message.get('type')
        if message_type == ResponseMessageTypes.INIT:
            await self._process_init_message(message)

    def _process_place_message(self, message):
        place = message.split(' ')[-1]
        self.place = place
        self.logger.info(f"Current place: {place}")

    async def _process_init_message(self, message):
        score = message.get('score')
        place = message.get('place')
        random_id = message.get('randomId')
        items = message.get('items')
        top = message.get('top')
        tick = message.get('tick')
        ccp = message.get('ccp')
        first_time = message.get('firstTime')
        m_pow = message.get('pow').replace(
            "window.location.host", "window.location")
        response_message = f"C1 {random_id}"
        await self.connection.send(response_message)
        self.messages_sent = 2
        self._start_sender()

    async def _listen(self, reconnect=True):
        self.logger.info("Listener started...")
        while True:
            try:
                message = await self.connection.recv()
                await self._process_message(message)
            except websockets.exceptions.ConnectionClosed:
                self.logger.info("Connection closed")
                if not reconnect:
                    asyncio.get_running_loop().stop()
                    return
                await asyncio.sleep(1)
                await self._reconnect()

    async def _reconnect(self):
        self._disconnect()
        await self._connect()

    def _start_listener(self):
        asyncio.get_running_loop().create_task(self._listen())

    def _start_sender(self):
        asyncio.get_running_loop().create_task(self._enqueue_tick_messages())
        asyncio.get_running_loop().create_task(self._enqueue_score_messages())
        asyncio.get_running_loop().create_task(self._send_enqueued_messages())

    async def run(self):
        self.logger.info(f"Connecting to {self.server_url}")
        await self._connect()
        self.logger.info("VKCoinPy is running...")
        self._start_listener()
        self._disconnect()
