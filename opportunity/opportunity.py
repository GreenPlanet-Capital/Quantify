class Opportunity:
    def __init__(self, strategy_id, ticker, order_type, default_price, metadata: dict()) -> None:
        self.strategy_id = strategy_id
        self.ticker = ticker
        self.order_type = order_type
        self.default_price = default_price
        self.metadata: dict() = metadata

    def __str__(self) -> str:
        pass
