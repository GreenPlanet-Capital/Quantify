import pandas as pd

def get_normalized_value(x, lower_bound, upper_bound, max_x, min_x):
    return ((upper_bound-lower_bound)*(x - min_x))/(max_x - min_x) + lower_bound

def normalize_values(series: pd.Series, lower_bound, upper_bound) -> pd.Series:
    min_x = series.min()
    max_x = series.max()

    args = (lower_bound, upper_bound, max_x, min_x)
    series_out = series.apply(get_normalized_value, args=args)
    return series_out

def buy_sell_mva(x):
    if x > 0:
        return -1
    elif x < 0:
        return 1
    return 0


def find_loc(df, dates):
    marks = []
    for date in dates:
        marks.append(df.index[df['cleaned_timestamp'] == date])
    return marks

