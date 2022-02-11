import os, sys
sys.path.append(os.getcwd())
from strats.macd_rsi import Macd_Rsi

strat_name_to_id = dict()
strat_id_to_class = dict()

def setup_strategies():
    global strat_name_to_id
    global strat_id_to_class
    strat_name_to_id = {
    "MACD_RSI": 0
    }
    class Strategies:
        def macd_rsi(self):
            return Macd_Rsi()
    
    strats = Strategies()

    strat_id_to_class = { 
    id: getattr(strats, name.lower())()
    for name, id in strat_name_to_id.items()
    }


def main():
    setup_strategies()
    print()

if __name__ == '__main__':
    main()