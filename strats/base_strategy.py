from typing import List, Optional

from opportunity.opportunity import Opportunity


class BaseStrategy:
    
    def set_data(self, list_of_tickers: list(), dict_of_dataframes: dict()):
        self.list_of_tickers = list_of_tickers
        self.dict_of_dataframes = dict_of_dataframes

    def _zero_data(self):
        self.list_of_tickers = None
        self.dict_of_dataframes = None

    def run(self) -> List[Opportunity]:
        assert self.list_of_tickers is not None, "DataNoneError: List of tickers not set for strategy"
        assert self.dict_of_dataframes is not None, "DataNoneError: Dict of Dataframes not set for strategy"