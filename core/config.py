class BotConfig(object):
    def __init__(self, config):
        # Intervals and timeouts
        self.current_place_message_interval = config.getint(
            'CURRENT_PLACE_MESSAGE_INTERVAL', 10)
        self.reconnect_timeout = config.getint('RECONNECT_TIMEOUT', 10)
        self.enqueue_message_timeout = config.getint(
            'ENQUEUE_MESSAGE_TIMEOUT', 1)
        self.init_connection_retry_interval = config.getint(
            'INIT_CONNECTION_RETRY_INTERVAL', 1)

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
