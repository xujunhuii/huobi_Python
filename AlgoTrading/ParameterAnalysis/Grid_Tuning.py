import pandas as pd

BOLL_UPPER = "boll_upper"
BOLL_LOWER = "boll_lower"
CLOSE = "Close"
TIMESTAMP = "TimeStamp"


# N = 24 * 60
# M = 2
# R_DECREASING = 0.005
# R_INCREASING = 0.005
# last_price = 0
BEGINNING_CASH = 100000
FEE = 0.005
records = []
profit = 0
start_index = 0


def calc_RSV(prices, INTERVALS_FOR_RSV):
    C = prices
    H = prices.rolling(INTERVALS_FOR_RSV).max()
    L = prices.rolling(INTERVALS_FOR_RSV).min()
    RSV = (C - L) / (H - L)
    return RSV


def calc_bbands(prices, INTERVAL_FOR_BOUNDS, SD_PARAMETER):
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
            "Hour",
        ],
    )
    records_df = check_last_row(records_df)
    return records_df


def transact(
    data, R_DECREASING, R_INCREASING, n=0, cash=BEGINNING_CASH, last_price=0,
):
    for index, row in data.iterrows():
        time = row[TIMESTAMP]
        price = row[CLOSE]
        upper_bound = row[BOLL_UPPER]
        lower_bound = row[BOLL_LOWER]
        trading_buying_price = price * (1 + FEE)
        trading_selling_price = price * (1 - FEE)

        if n == 0 and (
            trading_buying_price < upper_bound
            or trading_buying_price < last_price * (1 - R_DECREASING)
        ):
            if trading_buying_price > lower_bound:
                last_price = trading_buying_price
                n = cash // trading_buying_price
                if n > 0:
                    cash -= n * trading_buying_price
                    profit = cash - BEGINNING_CASH
                    records.append(
                        [
                            "Buying",
                            round(trading_buying_price),
                            n,
                            round(cash),
                            round(profit),
                            lower_bound,
                            upper_bound,
                            time,
                        ]
                    )

        elif n > 0 and (
            trading_selling_price > lower_bound
            or trading_selling_price > last_price * (1 + R_INCREASING)
        ):
            if (
                trading_selling_price < upper_bound
                and trading_selling_price > last_price
            ):
                last_price = trading_selling_price
                cash += n * trading_selling_price
                profit = cash - BEGINNING_CASH
                n = 0
                records.append(
                    [
                        "Selling",
                        round(trading_selling_price),
                        n,
                        round(cash),
                        round(profit),
                        lower_bound,
                        upper_bound,
                        time,
                    ]
                )
    return records


def get_final_profit(df):
    temp = df.tail(1)
    final_profit = temp.iloc[0]["Profit"]
    return final_profit


def grid_trading(
    data,
    INTERVALS_FOR_RSV,
    INTERVAL_FOR_BOUNDS,
    SD_PARAMETER,
    R_INCREASING,
    R_DECREASING,
):
    RSV = calc_RSV(data["Close"], INTERVALS_FOR_RSV)
    data["RSV"] = RSV
    upper, _, lower = calc_bbands(data["Close"], INTERVAL_FOR_BOUNDS, SD_PARAMETER)
    data["boll_upper"] = upper
    data["boll_lower"] = lower
    data = data.dropna()
    data.reset_index(drop=True, inplace=True)
    records = transact(data, R_INCREASING=R_INCREASING, R_DECREASING=R_DECREASING)
    records_df = generate_records_df(records)
    final_profit = get_final_profit(records_df)
    return final_profit


FILENAME = "Binance_BTC_1m.csv"
data = pd.read_csv(FILENAME)
final_profit = grid_trading(
    data,
    INTERVALS_FOR_RSV=9,
    INTERVAL_FOR_BOUNDS=24 * 60,
    SD_PARAMETER=3,
    R_INCREASING=0.005,
    R_DECREASING=0.006,
)

print(final_profit)
