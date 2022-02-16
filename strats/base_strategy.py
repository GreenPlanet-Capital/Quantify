from typing import List, Dict

from pandas import DataFrame

from DataManager.utils.timehandler import TimeHandler
from constants.timeframe import TimeFrame
from indicators.indicator_manager import IndicatorManager

from positions.opportunity import Opportunity
from positions.position import Position


class BaseStrategy:

    def __init__(self, sid: int, name: str, timeframe: TimeFrame, lookback,
                 ) -> None:
        self.sid = sid
        self.name = name
        self.timeframe = timeframe
        self.lookback = lookback
<<<<<<< HEAD
        self.indicator_manager: IndicatorManager = None

    def set_data(self, list_of_tickers: list[str], dict_of_dataframes: dict[str, DataFrame], exchangeName: str):
=======
        self.length_of_data_needed = max(timeframe.length, self.lookback)
    
    def set_data(self, list_of_tickers: list(), dict_of_dataframes: dict(), exchangeName: str):
>>>>>>> 2ee638f6e9b08f0c63e755c8547922f1e3309f6c
        lengths = [len(df) for df in dict_of_dataframes.values()]
        max_rows = max(lengths)
        min_rows = min(lengths)
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

    def health_check(self, cur_opportunity: Opportunity):
        assert cur_opportunity.strategy_id == self.sid, "Strategy type of opportunity does not match the current strat"
        ticker, transaction_date = cur_opportunity.ticker, cur_opportunity.timestamp
        self.indicator_manager.retrieve_single_score(ticker, self.dict_of_dataframes, self._score)

        df_all_scores = DataFrame()
        df_all_scores['score'] = 1 - self.dict_of_dataframes[ticker]['score']
        df_after_opp = df_all_scores[self.dict_of_dataframes[ticker]['timestamp'].apply
                                     (TimeHandler.get_datetime_from_string) > transaction_date]

        # Stop Score (20%)
        df_after_opp['highest'] = df_after_opp['score'].cummax()
        df_after_opp['trailing_stop'] = df_after_opp['highest'] * (1 - 0.20)
        df_after_opp['exit_signal'] = df_after_opp['score'] < df_after_opp['trailing_stop']

        return df_after_opp

    def multiple_health_check(self, list_pos: List[Position]):
        dict_dfs = dict()
        for pos in list_pos:
            dict_dfs[pos.ticker] = (self.health_check(pos), pos)
        return dict_dfs

    def __repr__(self) -> str:
        return self.name
