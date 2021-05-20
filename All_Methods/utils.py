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
    return records_df


def save_excel(records_df, FILENAME, METHOD_TAG):
    if len(records_df) > 0:
        FILE = FILENAME.split("/")[-1].split(".")[0]
        EXCEL_NAME = f"./RESULT_EXCELS/{FILE}_{METHOD_TAG}.xlsx"
        print(f"The transactions will be saved into {EXCEL_NAME} :)")
        records_df.to_excel(EXCEL_NAME)


def get_final_profit(df, data):
    temp = df.tail(1).iloc[0]
    last_data = data.tail(1).iloc[0]
    if temp["Action"] == "Buying":
        final_profit = (last_data["Close"] - temp["Price"]) * temp["n"] + temp["Profit"]
    else:
        final_profit = temp["Profit"]
    return final_profit


def get_dumb_profit(data, BEGINNING_CASH):
    begin = data.iloc[0]
    end = data.tail(1).iloc[0]
    n = BEGINNING_CASH / begin["Close"]
    profit = (end["Close"] - begin["Close"]) * n
    return profit


def dealing_results(
    records_df, FILENAME, BEGINNING_CASH, final_profit, data, METHOD_TAG
):
    records_df["Hour"] = pd.to_datetime(records_df["Hour"])
    save_excel(records_df=records_df, FILENAME=FILENAME, METHOD_TAG=METHOD_TAG)
    dumb_profit = get_dumb_profit(data=data, BEGINNING_CASH=BEGINNING_CASH)
    difference = final_profit - dumb_profit
    print(
        f"\nFinal Profit: {final_profit}\nDumb Profit: {dumb_profit}\nDifference: {difference}\n"
    )
    print(records_df)
    return dumb_profit, difference
