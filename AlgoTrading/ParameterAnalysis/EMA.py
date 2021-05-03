#
# See how to use this script and what type of input to use at:
# https://steemit.com/trading/@jwyles/ema-ema-and-dema-how-to-calculate-using-python-and-spreadsheets
#
# This gist is an extension of this other gist:
# https://gist.github.com/jtwyles/517becb2deebf9e3b2874d8c26c4c99f
#

import csv
import re
from functools import reduce
from dateutil import parser

CSV_FILE = "input.csv"
EMA_LENGTH = 5
EMA_SOURCE = "close"

candles = []

# Reads the input file and saves to `candles` all the candles found. Each candle is
# a dict with the timestamp and the OHLC values.
def read_candles():
    with open(CSV_FILE, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            try:
                candles.append(
                    {
                        "ts": parser.parse(row[0]),
                        "low": float(re.sub(",", "", row[1])),
                        "high": float(re.sub(",", "", row[2])),
                        "open": float(re.sub(",", "", row[3])),
                        "close": float(re.sub(",", "", row[4])),
                    }
                )
            except:
                print("Error parsing {}".format(row))


# Calculates the SMA of an array of candles using the `source` price.
def calculate_sma(candles, source):
    length = len(candles)
    sum = reduce((lambda last, x: {source: last[source] + x[source]}), candles)
    sma = sum[source] / length
    return sma


# Calculates the EMA of an array of candles using the `source` price.
def calculate_ema(candles, source):
    length = len(candles)
    target = candles[0]
    previous = candles[1]

    # if there is no previous EMA calculated, then EMA=SMA
    if "ema" not in previous or previous["ema"] == None:
        return calculate_sma(candles, source)

    else:
        # multiplier: (2 / (length + 1))
        # EMA: (close * multiplier) + ((1 - multiplier) * EMA(previous))
        multiplier = 2 / (length + 1)
        ema = (target[source] * multiplier) + (previous["ema"] * (1 - multiplier))

        return ema


# Calculates the EMA(EMA) of an array of candles.
def calculate_ema_ema(candles):
    length = len(candles)
    target = candles[0]
    previous = candles[1]

    # all previous candles need to have an EMA already, otherwise we can't calculate EMA(EMA)
    have_ema = list(filter(lambda a: "ema" in a and a["ema"] != None, candles[1:]))
    if len(have_ema) >= length - 1:

        # if there is no previous EMA(EMA) calculated yet, then EMA(EMA)=SMA(EMA)
        if "ema_ema" not in previous or previous["ema_ema"] == None:
            return calculate_sma(candles, "ema")

        # if there is a previous EMA(EMA), it is used
        else:
            # multiplier: (2 / (length + 1))
            # EMA(EMA): (EMA * multiplier) + ((1 - multiplier) * EMA(EMA, previous))
            multiplier = 2 / (length + 1)
            ema_ema = (target["ema"] * multiplier) + (
                previous["ema_ema"] * (1 - multiplier)
            )

            return ema_ema

    else:
        return None


# Calculates the DEMA of an array of candles.
def calculate_dema(candles):
    target = candles[0]

    # can only calculate the DEMA if we have the EMA and the EMA(EMA) if the target candle
    if (
        "ema" not in target
        or "ema_ema" not in target
        or target["ema"] == None
        or target["ema_ema"] == None
    ):
        return None

    else:
        # DEMA = 2*EMA – EMA(EMA)
        dema = (2 * target["ema"]) - target["ema_ema"]
        return dema


def calculate(candles, source):
    candles[0]["sma"] = calculate_sma(candles, source)
    candles[0]["ema"] = calculate_ema(candles, source)
    candles[0]["ema_ema"] = calculate_ema_ema(candles)
    candles[0]["dema"] = calculate_dema(candles)


if __name__ == "__main__":
    read_candles()

    # progress through the array of candles to calculate the indicators for each
    # block of candles
    position = 0
    while position + EMA_LENGTH <= len(candles):
        current_candles = candles[position : (position + EMA_LENGTH)]
        current_candles = list(reversed(current_candles))
        calculate(current_candles, EMA_SOURCE)
        position += 1

    for candle in candles:
        if "sma" in candle:
            print(
                "{}: sma={} ema={} ema(ema)={} dema={}".format(
                    candle["ts"],
                    candle["sma"],
                    candle["ema"],
                    candle["ema_ema"],
                    candle["dema"],
                )
            )
