import asyncio
import json
import logging
import threading
from typing import Dict, List

from core.bot import VKCoinBot
from core.helpers import setup_logging
from core.locale import _
from core.logger import Logger
from core.vk import VKConnector

logger = logging.getLogger(__file__)


class VKCoinBotSession(object):
    def __init__(self, config: Dict):
        self.config = config
        vk_token = config.get("vk_token")
        vk_username = config.get('vk_username')
        vk_password = config.get('vk_password')
        vk_use_credentials = config.get('vk_use_credentials')
        vk_group_id = config.get('vk_group_id')

        self.vk_connector = VKConnector(vk_token, vk_username, vk_password, vk_use_credentials, vk_group_id)
        self.vk_user_id = None
        self.bot = None

    def setup(self):
        Logger.log_system(_("Starting bot session"))

        self.vk_connector.authorize()
        self.vk_user_id = self.vk_connector.vk_user_id

        self.vk_connector.check_bot_group_subscription()

        server_url = self.vk_connector._get_server_url()

        logger.debug("Server URL: {}".format(server_url))
        Logger.log_system(_("Bot session created for user with ID {}").format(self.vk_user_id))

        self.bot = VKCoinBot(server_url, self.config)


class VKCoinBotSessionThread(threading.Thread):
    def __init__(self, session: VKCoinBotSession):
        super().__init__()
        self.event_loop = None
        self.session = session
        self.name = "Bot ID{}".format(self.session.vk_user_id)

    def run(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(self.session.bot.run())

    def add_task(self, coro):
        task = self.event_loop.create_task(coro)
        self.event_loop.call_soon_threadsafe(task)


class VKCoinBotManager(object):
    def __init__(self):
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.INFO)

        self.config = self.load_common_config()
        setup_logging(self.config)
        self.bot_sessions = self.create_bot_sessions(self.config)

    @staticmethod
    def create_bot_sessions(config: Dict) -> List[VKCoinBotSession]:
        bot_configs = config["bots"]
        bot_count = len(bot_configs)
        Logger.log_system(_("Found {} bots in config file").format(bot_count))

        sessions = []
        try:
            for bot_config in bot_configs:
                session = VKCoinBotSession(bot_config)
                session.setup()
                sessions.append(session)
        except Exception as e:
            Logger.log_error(_("Can not load bot with config #{}").format(config))
            logger.exception(e)

        if not sessions:
            Logger.log_error(_("No sessions created"))

        return sessions

    @staticmethod
    def load_common_config() -> Dict:
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
            return config
        except (json.JSONDecodeError, FileNotFoundError):
            print(_("Can not load config"))

    def start(self):
        for session in self.bot_sessions:
            session_thread = VKCoinBotSessionThread(session)
            session_thread.start()
