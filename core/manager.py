import asyncio
import logging
from urllib.parse import urlparse

import vk_api

from core.bot import VKCoinBot
from core.helpers import get_pass


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

        return "{}://{}/channel/{}/?{}&ver=1&pass={}".format(protocol, host, channel, query, pass_hash)

    def authorize(self):
        self.vk_session = vk_api.VkApi(token=self.vk_token)

    def _get_current_user_data(self):
        self.vk_user_data = self.vk_session.method('users.get')[0]

    def _get_mobile_iframe_url(self):
        app_data = self.vk_session.method(
            'apps.get', {'app_id': self.VK_COIN_APP_ID}).get('items')[0]
        mobile_iframe_url = app_data.get('mobile_iframe_url', None)
        if mobile_iframe_url is None:
            raise ValueError("Mobile Iframe URL is empty")
        return mobile_iframe_url

    def _get_channel(self):
        return self.vk_user_data['id'] % 32

    def start(self):
        self.authorize()
        self._get_current_user_data()
        server_url = self._get_server_websocket_url(
            channel=self._get_channel())
        self.logger.debug("Server URL: {}".format(server_url))

        bot = VKCoinBot(server_url, self.config)

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(bot.run())
