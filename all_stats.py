import streamlit as st
import pandas as pd

import numpy as np
from datetime import timedelta, datetime, date
import plotly.graph_objects as go

from single_stats import single_stats


def all_stats(json_obj):

    start_date = datetime(2021, 6, 7)
    to_date = date.today()
    dates_arr = np.arange(start_date, to_date,
                          timedelta(days=1)).astype(datetime)
    dates_arr = pd.Series(dates_arr)

    df = pd.DataFrame(data=dates_arr, columns=["Date"])

    df.set_index("Date", inplace=True)

    df["Capital"] = 0
    df["Lot"] = 0
    df["Brokerage"] = 0
    df["PNL"] = 0

    for s_name, val_df in json_obj.items():
        df["Capital"] = df["Capital"].add(val_df["Capital"], fill_value=0)
        df["Lot"] = df["Lot"].add(val_df["Lot"], fill_value=0)
        df["PNL"] = df["PNL"].add(val_df["PNL"], fill_value=0)
        df["Brokerage"] = df["Brokerage"].add(
            val_df["Brokerage"], fill_value=0)

    for datee in df.index:
        if df.loc[datee]["Capital"] == 0:
            df.drop(datee, inplace=True)

    single_stats("Portfolio", df)
