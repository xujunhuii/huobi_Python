import pandas as pd
from utils import calc_bbands, generate_records_df, calc_ATRP, get_final_profit

BOLL_UPPER = "boll_upper"
BOLL_LOWER = "boll_lower"
CLOSE = "Close"
TIMESTAMP = "TimeStamp"

BEGINNING_CASH = 100000
FEE = 0.005
records = []
profit = 0
start_index = 0
N_GRID = 20


def calc_RSV(prices, INTERVALS_FOR_RSV):
    C = prices
    H = prices.rolling(INTERVALS_FOR_RSV).max()
    L = prices.rolling(INTERVALS_FOR_RSV).min()
    RSV = (C - L) / (H - L)
    return RSV


def get_rate(lower_bound, upper_bound):
    for n in range(N_GRID, 5, -5):
        rate = pow(upper_bound / lower_bound, 1 / (n - 1)) - 1
        if not isinstance(1j, complex) and rate > FEE:
            return rate
    return FEE + 0.001


def transact(
    data, n=0, cash=BEGINNING_CASH, last_price=0,
):
    for index, row in data.iterrows():
        time = row[TIMESTAMP]
        price = row[CLOSE]
        upper_bound = row[BOLL_UPPER]
        lower_bound = row[BOLL_LOWER]
        rate = get_rate(lower_bound, upper_bound)
        fluctuate_rate = row["ATRP_Diff"]
        rate = rate * (1 + fluctuate_rate)

        trading_buying_price = price * (1 + FEE)
        trading_selling_price = price * (1 - FEE)

        if n == 0 and (
            trading_buying_price < upper_bound
            or trading_buying_price < last_price * (1 - rate)
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
                            rate,
                            time,
                        ]
                    )

        elif n > 0 and (
            trading_selling_price > lower_bound
            or trading_selling_price > last_price * (1 + rate)
        ):
            if (
                trading_selling_price < upper_bound
                and trading_selling_price > last_price * (1 + rate)
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
                        rate,
                        time,
                    ]
                )
    return records


def grid_trading(
    data, INTERVALS_FOR_RSV, INTERVAL_FOR_BOUNDS, SD_PARAMETER,
):
    RSV = calc_RSV(data["Close"], INTERVALS_FOR_RSV)
    data["RSV"] = RSV
    upper, _, lower = calc_bbands(data["Close"], INTERVAL_FOR_BOUNDS, SD_PARAMETER)
    data["boll_upper"] = upper
    data["boll_lower"] = lower
    ATRP = calc_ATRP(data["High"], data["Low"], data["Close"])
    data["ATRP"] = ATRP
    TOTAL_RANGE = data["ATRP"].max() - data["ATRP"].min()
    AVERAGE = (data["ATRP"].max() + data["ATRP"].min()) / 2
    data["ATRP_Diff"] = (data["ATRP"] - AVERAGE) / TOTAL_RANGE
    data = data.dropna()
    data.reset_index(drop=True, inplace=True)
    records = transact(data)
    if len(records) > 0:
        records_df = generate_records_df(records)
        final_profit = get_final_profit(records_df)
        return records_df, final_profit
    else:
        return "No records", 0


def speedy_grid_trading(
    data, INTERVAL_FOR_BOUNDS, SD_PARAMETER,
):
    upper, _, lower = calc_bbands(data["Close"], INTERVAL_FOR_BOUNDS, SD_PARAMETER)
    data["boll_upper"] = upper
    data["boll_lower"] = lower
    ATRP = calc_ATRP(data["High"], data["Low"], data["Close"])
    data["ATRP"] = ATRP
    TOTAL_RANGE = data["ATRP"].max() - data["ATRP"].min()
    AVERAGE = (data["ATRP"].max() + data["ATRP"].min()) / 2
    data["ATRP_Diff"] = (data["ATRP"] - AVERAGE) / TOTAL_RANGE
    data = data.dropna()
    data.reset_index(drop=True, inplace=True)
    records = transact(data)
    if len(records) > 0:
        records_df = generate_records_df(records)
        final_profit = get_final_profit(records_df)
        return records_df, final_profit
    else:
        return "No records", 0


# FILENAME = "Binance_BTC_1m.csv"
# data = pd.read_csv(FILENAME)
# records_df, final_profit = grid_trading(
#     data, INTERVALS_FOR_RSV=9, INTERVAL_FOR_BOUNDS=24 * 60, SD_PARAMETER=3,
# )
# records_df.to_excel("Transactions.xlsx")

# print(final_profit)
