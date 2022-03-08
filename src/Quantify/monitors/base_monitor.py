from typing import List

from pandas import DataFrame

from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy


class BaseMonitor:
    def __init__(self, sid: int, name: str, strat: BaseStrategy):
        self.sid = sid
        self.name = name
        self.strat = strat

    def health_check(self, cur_position: Position) -> DataFrame:
        assert (
            cur_position.strategy_id == self.sid
        ), "Strategy type of opportunity does not match the current strat"
        return DataFrame()

    def multiple_health_check(self, list_pos: List[Position]):
        dict_dfs = dict()
        for pos in list_pos:
            curr_health_df = self.health_check(pos)
            pos.health_df = curr_health_df
            dict_dfs[pos.ticker] = (curr_health_df, pos)
        return dict_dfs
