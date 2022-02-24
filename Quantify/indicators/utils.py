import numpy as np


class IndicUtils:

    @staticmethod
    def account_for_buy_sell_signal(value, signal):
        if signal == 1:
            return 1 - value
        return value

    @staticmethod
    def nan_out_between_range(x, lower_limit, upper_limit):
        if x >= lower_limit and x <= upper_limit:
            return np.nan
        return x

    @staticmethod
    def constrain(x, lower_limit, upper_limit):
        if x >= lower_limit and x <= upper_limit:
            return x
        return 0