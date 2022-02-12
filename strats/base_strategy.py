from time import time
from typing import List, Optional
from constants.timeframe import TimeFrame

from opportunity.opportunity import Opportunity


class BaseStrategy:

    def __init__(self, timeframe: TimeFrame, lookback) -> None:
        self.timeframe = timeframe
        self.lookback = lookback
    
    def set_data(self, list_of_tickers: list(), dict_of_dataframes: dict()):
        lengths = [len(df) for df in dict_of_dataframes.values()]
        max_rows = max(lengths)
        min_rows = min(lengths)
        assert all([max_rows==len(df) for df in dict_of_dataframes.values()]), "Lengths Mismatch: Not all dataframes in the dictionary are of the same length"
        assert min_rows>=self.timeframe.length
        
        self.list_of_tickers = list_of_tickers
        self.dict_of_dataframes = dict_of_dataframes

    def _zero_data(self):
        self.list_of_tickers = None
        self.dict_of_dataframes = None

    def run(self) -> List[Opportunity]:
        assert self.list_of_tickers is not None, "DataNoneError: List of tickers not set for strategy"
        assert self.dict_of_dataframes is not None, "DataNoneError: Dict of Dataframes not set for strategy"