import pandas as pd


def calc_bbands(prices, INTERVAL_FOR_BOUNDS, SD_PARAMETER):
    if len(prices) < INTERVAL_FOR_BOUNDS:
        INTERVAL_FOR_BOUNDS = 1 * 24 * 60
    middle_vals = prices.rolling(INTERVAL_FOR_BOUNDS).mean()
    std_vals = prices.rolling(INTERVAL_FOR_BOUNDS).std(ddof=0)
    upper_vals = middle_vals + SD_PARAMETER * std_vals
    lower_vals = middle_vals - SD_PARAMETER * std_vals
    return upper_vals, middle_vals, lower_vals


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
