class BotConfig(object):
    def __init__(self, config):
        # Common settings
        self.goal = config.getint('GOAL', 0)

        # Auto buy settings
        self.auto_buy_enabled = config.getboolean('AUTOBUY_ENABLED', False)
        self.auto_buy_interval = config.getint('AUTOBUY_INTERVAL', 10)
        self.auto_buy_items = config.get("AUTOBUY_ITEMS", None)
        self.missed_messages_limit = config.getint(
            "MISSED_MESSAGES_LIMIT", 10)

        # Auto transfer settings
        self.auto_transfer_enabled = config.getboolean(
            'AUTO_TRANSFER', False)
        self.auto_transfer_to = config.getint('AUTO_TRANSFER_TO', 0)
        self.auto_transfer_when = config.getint('AUTO_TRANSFER_WHEN', 0)
        self.auto_transfer_percent = config.getint(
            'AUTO_TRANSFER_PERCENT', 0)
