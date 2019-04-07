from urllib.parse import urlparse

import requests
import vk_api

from core.helpers import get_pass
from core.locale import _


class VKConnector(object):
    VK_COIN_APP_ID = 6915965

    def __init__(self, token: str = None, username: str = None, password: str = None, use_credentials: bool = False,
                 vk_group_id=None):
        if not token and not (username and password):
            raise Exception(_("Either token or credentials must be provided"))

        if use_credentials and not (username and password):
            raise Exception(_("Username and password are not provided"))

        self.use_credentials = use_credentials
        self.vk_group_id = vk_group_id

        self.mine_for_vk_group = False
        if self.use_credentials and self.vk_group_id:
            self.mine_for_vk_group = True

        if not self.use_credentials:
            self.vk_token = token
        else:
            self.vk_token = None
            self.vk_username = username
            self.vk_password = password

        self.vk_session = None
        self.vk_user_data = None

    @property
    def vk_user_id(self) -> any:
        return self.vk_user_data and self.vk_user_data.get('id')

    def _get_server_url(self):
        base_url = self._get_mobile_iframe_url() if not self.mine_for_vk_group else self._get_group_mobile_iframe_url()
        user_id = self.vk_user_id
        pass_hash = get_pass(user_id, 0)
        channel = self._get_channel()

        parsed_base_url = urlparse(base_url)
        protocol = "ws" if parsed_base_url.scheme == "http" else "wss"
        host = parsed_base_url.netloc
        query = parsed_base_url.query

        return "{}://{}/channel/{}/?{}&ver=1&pass={}".format(protocol, host, channel, query, pass_hash)

    def authorize(self):
        if self.use_credentials:
            self.vk_token = self._get_token_from_credentials()
        self.vk_session = vk_api.VkApi(token=self.vk_token)
        self._get_current_user_data()

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
