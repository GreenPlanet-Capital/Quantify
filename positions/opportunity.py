from datetime import datetime
import pprint
from typing import List
from prettytable import PrettyTable, SINGLE_BORDER


class Opportunity:
    def __init__(self, *, strategy_id, timestamp: datetime, ticker, exchangeName, order_type, default_price, metadata: dict()) -> None:
        self.strategy_id = strategy_id
        self.timestamp = timestamp
        self.ticker = ticker
        self.exchangeName = exchangeName
        self.tv_link = self._generate_tv_link()
        self.order_type = order_type
        self.default_price = default_price
        self.metadata: dict() = metadata

    def get_rows(self, pre_entries: List=None, post_entries: List=None):
        to_return = []
        mid_rows = [
            ('strategy_id', self.strategy_id),
            ('timestamp', self.timestamp),
            ('ticker', self.ticker),
            ('tv_link', self.tv_link),
            ('order_type', self.order_type),
            ('default_price', self.default_price),
            ('metadata', pprint.pformat(self.metadata))
        ]
        if pre_entries:
            to_return.extend(mid_rows)
        to_return.extend(mid_rows)
        if post_entries:
            to_return.extend(post_entries)
        return to_return


    def _generate_tv_link(self):
        return f'https://www.tradingview.com/chart/?symbol={self.exchangeName}:{self.ticker}'

    def get_string(self, pre_entries: List=None, post_entries: List=None):
        x = PrettyTable()
        x.set_style(SINGLE_BORDER)
        x.field_names = ['Data', 'Value']
        x.add_rows(self.get_rows(pre_entries, post_entries))
        return x.get_string()

    def __repr__(self):
        x = PrettyTable()
        x.set_style(SINGLE_BORDER)
        x.field_names = ['Data', 'Value']
        x.add_rows(self.get_rows())
        return x.get_string()

