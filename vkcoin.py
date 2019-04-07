import threading

from core.manager import VKCoinBotManager

threading.current_thread().name = "VKCoinPy Bot Manager"

bot = VKCoinBotManager()
bot.start()
