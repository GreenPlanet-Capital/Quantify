from typing import List, Dict
from pandas import DataFrame
from tqdm import tqdm

from Quantify.indicators.base_indicator import BaseIndicator


class IndicatorManager:
    def __init__(self, list_indicators: List[BaseIndicator], list_tickers: List[str]):
        self.list_indicators = list_indicators
        self.list_of_tickers = list_tickers

    def retrieve_scores(
        self,
        sid_strategy: int,
        name_strategy: str,
        score_func,
        dict_of_dataframes: Dict[str, DataFrame],
    ):

        for ticker in tqdm(
            self.list_of_tickers, desc=f"{sid_strategy}: {name_strategy} "
        ):
            # FIXME: An arbitrary minimum dollar volume of $25M was chosen here
            if (
                dict_of_dataframes[ticker]["volume"]
                * dict_of_dataframes[ticker]["close"]
            ).mean() > 35_000_000:
                dict_of_dataframes[ticker][["score", "buy/sell signal"]] = 0
                continue
            self.retrieve_single_score(ticker, dict_of_dataframes, score_func)

    def retrieve_single_score(self, ticker_name, dict_of_dataframes, score_func):
        for indicator in self.list_indicators:
            indicator.run(dict_of_dataframes[ticker_name])
        dict_of_dataframes[ticker_name]["score"] = score_func(
            dict_of_dataframes[ticker_name]
        )["score"]
