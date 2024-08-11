from datetime import datetime
from typing import List
import robin_stocks.robinhood as r
from Quantify.integrations.base import BaseIntegration
from Quantify.positions.position import Position
from Quantify.positions.opportunity import Opportunity
import configparser


class RobinhoodIntegration(BaseIntegration):
    def __init__(self, strat_id) -> None:
        super().__init__(strat_id)

    def authenticate(self) -> None:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read("../creds.ini")
        r.login(
            username=cfg_parser.get("robinhood", "username"),
            password=cfg_parser.get("robinhood", "password"),
        )

    def get_open_positions(self) -> List[Position]:
        rh_positions = r.get_open_stock_positions()
        positions = []

        for rh_pos in rh_positions:
            opp = Opportunity(
                strategy_id=self.strat_id,
                timestamp=self.parse_rh_datetime(rh_pos["created_at"]),
                ticker=rh_pos["symbol"],
                exchangeName="",  # Not available in RH API
                order_type=1,  # No shorting in RH
                default_price=rh_pos["average_buy_price"],
                metadata={},
            )
            positions.append(opp)

        return positions

    def parse_rh_datetime(self, rh_datetime: str) -> datetime:
        return datetime.strptime(rh_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")


if __name__ == "__main__":
    robinhood = RobinhoodIntegration(1)
    robinhood.authenticate()
    positions = robinhood.get_open_positions()
    print(positions)
