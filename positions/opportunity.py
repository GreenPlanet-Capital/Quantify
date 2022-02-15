from datetime import datetime
import pprint
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

    def get_rows(self):
        return [
            ('strategy_id', self.strategy_id),
            ('timestamp', self.timestamp),
            ('ticker', self.ticker),
            ('tv_link', self.tv_link),
            ('order_type', self.order_type),
            ('default_price', self.default_price),
            ('metadata', pprint.pformat(self.metadata))
        ]

    def _generate_tv_link(self):
        #TODO Generate a link to trading view for the ticker
        return f'https://www.tradingview.com/chart/?symbol={self.exchangeName}:{self.ticker}'

    def __repr__(self):
        x = PrettyTable()
        x.set_style(SINGLE_BORDER)
        x.field_names = ['Data', 'Value']
        x.add_rows(self.get_rows())
        return x.get_string()

