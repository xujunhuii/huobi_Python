import pandas as pd
import numpy as np


def calc_RSV(prices, INTERVALS_FOR_RSV):
    C = prices
    H = prices.rolling(INTERVALS_FOR_RSV).max()
    L = prices.rolling(INTERVALS_FOR_RSV).min()
    RSV = (C - L) / (H - L)
    return RSV


def calc_bbands(prices, INTERVAL_FOR_BOUNDS, SD_PARAMETER):
    if len(prices) < INTERVAL_FOR_BOUNDS:
        INTERVAL_FOR_BOUNDS = 1 * 24 * 60
    middle_vals = prices.rolling(INTERVAL_FOR_BOUNDS).mean()
    std_vals = prices.rolling(INTERVAL_FOR_BOUNDS).std(ddof=0)
    upper_vals = middle_vals + SD_PARAMETER * std_vals
    lower_vals = middle_vals - SD_PARAMETER * std_vals
    return upper_vals, middle_vals, lower_vals


def calc_ATRP(high, low, close, n=15 * 24 * 60):
    if len(close) < 15 * 24 * 60:
        n = 1 * 24 * 60
    high_low = high - low
    high_cp = np.abs(high - close.shift())
    low_cp = np.abs(low - close.shift())

    df = pd.concat([high_low, high_cp, low_cp], axis=1)
    true_range = np.max(df, axis=1)
    average_true_range = true_range.rolling(n).mean()
    average_true_range_percentage = average_true_range / close

    return average_true_range_percentage


def check_last_row(records_df):
    temp = records_df.tail(1)
    last_action = temp.iloc[0]["Action"]
    if last_action == "Buying":
        records_df = records_df.iloc[:-1, :]
    return records_df


def generate_records_df(records):
    records_df = pd.DataFrame(
        records,
        columns=[
            "Action",
            "Price",
            "n",
            "Cash",
            "Profit",
            "LowerBound",
            "UpperBound",
            "Rate",
            "Hour",
        ],
    )
    records_df = check_last_row(records_df)
    return records_df
