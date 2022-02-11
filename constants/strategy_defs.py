import inspect
from constants.timeframe import TimeFrame
from strats.macd_rsi import Macd_Rsi


def get_strategy_definitons():
    """
    Returns
    1. strat_name_to_id mapping
    2. strat_id_to_class mapping
    3. strat_id_to_TimeFrame mapping
    """
    strat_name_to_id = {
    "MACD_RSI": 0
    }

    strat_id_to_TimeFrame = {
        0: TimeFrame(27, '1Day')
    }

    assert len(strat_name_to_id)==len(strat_id_to_TimeFrame), "Lengths Mismatch: Add a strategy to both strat_name_to_id and strat_id_to_TimeFrame"

    class Strategies:
        def macd_rsi(self):
            return Macd_Rsi()

    assert len(strat_name_to_id) == \
        len(inspect.getmembers(Strategies, inspect.isfunction)), "Lengths Mismatch: Add a strategy to both strat_name_to_id and the Strategies class"

    strats = Strategies()

    strat_id_to_class = { 
        id: getattr(strats, name.lower())(strat_id_to_TimeFrame[id])
        for name, id in strat_name_to_id.items()
    }

    return strat_name_to_id, strat_id_to_class, strat_id_to_TimeFrame