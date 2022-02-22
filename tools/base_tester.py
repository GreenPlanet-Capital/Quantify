from typing import Dict, List

from pandas import DataFrame

from positions.opportunity import Opportunity
from strats.base_strategy import BaseStrategy


class BaseTester:
    def __init__(self, list_of_final_symbols: List[str], dict_of_dfs: Dict[str, DataFrame], exchangeName: str,
                 strat: BaseStrategy, num_top: int):
        self.list_of_final_symbols = list_of_final_symbols
        self.dict_of_dfs = dict_of_dfs
        self.exchangeName = exchangeName
        self.strat = strat
        self.num_top = num_top

    def execute_strat(self, graph_positions=False, print_terminal=False) -> List[Opportunity]:
        return []
