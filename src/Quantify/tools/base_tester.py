from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple, Union
import warnings

from pandas import DataFrame
from tqdm import tqdm

from Quantify.positions.opportunity import Opportunity
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy
from DataManager.utils.timehandler import TimeHandler
from DataManager.datamgr.options_extractor import OptionsExtractor
from Quantify.constants.op_utils import OptionsDfParams, get_options_df

OPTIONS_TABLE = "option_chain"
VOL_WINDOW_SIZE = 21


@dataclass
class OptionsParams:
    limit_per_ticker: int
    max_mark_for_option: float
    min_mark_for_option: float
    num_contracts: int


class BaseTester:
    def __init__(
        self,
        list_of_final_symbols: List[str],
        dict_of_dfs: Dict[str, DataFrame],
        exchangeName: str,
        strat: BaseStrategy,
        num_top: int,
        percent_l: float,
        options_params: OptionsParams = None,
    ):
        self.list_of_final_symbols = list_of_final_symbols
        self.dict_of_dfs = dict_of_dfs
        self.exchangeName = exchangeName
        self.strat = strat
        self.num_top = num_top
        self.percent_l = percent_l

        self.options_params = options_params
        if self.options_params is not None:
            self.ope = OptionsExtractor()
            self.common_tickers = set(self.dict_of_dfs.keys()).intersection(
                self.ope.tickers
            )

    def get_good_mix_of_opps(
        self, opps: List[Opportunity], num_opps: int
    ) -> Tuple[List[Opportunity], int]:
        n_longs_req = int(self.percent_l * num_opps)
        n_shorts_req = num_opps - n_longs_req
        mixed_opps: List[Opportunity] = []

        for op in opps:
            op_order_type = op.order_type
            if op_order_type == 1:
                if n_longs_req != 0:
                    n_longs_req -= 1
                else:
                    continue
            elif op_order_type == -1:
                if n_shorts_req != 0:
                    n_shorts_req -= 1
                else:
                    continue
            else:  # ignore order type of 0
                continue

            mixed_opps.append(op)
            if not (n_longs_req or n_shorts_req):
                break

        return mixed_opps

    def execute_strat(
        self, graph_positions=False, print_terminal=False
    ) -> Union[List[Opportunity], List[Position]]:
        raise NotImplementedError("execute_strat must be implemented in child classes")

    @staticmethod
    def get_annual_std(df: DataFrame) -> float:
        unique_df = df.drop_duplicates("timestamp")
        unique_df["date"] = unique_df["timestamp"].apply(
            TimeHandler.get_datetime_from_string
        )

        last_dt: datetime = unique_df["date"].max()
        unique_df = unique_df[unique_df["date"].dt.year == last_dt.year]

        return (
            unique_df["close"].pct_change().rolling(VOL_WINDOW_SIZE).std()
            * (len(unique_df) ** 0.5)
        ).iloc[-1]

    def optionize_opportunity(self, opportunity: Opportunity) -> bool:
        df_opp = self.dict_of_ops[opportunity.ticker]
        df_time = df_opp[
            df_opp["timestamp"]
            == TimeHandler.get_string_from_datetime(opportunity.timestamp)
        ]

        if df_time["bid"].isnull().values.all():
            days_buffer = timedelta(days=10)  # TODO - check if this is a good buffer
            start_dt = opportunity.timestamp - days_buffer
            end_dt = opportunity.timestamp + days_buffer

            neigh_df = df_opp[
                (df_opp["timestamp"] >= TimeHandler.get_string_from_datetime(start_dt))
                & (df_opp["timestamp"] <= TimeHandler.get_string_from_datetime(end_dt))
            ]
            neigh_options = neigh_df[neigh_df["bid"].notnull()]
            neigh_options = neigh_options.drop_duplicates(
                subset=["strike", "expiration", "call_put"]
            )

            if neigh_options.empty:
                return False

            op_params = [
                OptionsDfParams(
                    call_or_put=neigh_s["call_put"].lower()[0],
                    strike_price=neigh_s["strike"],
                    expiration_date_days=max(
                        1, (neigh_s["expiration"] - neigh_s["date"]).days
                    ),
                )
                for _, neigh_s in neigh_options.iterrows()
            ]

            # FIXME: check if this is the correct way to calculate annual std
            avail_options = get_options_df(
                df_time.iloc[0],
                op_params,
                self.get_annual_std(df_opp),
            )
        else:
            avail_options = df_time[df_time["bid"].notnull()]
            avail_options["mark"] = (avail_options["bid"] + avail_options["ask"]) / 2

        if opportunity.order_type == 1:
            avail_options = avail_options[avail_options["call_put"] == "Call"]
        else:
            avail_options = avail_options[avail_options["call_put"] == "Put"]

        avail_options = avail_options[
            (avail_options["mark"] <= self.options_params.max_mark_for_option)
            & (avail_options["mark"] >= self.options_params.min_mark_for_option)
        ]

        if avail_options.empty:
            return False

        # TODO: optimize later, for now go with the scoreth opportunity after sorting by mark
        avail_options = avail_options.sort_values("mark", ascending=True)
        score = opportunity.metadata["score"]

        pick_idx = int(score * (len(avail_options) - 1))
        pick_option = avail_options.iloc[pick_idx]

        opportunity.metadata["mark"] = pick_option["mark"]
        opportunity.metadata["strike"] = pick_option["strike"]
        opportunity.metadata["expiration"] = TimeHandler.get_string_from_datetime(
            pick_option["expiration"]
        )

        return True

    def get_options_dt_range(self) -> Tuple[datetime, datetime]:
        dt_range = self.dict_of_dfs[self.list_of_final_symbols[0]]["timestamp"].apply(
            TimeHandler.get_datetime_from_string
        )
        return (
            dt_range.min() + timedelta(days=self.strat.timeframe.length),
            dt_range.max(),
        )

    def combine_df_with_options(self):
        dt_range = self.get_options_dt_range()
        self.dict_of_ops: Dict[str, DataFrame] = dict()

        warnings.filterwarnings("ignore", category=UserWarning)
        for symbol in tqdm(
            self.list_of_final_symbols, desc="Fetching options dataframes"
        ):
            op_query = self.ope.construct_query(
                table=OPTIONS_TABLE,
                ticker=symbol,
                date_range=dt_range,
                limit=self.options_params.limit_per_ticker,
            )
            df_op = self.ope.get_query_result_pd(op_query)
            df_op["timestamp"] = df_op["date"].apply(
                TimeHandler.get_string_from_datetime
            )

            self.dict_of_ops[symbol] = pd.merge(
                self.dict_of_dfs[symbol], df_op, on="timestamp", how="left"
            )

        warnings.filterwarnings("default", category=UserWarning)
