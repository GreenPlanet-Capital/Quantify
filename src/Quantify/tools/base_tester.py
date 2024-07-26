from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from Quantify.positions.opportunity import Opportunity
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy


class BaseTester:
    def __init__(
        self,
        list_of_final_symbols: List[str],
        dict_of_dfs: Dict[str, DataFrame],
        exchangeName: str,
        strat: BaseStrategy,
        num_top: int,
        percent_l: float,
    ):
        self.list_of_final_symbols = list_of_final_symbols
        self.dict_of_dfs = dict_of_dfs
        self.exchangeName = exchangeName
        self.strat = strat
        self.num_top = num_top
        self.percent_l = percent_l

    def get_good_mix_of_opps(self, opps: List[Opportunity], num_opps: int) -> Tuple[List[Opportunity], int]:
        n_longs_req = int(self.percent_l * num_opps)
        n_shorts_req = num_opps - n_longs_req
        mixed_opps: List[Opportunity] = []
        last_op_idx = -1

        for op_idx, op in enumerate(opps):
            op_order_type = op.order_type
            if op_order_type == 1:
                if n_longs_req != 0:
                    n_longs_req -= 1
                    last_op_idx = op_idx
                else:
                    continue
            elif op_order_type == -1:
                if n_shorts_req != 0:
                    n_shorts_req -= 1
                    last_op_idx = op_idx
                else:
                    continue
            else:  # ignore order type of 0
                continue

            mixed_opps.append(op)
            if not (n_longs_req or n_shorts_req):
                break
        return mixed_opps, last_op_idx

    def execute_strat(
        self, graph_positions=False, print_terminal=False
    ) -> Union[List[Opportunity], List[Position]]:
        pass
