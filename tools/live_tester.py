from typing import Dict, List
from positions.opportunity import Opportunity
from strats.base_strategy import BaseStrategy

def live_tester(list_of_final_symbols: List, dict_of_dfs: Dict, strat: BaseStrategy, exchangeName):
    strat.set_data(list_of_tickers=list_of_final_symbols,
                   dict_of_dataframes=dict_of_dfs,
                   exchangeName=exchangeName)
    opps: List[Opportunity] = strat.run()
    n_top = 5
    for pos in opps[:n_top]:
        print(pos)