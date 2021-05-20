import pandas as pd
from tqdm import tqdm
import numpy as np

# from Geometric import speedy_grid_trading
from Arithmetic import speedy_grid_trading

# from Arithmetic_RSV import grid_trading
# from Arithmetic_RSV_GridNumber import grid_trading
# from RSV_GridNumber_ATRP_Arithmetic import grid_trading
# from Geometric_ATRP import speedy_grid_trading
# from Arithmetic_RSV_GridNumber_MultiBuy_MultiSell import grid_trading


FILENAME = "Decreasing_Data.csv"
# FILENAME = "Increasing_Data.csv"
# FILENAME = "Mild_Fluctuate_Data.csv"
# FILENAME = "Binance_BTC_1m.csv"
data = pd.read_excel(FILENAME)
# records_df, final_profit = grid_trading(
#     data,
#     INTERVALS_FOR_RSV=30,
#     INTERVAL_FOR_BOUNDS=15 * 24 * 60,
#     SD_PARAMETER=2,
#     GRID_NUMBER=6,
# )
print("\n", FILENAME, "\n")
# records_df, final_profit = grid_trading(
#     data, INTERVALS_FOR_RSV=40, INTERVAL_FOR_BOUNDS=15 * 24 * 60, SD_PARAMETER=3,
# )
records_df, final_profit = speedy_grid_trading(
    data, INTERVAL_FOR_BOUNDS=15 * 24 * 60, SD_PARAMETER=2,
)
records_df["Hour"] = pd.to_datetime(records_df["Hour"])
print(records_df)

# FILENAMES = [
#     "Binance_BTC_1m.csv",
#     "Mild_Fluctuate_Data.csv",
#     "Increasing_Data.csv",
#     "Decreasing_Data.csv",
# ]
# for FILENAME in FILENAMES:
#     data = pd.read_excel(FILENAME)
#     print(f"Number of data: {len(data)}")
#     # records_df, final_profit = grid_trading(
#     #     data,
#     #     INTERVALS_FOR_RSV=30,
#     #     INTERVAL_FOR_BOUNDS=15 * 24 * 60,
#     #     SD_PARAMETER=2,
#     #     GRID_NUMBER=6,
#     # )
#     print(FILENAME, "\n")
#     # records_df, final_profit = grid_trading(
#     #     data,
#     #     INTERVALS_FOR_RSV=30,
#     #     INTERVAL_FOR_BOUNDS=15 * 24 * 60,
#     #     SD_PARAMETER=2,
#     #     GRID_NUMBER=6,
#     # )
#     records_df, final_profit = speedy_grid_trading(
#         data, INTERVAL_FOR_BOUNDS=15 * 24 * 60, SD_PARAMETER=2,
#     )
#     records_df["Hour"] = pd.to_datetime(records_df["Hour"])
#     print(records_df)
#     print(f"Final Profit: {final_profit}")
