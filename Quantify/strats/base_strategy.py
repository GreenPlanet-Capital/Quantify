from typing import List, Dict
import numpy as np

from pandas import DataFrame

from DataManager.utils.timehandler import TimeHandler
from Quantify.constants.timeframe import TimeFrame
from Quantify.indicators.indicator_manager import IndicatorManager

from Quantify.positions.opportunity import Opportunity
from Quantify.positions.position import Position


class BaseStrategy:

    def __init__(self, sid: int, name: str, timeframe: TimeFrame, lookback,
                 ) -> None:
        self.sid = sid
        self.name = name
        self.timeframe = timeframe
        self.lookback = lookback
        self.length_of_data_needed = max(self.timeframe.length, self.lookback)
        self.indicator_manager: IndicatorManager = None

    def set_data(self, list_of_tickers: list[str], dict_of_dataframes: dict[str, DataFrame], exchangeName: str):
        lengths = [len(df) for df in dict_of_dataframes.values()]
        max_rows = max(lengths)
        min_rows = min(lengths)
        # TODO Fix Data Manager
        assert all([max_rows == len(df) for df in
                    dict_of_dataframes.values()]), \
            "Lengths Mismatch: Not all dataframes in the dictionary are of the same length"
        assert min_rows >= self.timeframe.length, "Lengths Mismatch: Not enough entries supplied for this strategy"

        self.list_of_tickers = list_of_tickers
        self.dict_of_dataframes = dict_of_dataframes
        self.exchangeName = exchangeName

    def zero_data(self):
        self.list_of_tickers = None
        self.dict_of_dataframes = None

    def instantiate_indicator_mgr(self):
        pass

    def run(self):
        """
        Requires self.list_of_tickers and self.dict_of_dataframes to be set
        Returns a List of Opportunity objects or an empty List
        """
        assert self.list_of_tickers is not None, "DataNoneError: List of tickers not set for strategy"
        assert self.dict_of_dataframes is not None, "DataNoneError: Dict of Dataframes not set for strategy"

        self.indicator_manager.retrieve_scores(self.sid, self.name, self._score, self.dict_of_dataframes)
        opportunity_list = self.get_opportunity_list()

        opps_objects = self.generate_list_opportunities(opportunity_list)
        return sorted(opps_objects, key=lambda d: d.metadata['score'], reverse=True)

    def get_opportunity_list(self) -> List[dict]:
        # Gets the last entry of each ticker and bundles it
        opportunity_list = []
        for ticker, df in self.dict_of_dataframes.items():
            strat_id = self.sid
            timestamp = TimeHandler.get_clean_datetime_from_string(
                self.dict_of_dataframes[ticker]['timestamp'].iloc[-1])

            order_type = df['buy/sell signal'].iloc[-1]
            default_price = self.dict_of_dataframes[ticker]['close'].iloc[-1]
            score = df['score'].iloc[-1]

            opportunity_list.append(
                {
                    'strategy_id': strat_id,
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'exchangeName': self.exchangeName,
                    'order_type': order_type,
                    'default_price': default_price,
                    'score': score
                }
            )

        return opportunity_list

    def _generate_opportunity(self, dictionary: Dict) -> Opportunity:
        metadata = {'score': dictionary.pop('score')}
        return Opportunity(**dictionary, metadata=metadata)

    def generate_list_opportunities(self, list_opps) -> List[Opportunity]:
        opportunity_list = []
        for dictionary in list_opps:
            opportunity_list.append(self._generate_opportunity(dictionary))
        return opportunity_list

    def _score(self, input_df: DataFrame):
        return DataFrame()

    def health_check(self, cur_position: Position):
        assert cur_position.strategy_id == self.sid, "Strategy type of opportunity does not match the current strat"
        ticker, transaction_date = cur_position.ticker, cur_position.timestamp
        self.indicator_manager.retrieve_single_score(ticker, self.dict_of_dataframes, self._score)

        df_all_scores = self.dict_of_dataframes[ticker].copy()

        df_all_scores['health_score'] = 0.60 * df_all_scores['rsi_score'] + \
                                        0.40 * (1-df_all_scores['normalized macd'].replace({0:np.nan})).fillna(0)

        df_after_opp = df_all_scores[df_all_scores['timestamp'].apply
                                     (TimeHandler.get_datetime_from_string) > transaction_date]

        # Stop Health Score (20%)
        df_after_opp['current_peak_change_health'] = df_after_opp['health_score'].cummax()
        # TODO WHAT THIS
        df_after_opp['trailing_stop'] = df_after_opp['current_peak_change_health'] * (1 - 0.30)
        df_after_opp['exit_signal'] = df_after_opp['health_score'] < df_after_opp['trailing_stop']

        # Current stats
        df_after_opp['daily_percent_change_health'] = df_after_opp['health_score'].pct_change().fillna(0)
        df_after_opp['total_percent_change_health'] = \
            df_after_opp['daily_percent_change_health'].add(1).cumprod().sub(1)

        df_after_opp['daily_percent_change_price'] = df_after_opp['close'].pct_change().fillna(0)
        df_after_opp['total_percent_change_price'] = df_after_opp['daily_percent_change_price'].add(1).cumprod().sub(1)

        return df_after_opp

    def multiple_health_check(self, list_pos: List[Position]):
        dict_dfs = dict()
        for pos in list_pos:
            curr_health_df = self.health_check(pos)
            pos.health_df = curr_health_df
            dict_dfs[pos.ticker] = (curr_health_df, pos)
        return dict_dfs

    def __repr__(self) -> str:
        return self.name
