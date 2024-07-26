from typing import Dict, List
from pandas import DataFrame
from Quantify.positions.opportunity import Opportunity
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.base_tester import BaseTester
import alpaca_trade_api as tradeapi
from subprocess import check_output


class LiveTester(BaseTester):
    def __init__(
        self,
        list_of_final_symbols: List[str],
        dict_of_dfs: Dict[str, DataFrame],
        exchangeName: str,
        strat: BaseStrategy,
        num_top: int,
        percent_l: float,
    ):
        super().__init__(
            list_of_final_symbols, dict_of_dfs, exchangeName, strat, num_top, percent_l
        )

    def execute_strat(
        self, graph_positions=False, print_terminal=False
    ) -> List[Opportunity]:
        self.strat.set_data(
            list_of_tickers=self.list_of_final_symbols,
            dict_of_dataframes=self.dict_of_dfs,
            exchangeName=self.exchangeName,
        )

        self.strat.instantiate_indicator_mgr()
        opps: List[Opportunity] = self.strat.run()
        opps = self.get_good_mix_of_opps(opps, self.num_top)[0]

        if print_terminal:
            for pos in opps:
                print(pos)

        # api = LiveTester.instantiate_alpaca_api()

        # # Spend $100 per trade
        # # check for fractional orders if short since it's not allowed
        # for opp in opps:
        #     if (qty := 100 // opp.default_price) == 0:
        #         continue

        #     try:
        #         api.submit_order(
        #             symbol=opp.ticker,
        #             qty=qty,
        #             side="buy" if opp.order_type == 1 else "sell",
        #             type="market",
        #             time_in_force="ioc",
        #         )
        #     except Exception as e:
        #         print(f"Error: {e}")

        return opps

    @staticmethod
    def instantiate_alpaca_api():
        BASE_URL = "https://paper-api.alpaca.markets"
        api_key, api_secret = LiveTester.get_alpaca_api_key()

        return tradeapi.REST(
            key_id=api_key,
            secret_key=api_secret,
            base_url=BASE_URL,
            api_version="v2",
        )

    @staticmethod
    def get_alpaca_api_key():
        resp = check_output(["datamgr", "show-config"])
        parsed_resp = resp.decode("utf-8").split("\n")
        api_key = parsed_resp[1].split("=")[1].strip()
        api_secret = parsed_resp[2].split("=")[1].strip()
        return api_key, api_secret
