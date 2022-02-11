from indicators.base_indicator import BaseIndicator


class Macd(BaseIndicator):
    def run(self):
        super().run()
        
        self._zero_dataframe()