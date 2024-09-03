from datetime import timedelta
from typing import List
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import delta, gamma, rho, theta, vega
from py_lets_be_rational.exceptions import BelowIntrinsicException
import pandas as pd
from dataclasses import dataclass
from DataManager.utils.timehandler import TimeHandler
import traceback


# FIXME: this calculates for european options only
def greek_val(flag, S, K, t, r, sigma):
    """
    price (float) - the Black-Scholes option price
    S (float) - underlying asset price
    sigma (float) - annualized standard deviation, or volatility
    K (float) - strike price
    t (float) - time to expiration in years
    r (float) - risk-free interest rate
    flag (str) - 'c' or 'p' for call or put.
    """
    price = bs(flag, S, K, t, r, sigma)
    imp_v = iv(price, S, K, t, r, flag)
    delta_calc = delta(flag, S, K, t, r, sigma)
    gamma_calc = gamma(flag, S, K, t, r, sigma)
    rho_calc = rho(flag, S, K, t, r, sigma)
    theta_calc = theta(flag, S, K, t, r, sigma)
    vega_calc = vega(flag, S, K, t, r, sigma)
    return price, imp_v, theta_calc, delta_calc, rho_calc, vega_calc, gamma_calc


@dataclass
class OptionsDfParams:
    call_or_put: str
    strike_price: float
    expiration_date_days: float


def get_options_df(
    s: pd.Series, options_params: List[OptionsDfParams], annual_std: float
) -> pd.DataFrame:
    r = 0.07  # TODO - check if this is the correct risk free rate
    res: List[pd.Series] = []

    for param in options_params:
        cur = s.copy()

        cur["strike"] = param.strike_price
        cur["expiration"] = TimeHandler.get_datetime_from_string(
            cur["timestamp"]
        ) + timedelta(days=param.expiration_date_days)

        try:
            gv = greek_val(
                param.call_or_put,
                cur["close"],
                cur["strike"],
                param.expiration_date_days / 365,
                r,
                annual_std,
            )
        except Exception:
            print(f"Error while computing greek val: {traceback.format_exc()}")
            continue

        price, imp_v, theta_calc, delta_calc, rho_calc, vega_calc, gamma_calc = gv

        cur["mark"] = price
        cur["vol"] = imp_v
        cur["theta"] = theta_calc
        cur["delta"] = delta_calc
        cur["rho"] = rho_calc
        cur["vega"] = vega_calc
        cur["gamma"] = gamma_calc

        cur["call_put"] = "Call" if param.call_or_put == "c" else "Put"

        res.append(cur)

    return pd.DataFrame(res)
