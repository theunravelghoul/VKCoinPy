import asyncio
import configparser
import logging
import os
from urllib.parse import urlparse

import vk_api

from bot import VKCoinBot
from helpers import get_pass


class VKCoinBotManager(object):
    VK_COIN_APP_ID = 6915965

    def __init__(self, config):
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.INFO)
        self.config = config

        self.vk_session = None
        self.vk_user_data = None

    @property
    def vk_token(self):
        return self.config['VK_TOKEN']

    def _get_server_websocket_url(self, channel):
        base_url = self._get_mobile_iframe_url()
        user_id = self.vk_user_data['id']
        pass_hash = get_pass(user_id, 0)

        parsed_base_url = urlparse(base_url)
        protocol = "ws" if parsed_base_url.scheme == "http" else "wss"
        host = parsed_base_url.netloc
        query = parsed_base_url.query

        return f"{protocol}://{host}/channel/{channel}?{query}&pass={pass_hash}"

    def authorize(self):
        self.vk_session = vk_api.VkApi(token=self.vk_token)

    def _get_current_user_data(self):
        self.vk_user_data = self.vk_session.method('users.get')[0]

    def _get_mobile_iframe_url(self):
        app_data = self.vk_session.method(
            'apps.get', {'app_id': self.VK_COIN_APP_ID}).get('items')[0]
        mobile_iframe_url = app_data.get('mobile_iframe_url', None)
        if mobile_iframe_url is None:
            raise ValueError("Mobile App Iframe URL is empty")
        return mobile_iframe_url

    def _get_channel(self):
        return self.vk_user_data['id'] % 16

    def start(self):
        self.authorize()
        self._get_current_user_data()
        server_url = self._get_server_websocket_url(
            channel=self._get_channel())
        self.logger.info(f"Server URL: {server_url}")
        self.bot = VKCoinBot(server_url)

        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.bot.run())
        event_loop.run_forever()


logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config_file_path = os.path.join(os.getcwd(), 'config.ini')
if not os.path.exists(config_file_path):
    raise AttributeError("Config file not found!")
config.read(config_file_path)
try:
    bot = VKCoinBotManager(config['BOT'])
    bot.start()
except KeyError:
    raise AttributeError("Config does not contain BOT section!")
