from core.enums import ItemTypes
from typing import Dict
from gettext import gettext as _


class BotWallet(object):
    def __init__(self):
        self.place = 0
        self.score = 0
        self.tick = 0
        self.items = dict()

    def get_player_score_report(self) -> str:
        score = round(int(self.score) / 1000, 3)
        speed = round(int(self.tick) / 1000, 2)
        return _('Coins: {} | Speed: {} / tick | Place: {}'.format(score, speed, self.place))

    def get_player_items_report(self) -> str:
        return _(' | '.join(["{}: {}".format(key, value) for (key, value) in self.items.items()]))

    def set_score(self, score: any) -> None:
        self.score = int(score)

    def set_place(self, place: str) -> None:
        self.place = place

    def set_tick(self, tick: any) -> None:
        self.tick = tick

    def update_items(self, items: Dict) -> None:
        self.items = dict()
        for item in items:
            item_name = item.upper()
            if hasattr(ItemTypes, item_name):
                self.items[item_name] = self.items[item_name] + 1 if item_name in self.items.keys() else 0
