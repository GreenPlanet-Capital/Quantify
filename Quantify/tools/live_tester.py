from typing import Dict, List
from pandas import DataFrame
from Quantify.positions.opportunity import Opportunity
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.base_tester import BaseTester


class LiveTester(BaseTester):
    def __init__(self, list_of_final_symbols: List[str], dict_of_dfs: Dict[str, DataFrame], exchangeName: str,
                 strat: BaseStrategy, num_top: int, percent_l: float):
        super().__init__(list_of_final_symbols, dict_of_dfs, exchangeName, strat, num_top, percent_l)

    def execute_strat(self, graph_positions=False, print_terminal=False) -> List[Opportunity]:
        self.strat.set_data(list_of_tickers=self.list_of_final_symbols,
                            dict_of_dataframes=self.dict_of_dfs,
                            exchangeName=self.exchangeName)

        self.strat.instantiate_indicator_mgr()
        opps: List[Opportunity] = self.strat.run()
        opps = self.get_good_mix_of_opps(opps)

        if print_terminal:
            for pos in opps:
                print(pos)

        return opps
