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

    start_date = st.sidebar.date_input(
        "select start date", value=min_date, min_value=min_date, max_value=max_date)

    to_date = st.sidebar.date_input(
        "select end date", value=max_date, min_value=start_date, max_value=max_date)

    dates_arr = np.arange(start_date, to_date + timedelta(days=1),
                          timedelta(days=1)).astype(datetime)
    dates_arr = pd.Series(dates_arr)

    df = pd.DataFrame(data=dates_arr, columns=["Date"])

    df.set_index("Date", inplace=True)

    corr_df = df.copy()

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

        corr_df[s_name] = val_df["PNL"]

    corr_df.fillna(0, inplace=True)
    corr_df = corr_df.loc[~(corr_df == 0).all(axis=1)]

    for datee in df.index:
        if df.loc[datee]["Capital"] == 0:
            df.drop(datee, inplace=True)

    single_stats("Portfolio", df)

    # plotting correlation heatmap
    st.header(f"Correlation Heatmap")
    sb.heatmap(corr_df.corr(), cmap="YlGnBu", annot=True)
    st.pyplot()

    # fig = px.imshow(corr_df.corr(), zmin=-1, zmax=1)
    # st.plotly_chart(fig)
