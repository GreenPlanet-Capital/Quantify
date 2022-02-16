from typing import Dict, List
from pandas import DataFrame
from positions.opportunity import Opportunity
from strats.base_strategy import BaseStrategy
from tools.base_tester import BaseTester


class LiveTester(BaseTester):
    def __init__(self, list_of_final_symbols: [str], dict_of_dfs: Dict[str, DataFrame], exchangeName: str,
                 strat: BaseStrategy, num_top: int):
        super().__init__(list_of_final_symbols, dict_of_dfs, exchangeName, strat, num_top)

    def execute_strat(self, graph_positions=True):
        self.strat.set_data(list_of_tickers=self.list_of_final_symbols,
                            dict_of_dataframes=self.dict_of_dfs,
                            exchangeName=self.exchangeName)

        self.strat.instantiate_indicator_mgr()
        opps: List[Opportunity] = self.strat.run()

        for pos in opps[:self.num_top]:
            print(pos)
