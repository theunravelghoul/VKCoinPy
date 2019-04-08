import datetime
from typing import Dict, Union

from core.enums import ItemTypes
from core.locale import _

DEFAULT_ITEM_PRICES = {
    ItemTypes.CURSOR: 30,
    ItemTypes.CPU: 100,
    ItemTypes.CPU_STACK: 1000,
    ItemTypes.COMPUTER: 10000,
    ItemTypes.SERVER_VK: 50000,
    ItemTypes.QUANTUM_PC: 200000,
    ItemTypes.DATACENTER: 5000000
}

ITEM_STATS = {
    ItemTypes.CURSOR: 1,
    ItemTypes.CPU: 3,
    ItemTypes.CPU_STACK: 10,
    ItemTypes.COMPUTER: 30,
    ItemTypes.SERVER_VK: 100,
    ItemTypes.QUANTUM_PC: 500,
    ItemTypes.DATACENTER: 1000
}


class BotWallet(object):
    def __init__(self):
        self.place = 0
        self.score = 0
        self.tick = 0
        self.items = dict()
        self.item_prices = DEFAULT_ITEM_PRICES.copy()
        self.hourly_rate = 0

    def get_player_score_report(self) -> str:
        score = round(int(self.score) / 1000, 3)
        speed = round(int(self.tick) / 1000, 2)
        return _('Coins: {} | Speed: {} / tick | Place: {}').format(score, speed, self.place)

    def get_player_items_report(self) -> str:
        return ' | '.join(["{}: {}".format(_(key), value) for (key, value) in self.items.items()])

    def get_player_stats_report(self) -> str:
        hourly_rate = self.hourly_rate / 1000
        return _("Hourly rate: {}").format(hourly_rate)

    def set_score(self, score: any) -> None:
        self.score = int(score)
        self.on_update()

    def set_place(self, place: str) -> None:
        self.place = place
        self.on_update()

    def set_tick(self, tick: any) -> None:
        self.tick = tick
        self.calculate_hourly_rate()
        self.on_update()

    def update_items(self, items: Dict) -> None:
        self.items = dict()
        for item in items:
            if item in [getattr(ItemTypes, key) for key in ItemTypes.__dict__.keys()]:
                self.items[item] = self.items[item] + 1 if item in self.items.keys() else 1
        self.update_item_prices()
        self.on_update()

    def _calculate_item_price(self, default_price, count) -> int:
        if count < 1:
            return default_price
        return round(1.3 * self._calculate_item_price(default_price, count - 1))

    def calculate_item_price(self, item: ItemTypes) -> int:
        default_price = DEFAULT_ITEM_PRICES.get(item)
        item_count = self.items.get(item, 0)
        return self._calculate_item_price(default_price, item_count)

    def update_item_prices(self) -> None:
        for item in self.item_prices.keys():
            self.item_prices[item] = self.calculate_item_price(item)

    def has_player_enough_coins_to_buy(self, item: str) -> bool:
        self.update_item_prices()
        item_price = self.item_prices.get(item, 0)
        return self.score > item_price

    def calculate_hourly_rate(self) -> None:
        self.hourly_rate = self.tick * 3600

    def calculate_goal_time(self, goal: int) -> datetime.timedelta:
        if goal < self.score / 1000 or (self.tick / 1000) == 0:
            seconds = 0
        else:
            amount = goal - self.score / 1000
            seconds = amount // (self.tick / 1000)
        return datetime.timedelta(seconds=seconds)

    def on_update(self) -> any:
        pass

    def get_best_item_to_buy(self) -> Union[ItemTypes, None]:
        if not self.items or not self.item_prices:
            return None

        sorted_by_price_items = sorted(self.items, reverse=True, key=lambda i: self.item_prices[i])
        best_item = sorted_by_price_items[0]
        for item in sorted_by_price_items[1::]:
            best_item_price = self.item_prices[best_item]
            best_item_efficiency = self.items[best_item] * ITEM_STATS[best_item]

            item_efficiency = self.items[item] * ITEM_STATS[item]
            item_price = self.item_prices[item]
            diff = best_item_price // item_price
            if diff > 1:
                efficiency_diff = best_item_efficiency - item_efficiency * diff
                if efficiency_diff < 0:
                    best_item = item
        return best_item
