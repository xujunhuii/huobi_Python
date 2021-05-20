import pandas as pd
from utils import calc_bbands, get_final_profit, dealing_results, ALL_FILES

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
            "Grid",
            "Hour",
        ],
    )
    return records_df


def get_grid_arithmetic(lower_bound, upper_bound):
    grid = (upper_bound - lower_bound) / 10
    return grid


def transact(
    data, n=0, cash=BEGINNING_CASH, last_price=0,
):
    is_it_first_buying = 0
    for index, row in data.iterrows():
        time = row[TIMESTAMP]
        price = row[CLOSE]
        upper_bound = row[BOLL_UPPER]
        lower_bound = row[BOLL_LOWER]
        grid = get_grid_arithmetic(lower_bound, upper_bound)
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
                        grid,
                        time,
                    ]
                )
        elif (
            is_it_first_buying > 0
            and n == 0
            and (
                trading_buying_price < upper_bound
                or trading_buying_price < last_price - grid
            )
        ):

            if trading_buying_price > lower_bound:
                last_price = trading_buying_price
                new_buying_n = cash / trading_buying_price
                if new_buying_n > 0:
                    # print(
                    #     f"Buying: trading_buying_price, {trading_buying_price}, trading_selling_price, {trading_selling_price}, upper_bound, {upper_bound}, lower_bound, {lower_bound}, last_price, {last_price}\n"
                    # )
                    cash -= new_buying_n * trading_buying_price
                    profit = new_buying_n * trading_buying_price - BEGINNING_CASH
                    n += new_buying_n
                    records.append(
                        [
                            "Buying",
                            round(trading_buying_price),
                            n,
                            round(cash),
                            round(profit),
                            lower_bound,
                            upper_bound,
                            grid,
                            time,
                        ]
                    )

        elif n > 0 and (
            trading_selling_price > lower_bound
            or trading_selling_price > last_price + grid
        ):
            if (
                trading_selling_price < upper_bound
                and trading_selling_price > last_price + grid
            ):
                # print(
                #     f"Selling: trading_buying_price, {trading_buying_price}, trading_selling_price, {trading_selling_price}, upper_bound, {upper_bound}, lower_bound, {lower_bound}, last_price, {last_price}\n"
                # )
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
                        grid,
                        time,
                    ]
                )
    return records


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
        if len(records_df) > 0:
            final_profit = get_final_profit(records_df, data=data)
            return records_df, final_profit
        else:
            return "No records", 0
    else:
        return "No records", 0


SD_PARAMETER_VALUE = 3
INTERVAL_FOR_BOUNDS_VALUE = 5
for FILENAME in ALL_FILES:
    data = pd.read_excel(FILENAME)
    print(f"\nData: {FILENAME}")
    records_df, final_profit = speedy_grid_trading(
        data,
        INTERVAL_FOR_BOUNDS=INTERVAL_FOR_BOUNDS_VALUE * 24 * 60,
        SD_PARAMETER=SD_PARAMETER_VALUE,
    )
    records_df["Hour"] = pd.to_datetime(records_df["Hour"])
    dumb_profit, difference = dealing_results(
        records_df=records_df,
        FILENAME=FILENAME,
        BEGINNING_CASH=BEGINNING_CASH,
        final_profit=final_profit,
        data=data,
        METHOD_TAG="Arithmetic",
    )
