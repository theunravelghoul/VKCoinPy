class BotConfig(object):
    def __init__(self, config):
        # Common settings
        self.goal = config.get("goal", 0)
        self.progress_report_interval = config.get("progress_report_interval", 2)

        # Auto buy settings
        self.auto_buy_enabled = config.get('auto_buy_enabled', False)
        self.auto_buy_interval = config.get('auto_buy_interval', 10)
        self.auto_buy_items = config.get("auto_buy_items", None)

        # Auto transfer settings
        self.auto_transfer_enabled = config.get("auto_transfer_enabled", False)
        self.auto_transfer_to = config.get('auto_transfer_to', 0)
        self.auto_transfer_when = config.get('auto_transfer_when', 0)
        self.auto_transfer_percent = config.get('auto_transfer_percent', 0)
