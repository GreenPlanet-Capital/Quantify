import inspect
from Quantify.constants.timeframe import TimeFrame
from Quantify.strats.macd_rsi import Macd_Rsi
from Quantify.strats.macd_rsi_boll import Macd_Rsi_Boll


def get_strategy_definitons():
    """
    Returns
    1. strat_id_to_name mapping
    2. strat_id_to_class mapping
    3. strat_id_to_TimeFrame mapping
    """
    strat_id_to_name = {
        0: "MACD_RSI",
        1: "MACD_RSI_BOLL"
    }

    strat_id_to_TimeFrame = {
        0: TimeFrame(100, '1Day'),
        1: TimeFrame(100, '1Day')
    }

    assert len(strat_id_to_name) == len(strat_id_to_TimeFrame), "Lengths Mismatch: Add a strategy to both " \
                                                                "strat_name_to_id and strat_id_to_TimeFrame "

    strat_id_to_lookback = {
        0: 100,
        1: 100
    }

    assert len(strat_id_to_name) == len(strat_id_to_TimeFrame), "Lengths Mismatch: Add a strategy to both " \
                                                                "strat_name_to_id and strat_id_to_lookback "

    class Strategies:
        def macd_rsi(self, sid, name, timeframe: TimeFrame, lookback):
            return Macd_Rsi(sid, name, timeframe, lookback)

        def macd_rsi_boll(self, sid, name, timeframe: TimeFrame, lookback):
            return Macd_Rsi_Boll(sid, name, timeframe, lookback)

    assert len(strat_id_to_name) == \
           len(inspect.getmembers(Strategies,
                                  inspect.isfunction)), "Lengths Mismatch: Add a strategy to both strat_name_to_id " \
                                                        "and the Strategies class "

    strats = Strategies()

    strat_id_to_class = {
        id: getattr(strats, name.lower())(id, name, strat_id_to_TimeFrame[id], strat_id_to_lookback[id])
        for id, name in strat_id_to_name.items()
    }

    return strat_id_to_name, strat_id_to_class, strat_id_to_TimeFrame
