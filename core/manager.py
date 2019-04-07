import asyncio
import json
import logging
from typing import Dict
from urllib.parse import urlparse

import requests
import vk_api

from core.bot import VKCoinBot
from core.helpers import get_pass, setup_logging
from core.locale import _


class VKCoinBotManager(object):
    VK_COIN_APP_ID = 6915965

    def __init__(self):
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.INFO)

        self.vk_session = None
        self.vk_user_data = None

        self.config = self.load_config()

        setup_logging(self.config)

        self.vk_token = self.config["vk_token"]
        self.use_credentials = self.config["vk_use_credentials"]
        self.vk_group_id = self.config.get("vk_group_id")

        self.mine_for_vk_group = False

        if self.use_credentials:
            self.vk_username = self.config.get('vk_username')
            self.vk_password = self.config.get('vk_password')
            if not self.vk_username or not self.vk_password:
                raise AttributeError(_("You must set vk_username and vk_password when setting use_credentials:true"))

        if self.use_credentials and self.vk_group_id:
            self.mine_for_vk_group = True

    def load_config(self) -> Dict:
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
            return config
        except (json.JSONDecodeError, FileNotFoundError):
            print(_("Can not load config"))

    def _get_server_url(self, channel):
        base_url = self._get_mobile_iframe_url() if not self.mine_for_vk_group else self._get_group_mobile_iframe_url()
        user_id = self.vk_user_data['id']
        pass_hash = get_pass(user_id, 0)

        parsed_base_url = urlparse(base_url)
        protocol = "ws" if parsed_base_url.scheme == "http" else "wss"
        host = parsed_base_url.netloc
        query = parsed_base_url.query

        return "{}://{}/channel/{}/?{}&ver=1&pass={}".format(protocol, host, channel, query, pass_hash)

    def authorize(self):
        if self.use_credentials:
            self.vk_token = self._get_token_from_credentials()
        self.vk_session = vk_api.VkApi(token=self.vk_token)

    def _get_token_from_credentials(self) -> str:
        api_auth_url = 'https://oauth.vk.com/token?grant_type=password&client_id=2274003' \
                       '&client_secret=hHbZxrka2uZ6jB1inYsH&username={}&password={}'.format(self.vk_username,
                                                                                            self.vk_password)
        response = requests.get(api_auth_url)
        token = response.json().get("access_token")
        if not token:
            raise Exception(_("Can not login with provided credentials"))
        return token

    def _handle_two_factor_auth(self, remember=True):
        code = input(_("Enter two-factor auth code"))
        return code, remember

    def _get_current_user_data(self):
        self.vk_user_data = self.vk_session.method('users.get')[0]

    def _get_mobile_iframe_url(self):
        app_data = self.vk_session.method(
            'apps.get', {'app_id': self.VK_COIN_APP_ID}).get('items')[0]
        mobile_iframe_url = app_data.get('mobile_iframe_url', None)
        if mobile_iframe_url is None:
            raise ValueError("Mobile Iframe URL is empty")
        return mobile_iframe_url

    def _get_group_mobile_iframe_url(self):
        screen_name = "app{}_-{}".format(self.VK_COIN_APP_ID, self.vk_group_id)
        owner_id = "-{}".format(self.vk_group_id)
        param = {
            'access_token': self.vk_token,
            'v': 5.55,
            'screen_name': screen_name,
            'owner_id': owner_id,
            'func_v': 3
        }

        response = requests.get('https://api.vk.com/method/execute.resolveScreenName', params=param).json()
        if response.get('errors'):
            raise ValueError(_("Can not load mobile_iframe_url from the VK API"))
        mobile_iframe_url = response.get("response", {}).get("embedded_uri", {}).get("view_url")
        if mobile_iframe_url is None:
            raise ValueError("Mobile Iframe URL is empty")
        return mobile_iframe_url

    def _get_channel(self):
        return self.vk_user_data['id'] % 32

    def start(self):
        self.authorize()
        self._get_current_user_data()
        server_url = self._get_server_url(
            channel=self._get_channel())
        self.logger.debug("Server URL: {}".format(server_url))

        bot = VKCoinBot(server_url, self.config)

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(bot.run())
