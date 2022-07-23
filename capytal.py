from csv import writer
from datetime import datetime, timedelta
from functools import partial
from typing import List

import numpy as np
import pandas as pd
from dateutil.relativedelta import *


def savings_bot(df: pd.DataFrame, threshold: int = 400, initial_savings: int = 0):
    """
    > For each time stamp, if the minimum bank account balance is greater than the threshold, then the
    difference between the minimum bank account balance and the threshold is added to the savings
    account

    :param df: pd.DataFrame
    :type df: pd.DataFrame
    :param threshold: the minimum amount of money you want to keep in your bank account, defaults to 400
    :type threshold: int (optional)
    :param initial_savings: The amount of money you have in savings before the bot starts running,
    defaults to 0
    :type initial_savings: int (optional)
    :return: A dataframe with a new column called "savings"
    """
    df["savings"] = initial_savings
    for time_stamp in df.index.unique():
        delta_save = df.loc[time_stamp:, "bank_account"].min() - threshold
        if delta_save > 0:
            df.loc[time_stamp:, "bank_account"] -= delta_save
            df.loc[time_stamp:, "savings"] += delta_save

    return df


def label_cleaner(new_col_name, row):
    """
    If the new column is null, then the label is "No movement". Otherwise, the label is whatever it was
    before

    :param new_col_name: the name of the column that will be created
    :param row: the row of the dataframe that we're currently iterating over
    :return: A dataframe with the new column added.
    """
    row["label"] = "No movement" if pd.isna(row[new_col_name]) else row["label"]
    return row


class MoneyFlow:
    def __init__(
        self,
        amount: int | float,
        start: str | datetime,
        end: str | datetime | None = None,
        label: str = "unlabeled",
        conditionnal: str = "base",
        frequency: str = "p",
    ) -> None:
        self.amount = amount
        self.frequency = frequency
        print(type(start))
        self.start = (
            datetime.strptime(start, "%Y-%m-%d") if type(start) is str else start
        )
        if end is not None:
            self.end = datetime.strptime(end, "%Y-%m-%d") if type(end) is str else end
        self.label = label
        self.conditionnal = conditionnal

    def write(self):
        """
        It writes a log in a csv file
        """
        logs = []
        if self.frequency == "p":
            logs.append([self.start, self.amount, self.label, self.conditionnal])
        elif self.end is not None:
            if self.frequency == "w":
                recurrent_step = timedelta(weeks=1)
            elif self.frequency == "m":
                recurrent_step = relativedelta(months=1)
            while self.start <= self.end:
                logs.append([self.start, self.amount, self.label, self.conditionnal])
                self.start += recurrent_step

        with open("logs/logs.csv", "a+", newline="") as f:
            csv_writer = writer(f)
            csv_writer.writerows(logs)


def Accountant(
    end: str | datetime,
    start: str | None = None,
    hypothesises: List[str] | None = None,
    threshold: int = 400,
    initial_savings=232,
):

    if hypothesises is None:
        hypothesises = []

    if start is None:
        start = datetime.now()
    elif start is str:
        start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d") if end is str else end

    df = pd.read_csv("logs/logs.csv", header=None)
    df.columns = ["timestamp", "movement", "label", "conditionnal"]
    df.timestamp = pd.to_datetime(df.timestamp)
    df.loc[:, "movement"] = df.loc[:, "movement"].astype(int)
    df.sort_values(by="timestamp", inplace=True)
    df.drop_duplicates(inplace=True)

    df["cumsum"] = df.movement.cumsum()

    cond = df.conditionnal == "base"
    cond_name = ["base"]
    for conditionnal in hypothesises:
        cond = cond | (df.conditionnal == conditionnal)
        cond_name.append(conditionnal)
    new_col_name = "bank_account"
    df[new_col_name] = np.NaN
    new_col = df[cond].movement.cumsum()
    df.loc[new_col.index, new_col_name] = new_col
    df.loc[:, "label"] = df.apply(partial(label_cleaner, new_col_name), axis=1)
    df[new_col_name].fillna(method="ffill", inplace=True)
    df[new_col_name] = df[new_col_name].astype(int)

    df.set_index("timestamp", inplace=True)
    df = df.loc[:end, :]
    df.dropna(inplace=True)
    df = savings_bot(df=df, threshold=threshold, initial_savings=initial_savings)
    return df


if __name__ == "__main__":
    MoneyFlow(
        500,
        start="2022-08-10",
        end="2022-09-20",
        frequency="m",
        label="internship wage",
    ).write()
    MoneyFlow(
        -250, start="2022-08-02", end="2023-05-20", frequency="m", label="rent"
    ).write()
    MoneyFlow(
        350, start="2022-07-26", end="2023-09-20", frequency="m", label="allowance"
    ).write()
    MoneyFlow(
        170, start="2022-10-02", end="2023-05-20", frequency="m", label="scholarship"
    ).write()
    MoneyFlow(500, start="2022-07-23", frequency="p", label="base money").write()
    MoneyFlow(
        1400, start="2022-08-23", frequency="p", label="FFHCM", conditionnal="FFHCM"
    ).write()
    MoneyFlow(
        2000,
        start="2022-09-30",
        frequency="p",
        label="CuttinEdge",
        conditionnal="CuttinEdge",
    ).write()
    MoneyFlow(
        400,
        start="2022-10-02",
        end="2023-05-20",
        frequency="m",
        label="Research Assistant",
        conditionnal="RA",
    ).write()
    MoneyFlow(
        -60, start="2022-07-24", end="2023-05-20", frequency="w", label="food"
    ).write()

    Accountant(end="2022-09-20", hypothesises=["FFHCM", "CuttinEdge", "RA"])
