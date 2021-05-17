import pandas as pd
from utils import calc_bbands

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


def check_last_row(records_df):
    print(records_df)
    print(len(records_df))
    if len(records_df) > 0:
        print(records_df)
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
            "LowerGrid",
            "UpperGrid",
            "Hour",
        ],
    )
    records_df = check_last_row(records_df)
    return records_df


def get_grid_arithmetic(lower_bound, upper_bound, rsv, grid_number):
    if rsv != 1:
        lower_grid = (upper_bound - lower_bound) * (1 - rsv) / (grid_number // 2)
        upper_grid = rsv / (1 - rsv) * lower_grid
    else:
        lower_grid = upper_grid = (upper_bound - lower_bound) / grid_number
    return lower_grid, upper_grid


def transact(
    data, n=0, cash=BEGINNING_CASH, last_price=0, grid_number=10,
):
    for index, row in data.iterrows():
        time = row[TIMESTAMP]
        price = row[CLOSE]
        rsv = row["RSV"]
        upper_bound = row[BOLL_UPPER]
        lower_bound = row[BOLL_LOWER]
        lower_grid, upper_grid = get_grid_arithmetic(
            lower_bound, upper_bound, rsv, grid_number
        )
        trading_buying_price = price * (1 + FEE)
        trading_selling_price = price * (1 - FEE)

        if n == 0 and (
            trading_buying_price < upper_bound
            or trading_buying_price < last_price - lower_grid
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
                            lower_grid,
                            upper_grid,
                            time,
                        ]
                    )

        elif n > 0 and (
            trading_selling_price > lower_bound
            or trading_selling_price > last_price + upper_grid
        ):
            if (
                trading_selling_price < upper_bound
                and trading_selling_price > last_price + upper_grid
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
                        lower_grid,
                        upper_grid,
                        time,
                    ]
                )
    return records


def get_final_profit(df):
    temp = df.tail(1)
    final_profit = temp.iloc[0]["Profit"]
    return final_profit


def grid_trading(
    data, INTERVALS_FOR_RSV, INTERVAL_FOR_BOUNDS, SD_PARAMETER, GRID_NUMBER,
):
    RSV = calc_RSV(data["Close"], INTERVALS_FOR_RSV)
    data["RSV"] = RSV
    upper, _, lower = calc_bbands(data["Close"], INTERVAL_FOR_BOUNDS, SD_PARAMETER)
    data["boll_upper"] = upper
    data["boll_lower"] = lower
    data = data.dropna()
    data.reset_index(drop=True, inplace=True)
    records = transact(data, grid_number=GRID_NUMBER)
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
