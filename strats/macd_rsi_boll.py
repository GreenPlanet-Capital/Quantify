from datetime import datetime
from pprint import pprint
from typing import Dict, List, AnyStr
from xml.sax import default_parser_list
from tqdm import tqdm
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from DataManager.utils.timehandler import TimeHandler
from constants.timeframe import TimeFrame
from constants.utils import normalize_values
from indicators.macd import Macd
from indicators.rsi import Rsi
from indicators.bollinger_bands import BollingerBands
from positions.opportunity import Opportunity
from positions.position import Position
from strats.base_strategy import BaseStrategy
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal


class Macd_Rsi_Boll(BaseStrategy):
    def __init__(self, sid, name, timeframe: TimeFrame, lookback) -> None:
        super().__init__(sid, name, timeframe, lookback)
        self.rsi = Rsi()
        self.macd = Macd(lower_ma=12, upper_ma=26, signal_length=9)
        self.boll = BollingerBands(num_periods=20)

    def run(self) -> List[Opportunity]:
        """
        Requires self.list_of_tickers and self.dict_of_dataframes to be set
        Returns a List of Opportunity objects or an empty List
        """
        super().run()

        ticker_to_score_df: Dict[str, pd.DataFrame] = dict()

        for ticker in tqdm(self.list_of_tickers, desc=f"{self.sid}: {self.name} "):
            # FIXME: An arbitary price of 80 was chosen here
            # if self.dict_of_dataframes[ticker]['close'].mean() < 80:
            #     ticker_to_score_df[ticker] = pd.DataFrame([[0, 0]], columns = ['Score', 'Buy/Sell Signal'])
            #     continue
            self.rsi.set_dataframe(self.dict_of_dataframes[ticker])
            self.macd.set_dataframe(self.dict_of_dataframes[ticker])
            self.boll.set_dataframe(self.dict_of_dataframes[ticker])
            ticker_to_score_df[ticker] = self._score()

        print()

        # Gets the last entry of each ticker and bundles it
        opportunity_list = []
        for ticker, df in ticker_to_score_df.items():
            strat_id = self.sid
            timestamp = TimeHandler.get_datetime_from_alpaca_string(
                TimeHandler.get_alpaca_string_from_string(
                    self.dict_of_dataframes[ticker]['timestamp'].iloc[-1]
                )
            )
            order_type = df['Buy/Sell Signal'].iloc[-1]
            default_price = self.dict_of_dataframes[ticker]['close'].iloc[-1]
            score = df['Score'].iloc[-1]

            opportunity_list.append(
                {
                    'strategy_id': strat_id,
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'order_type': order_type,
                    'default_price': default_price,
                    'score': score
                }
            )

        score_df = pd.DataFrame(opportunity_list)

        score_df.sort_values(by='score', ascending=False, inplace=True)
        # print(score_df)
        score_df.to_csv('results.csv')

        opportunities = []
        for dictionary in opportunity_list:
            opportunities.append(self._generate_opportunity(dictionary))

        self._zero_data()
        opportunities.sort(key=lambda d: d.metadata['score'], reverse=True)

        return opportunities

    def _score(self) -> pd.Series:
        # Store list timestamps
        list_timestamps = self.macd._dataframe['timestamp']

        rsi: pd.DataFrame = self.rsi.run()
        macd: pd.DataFrame = self.macd.run()
        boll: pd.DataFrame = self.boll.run()

        indicators_df = pd.concat([rsi, macd, boll], axis=1)
        indicators_df['timestamp'] = list_timestamps

        # Shifting RSI down by one
        indicators_df['Shifted RSI'] = indicators_df['rsi'].shift(1)
        indicators_df['Buy/Sell Signal'] = 0

        def buy_sell(x):
            if x > 0:
                return -1
            elif x < 0:
                return 1
            return 0

        # Calculate +1 for buy and -1 for sell
        indicators_df['Buy/Sell Signal'] = indicators_df['MACD'].apply(buy_sell)

        # for i, row in indicators_df.iterrows():
        #     if (i==0):
        #         continue
        #     macd_val = indicators_df.iloc[i-1]['MACD']
        #     macd_signal_val = indicators_df.iloc[i-1]['MACD Signal Line']

        #     if macd_val > macd_signal_val:
        #         signal = -1
        #     elif macd_val < macd_signal_val:
        #         signal = 1
        #     else:
        #         signal = 0

        #     indicators_df.at[i,'Buy/Sell Signal'] = signal

        # Calculate score
        indicators_df['Score'] = 0.25 * indicators_df['Shifted RSI'] / 100 + \
                                 0.25 * indicators_df['Normalized difference'] + 0.25 * indicators_df[
                                     'Normalized MACD'] + \
                                 0.25 * indicators_df['diff_bb']

        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        # print(indicators_df[['Score', 'Buy/Sell Signal']])

        return indicators_df[['Score', 'Buy/Sell Signal', 'timestamp']]

    def _generate_opportunity(self, dictionary: Dict) -> List[Opportunity]:
        metadata = {'score': dictionary.pop('score')}
        return Opportunity(**dictionary, metadata=metadata)

    def health_check(self, cur_opportunity: Opportunity):
        assert cur_opportunity.strategy_id == self.sid, "Strategy type of opportunity does not match the current strat"
        ticker, transaction_date = cur_opportunity.ticker, cur_opportunity.timestamp

        self.rsi.set_dataframe(self.dict_of_dataframes[ticker])
        self.macd.set_dataframe(self.dict_of_dataframes[ticker])
        self.boll.set_dataframe(self.dict_of_dataframes[ticker])

        df_all_scores = self._score()
        df_all_scores['Score'] = 1 - df_all_scores['Score']
        df_after_opp = df_all_scores[df_all_scores['timestamp'] >
                                     TimeHandler.get_string_from_timestamp(transaction_date)]

        # Plot order graph
        # pd.options.plotting.backend = "plotly"
        # fig = df_after_opp.plot(x='timestamp', y='Score')
        # fig.show()

        # Stop Score (20%)
        df_after_opp['highest'] = df_after_opp['Score'].cummax()
        df_after_opp['trailing_stop'] = df_after_opp['highest'] * (1 - 0.20)
        df_after_opp['exit_signal'] = df_after_opp['Score'] < df_after_opp['trailing_stop']

        return df_after_opp

    def multiple_health_check(self, list_pos: List[Position]):
        dict_dfs = dict()
        for pos in list_pos:
            dict_dfs[pos.ticker] = (self.health_check(pos), pos)
        self._zero_data()
        return dict_dfs
