from core.enums import ItemTypes
from typing import Dict
from gettext import gettext as _

DEFAULT_ITEM_PRICES = {
    ItemTypes.CURSOR: 30,
    ItemTypes.CPU: 100,
    ItemTypes.CPU_STACK: 1000,
    ItemTypes.COMPUTER: 10000,
    ItemTypes.SERVER_VK: 50000,
    ItemTypes.QUANTUM_PC: 200000,
    ItemTypes.DATACENTER: 5000000
}


class BotWallet(object):
    def __init__(self):
        self.place = 0
        self.score = 0
        self.tick = 0
        self.items = dict()

        self.item_prices = DEFAULT_ITEM_PRICES.copy()

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
            self.items[item] = self.items[item] + 1 if item in self.items.keys() else 0
        self.update_item_prices()

    def _calculate_item_price(self, default_price, count) -> int:
        if count < 1:
            return default_price
        return round(1.3 * self._calculate_item_price(default_price, count - 1))

    def calculate_item_price(self, item: ItemTypes) -> int:
        default_price = DEFAULT_ITEM_PRICES.get(item)
        item_count = self.items.get(item, 0) + 1
        return self._calculate_item_price(default_price, item_count)

    def update_item_prices(self) -> None:
        for item in self.item_prices.keys():
            self.item_prices[item] = self.calculate_item_price(item)

    def has_player_enough_coins_to_buy(self, item: str) -> bool:
        item = getattr(ItemTypes, item)
        self.update_item_prices()

        item_price = self.item_prices.get(item, 0)
        return self.score > item_price
