import pandas as pd
from utils import calc_bbands, calc_RSV, get_final_profit, dealing_results

BOLL_UPPER = "boll_upper"
BOLL_LOWER = "boll_lower"
CLOSE = "Close"
TIMESTAMP = "TimeStamp"

BEGINNING_CASH = 300000
CASH_MARGIN = 50000
FEE = 0.005
records = []
profit = 0
start_index = 0
N_GRID = 20


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
    is_it_first_buying = 0
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
        first_buying_price = (upper_bound + lower_bound) / 2
        if (
            is_it_first_buying == 0
            and first_buying_price - 10
            <= trading_buying_price
            <= first_buying_price + 10
        ):
            is_it_first_buying += 1
            last_price = trading_buying_price
            n = cash / trading_buying_price
            if n > 0:
                # print(
                #     f"First Buying: trading_buying_price, {trading_buying_price}, trading_selling_price, {trading_selling_price}, upper_bound, {upper_bound}, lower_bound, {lower_bound}, last_price, {last_price}\n"
                # )
                cash -= n * trading_buying_price
                profit = n * trading_buying_price - BEGINNING_CASH
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
        elif (
            is_it_first_buying > 0
            and cash >= CASH_MARGIN
            and (
                trading_buying_price < upper_bound
                or trading_buying_price < last_price - lower_grid
            )
        ):
            if trading_buying_price > lower_bound:
                last_price = trading_buying_price
                n_buying = CASH_MARGIN / trading_buying_price
                if n_buying > 0:
                    cash -= n_buying * trading_buying_price
                    n += n_buying
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
                n_selling = CASH_MARGIN / trading_selling_price
                cash += n_selling * trading_selling_price
                profit = cash - BEGINNING_CASH
                n -= n_selling
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
        final_profit = get_final_profit(records_df, data=data)
        return records_df, final_profit
    else:
        return "No records", 0


SD_PARAMETER_VALUE = 2
INTERVAL_FOR_BOUNDS_VALUE = 15
INTERVAL_FOR_RSV_VALUE = 30
GRID_NUMBER_VALUE = 6
FILES = [
    "./RESULT_EXCELS/Decreasing_Data.csv",
    "./RESULT_EXCELS/Increasing_Data.csv",
    "./RESULT_EXCELS/Mild_Fluctuate_Data.csv",
    "./RESULT_EXCELS/All_Data.csv",
]
for FILENAME in FILES:
    data = pd.read_csv(FILENAME)
    print(f"\nData: {FILENAME}")
    records_df, final_profit = grid_trading(
        data,
        INTERVALS_FOR_RSV=INTERVAL_FOR_RSV_VALUE,
        INTERVAL_FOR_BOUNDS=INTERVAL_FOR_BOUNDS_VALUE * 24 * 60,
        SD_PARAMETER=SD_PARAMETER_VALUE,
        GRID_NUMBER=GRID_NUMBER_VALUE,
    )
    dumb_profit, difference = dealing_results(
        records_df=records_df,
        FILENAME=FILENAME,
        BEGINNING_CASH=BEGINNING_CASH,
        final_profit=final_profit,
        data=data,
        METHOD_TAG="Arithmetic_RSV_GridNumber_MultiBuy_MultiSell",
    )
