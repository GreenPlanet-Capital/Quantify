from typing import List
from indicators.macd import Macd
from indicators.rsi import Rsi
from opportunity.opportunity import Opportunity
from strats.base_strategy import BaseStrategy

class Macd_Rsi(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.rsi = Rsi()
        self.macd = Macd()
    
    def run(self) -> List[Opportunity]:
        super().run()

