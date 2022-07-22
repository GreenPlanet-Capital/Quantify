from typing import Any, List, Dict
from pandas import DataFrame
from DataManager.utils.timehandler import TimeHandler
from Quantify.constants.timeframe import TimeFrame
from Quantify.indicators.indicator_manager import IndicatorManager

from Quantify.positions.opportunity import Opportunity


class BaseStrategy:

    indicator_manager: IndicatorManager
    list_of_tickers: List[str]
    dict_of_dataframes: Dict[str, DataFrame]

    def __init__(
        self,
        sid: int,
        name: str,
        timeframe: TimeFrame,
        lookback,
    ) -> None:
        self.sid = sid
        self.name = name
        self.timeframe = timeframe
        self.lookback = lookback
        self.length_of_data_needed = max(self.timeframe.length, self.lookback)
        self.list_of_tickers = []
        self.dict_of_dataframes = dict()

    def set_data(
        self,
        list_of_tickers: list[str],
        dict_of_dataframes: dict[str, DataFrame],
        exchangeName: str,
    ):
        lengths = [len(df) for df in dict_of_dataframes.values()]
        max_rows = max(lengths)
        min_rows = min(lengths)

        assert all(
            [max_rows == len(df) for df in dict_of_dataframes.values()]
        ), "Lengths Mismatch: Not all dataframes in the dictionary are of the same length"
        assert (
            min_rows >= self.timeframe.length
        ), "Lengths Mismatch: Not enough entries supplied for this strategy"

        self.list_of_tickers = list_of_tickers
        self.dict_of_dataframes = dict_of_dataframes
        self.exchangeName = exchangeName

    def zero_data(self):
        self.list_of_tickers = []
        self.dict_of_dataframes = dict()

    def instantiate_indicator_mgr(self):
        pass

    def run(self):
        """
        Requires self.list_of_tickers and self.dict_of_dataframes to be set
        Returns a List of Opportunity objects or an empty List
        """
        assert (
            self.list_of_tickers is not None
        ), "DataNoneError: List of tickers not set for strategy"
        assert (
            self.dict_of_dataframes is not None
        ), "DataNoneError: Dict of Dataframes not set for strategy"

        self.indicator_manager.retrieve_scores(
            self.sid, self.name, self._score, self.dict_of_dataframes
        )
        opportunity_list = self.get_opportunity_list()

        opps_objects = self.generate_list_opportunities(opportunity_list)
        opps_objects = sorted(
            opps_objects, key=lambda d: d.metadata["score"], reverse=True
        )
        return opps_objects

    def get_opportunity_list(self) -> List[Dict[str, Any]]:
        # Gets the last entry of each ticker and bundles it
        opportunity_list = []
        for ticker, df in self.dict_of_dataframes.items():
            strat_id = self.sid
            timestamp = TimeHandler.get_clean_datetime_from_string(
                self.dict_of_dataframes[ticker]["timestamp"].iloc[-1]
            )

            order_type = df["buy/sell signal"].iloc[-1]
            default_price = self.dict_of_dataframes[ticker]["close"].iloc[-1]
            score = df["score"].iloc[-1]

            opportunity_list.append(
                {
                    "strategy_id": strat_id,
                    "timestamp": timestamp,
                    "ticker": ticker,
                    "exchangeName": self.exchangeName,
                    "order_type": order_type,
                    "default_price": default_price,
                    "score": score,
                }
            )

        return opportunity_list

    def _generate_opportunity(self, dictionary: Dict[str, Any]) -> Opportunity:
        metadata = {"score": dictionary.pop("score")}
        return Opportunity(**dictionary, metadata=metadata)

    def generate_list_opportunities(self, list_opps) -> List[Opportunity]:
        opportunity_list = []
        for dictionary in list_opps:
            opportunity_list.append(self._generate_opportunity(dictionary))
        return opportunity_list

    def _score(self, input_df: DataFrame):
        return DataFrame()

    def __repr__(self) -> str:
        return self.name
