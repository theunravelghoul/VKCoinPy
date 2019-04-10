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
from core.wallet import BotWallet

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

        self.report_enabled = self.config.get('report_enabled', True)
        self.report_interval = self.config.get('report_interval', 60)
        self.bot_sessions = self.create_bot_sessions(self.config)

    @staticmethod
    def create_bot_sessions(config: Dict) -> List[VKCoinBotSession]:
        bot_configs = config["bots"]
        bot_count = len(bot_configs)
        Logger.log_system(_("Found {} bots in config file").format(bot_count))

        sessions = []
        for bot_config in bot_configs:
            try:
                session = VKCoinBotSession(bot_config)
                session.setup()
                sessions.append(session)
            except Exception:
                Logger.log_error(_("Can not load bot with config #{}").format(bot_config))

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
            exit()

    def is_any_bot_running(self) -> bool:
        return any([session.bot.is_connected for session in self.bot_sessions])

    def count_bots_running(self) -> int:
        return len([session.bot for session in self.bot_sessions if session.bot.is_connected])

    async def report(self):
        while True:
            wallets: List[BotWallet] = [session.bot.wallet for session in self.bot_sessions]
            summary_tick = sum([wallet.tick for wallet in wallets]) / 1000
            summary_score = sum([wallet.score for wallet in wallets]) / 1000
            summary_hourly_rate = sum([wallet.hourly_rate for wallet in wallets]) / 1000

            Logger.log_warning(_("VKCoinPy stats"))
            Logger.log_warning(_("{} bots are running").format(self.count_bots_running()))
            Logger.log_warning(
                _("Summary speed: {} / tick | Summary score: {} | Summary hourly rate: {}").format(summary_tick,
                                                                                                   summary_score,
                                                                                                   summary_hourly_rate))
            await asyncio.sleep(self.report_interval)

    def start(self):
        for session in self.bot_sessions:
            session_thread = VKCoinBotSessionThread(session)
            try:
                session_thread.start()
            except:
                Logger.log_error(_("Can not start session for bot ID{}").format(session.vk_user_id))
        event_loop = asyncio.get_event_loop()
        if self.report_enabled:
            event_loop.create_task(self.report())
        event_loop.run_forever()
