import threading
import daemonize

from core.manager import VKCoinBotManager

config = VKCoinBotManager.load_common_config()
daemon_mode = config.get('daemon', False)

threading.current_thread().name = "VKCoinPy Bot Manager"

bot = VKCoinBotManager(config)
if not daemon_mode:
    bot.start()
else:
    pid = './VKCoinPy.pid'
    daemon_instance = daemonize.Daemonize(app='VKCoinPy', pid=pid, action=bot.start, foreground=False)
    daemon_instance.start()
