import streamlit as st
import pandas as pd

import numpy as np
from datetime import timedelta, datetime, date
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import seaborn as sb

import plotly.express as px
import plotly.figure_factory as ff


from single_stats import single_stats


def all_stats(json_obj):
    min_date = datetime(2021, 6, 7)
    max_date = date.today()
    month_start = datetime.now().replace(day=1)

    start_date = st.sidebar.date_input(
        "select start date", value=month_start, min_value=min_date, max_value=max_date)

    to_date = st.sidebar.date_input(
        "select end date", value=max_date, min_value=start_date, max_value=max_date)

    dates_arr = np.arange(start_date, to_date + timedelta(days=1),
                          timedelta(days=1)).astype(datetime)
    dates_arr = pd.Series(dates_arr)

    df = pd.DataFrame(data=dates_arr, columns=["Date"])

    df.set_index("Date", inplace=True)

    corr_df = df.copy()

    df["capital"] = 0
    df["lot"] = 0
    df["brokerage"] = 0
    df["pnl"] = 0

    for s_name, val_df in json_obj.items():
        df["capital"] = df["capital"].add(val_df["capital"], fill_value=0)
        df["lot"] = df["lot"].add(val_df["lot"], fill_value=0)
        df["pnl"] = df["pnl"].add(val_df["pnl"], fill_value=0)
        df["brokerage"] = df["brokerage"].add(
            val_df["brokerage"], fill_value=0)

        corr_df[s_name] = val_df["pnl"]

    corr_df.fillna(0, inplace=True)
    corr_df = corr_df.loc[~(corr_df == 0).all(axis=1)]

    for datee in df.index:
        if df.loc[datee]["capital"] == 0:
            df.drop(datee, inplace=True)

    single_stats("Portfolio", df)

    # plotting correlation heatmap
    st.header(f"Correlation Heatmap")
    sb.heatmap(corr_df.corr(), cmap="YlGnBu", annot=True)
    st.pyplot()

    # fig = px.imshow(corr_df.corr(), zmin=-1, zmax=1)
    # st.plotly_chart(fig)
