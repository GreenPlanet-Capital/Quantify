from itertools import zip_longest
import pandas as pd


def get_normalized_value(x, lower_bound, upper_bound, max_x, min_x):
    return (
        ((upper_bound - lower_bound) * (x - min_x))
        / ((max_x - min_x) if max_x != min_x else 1e-6)
    ) + lower_bound


def normalize_values(series: pd.Series, lower_bound, upper_bound) -> pd.Series:
    min_x = series.min()
    max_x = series.max()

    args = (lower_bound, upper_bound, max_x, min_x)
    series_out = series.apply(get_normalized_value, args=args)
    return series_out


def combine(*strings):
    str_list = [s for s in strings if s]
    lines = zip(*(s.splitlines() for s in str_list))
    return "\n".join("  ".join(line) for line in lines)


def n_wise(iterable, n=2):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip_longest(*[iter(a)] * n, fillvalue="")


def buy_sell_mva(x):
    if x > 0:
        return -1
    elif x < 0:
        return 1
    return 0


def buy_sell_rsi(x):
    if x > 50:
        return -1
    elif x <= 50:
        return 1


def find_loc(df, dates):
    marks = []
    for date in dates:
        marks.append(df.index[df["cleaned_timestamp"] == date])
    return marks
