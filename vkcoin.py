from manager import VKCoinBotManager
from helpers import setup_logging
import configparser
import os

config = configparser.ConfigParser()
config_file_path = os.path.join(os.getcwd(), 'config.ini')
if not os.path.exists(config_file_path):
    raise AttributeError("Config file not found!")
config.read(config_file_path)

try:
    bot_config = config['BOT']
except KeyError:
    raise AttributeError("Config does not contain [BOT] section!")

setup_logging(bot_config=bot_config)

bot = VKCoinBotManager(config['BOT'])
bot.start()
