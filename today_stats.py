import streamlit as st
from datetime import datetime

# Extrenal packages
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def today_stats(json_obj):

    # process the json_obj and combine curr day stats.
    stats = {}
    for strat in json_obj.keys():
        row = json_obj[strat].iloc[-1]
        date = json_obj[strat].index[-1]
        stats[strat] = row

    # create date to print
    date = datetime.strftime(date, "%d-%b-%Y")

    # combine all rows.
    df = pd.concat(stats, axis=1)
    df = df.T

    df.loc["Net"] = df.sum()
    df["ROI"] = df["PNL"]/df["Capital"]

    # print the dataframe.
    st.header(f"Date: {date}")
    st.table(df.style.format({'Capital': '{:.0f}', 'Lot': '{:.0f}',
             'Brokerage': '{:.0f}', 'ROI': '{:.2%}', 'PNL': '{:.2f}'}))

    # plot PnL chart.
    st.header(f"Today stats")
    colours = np.where(df["PNL"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["PNL"], marker_color=colours))
    fig.update_layout(
        title="Today profit and loss",
        xaxis_title="Strategy",
        yaxis_title="P&L(₹)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        )
    )
    st.plotly_chart(fig)

    # plot ROI chart for the day.
    colours = np.where(df["ROI"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=round(
        df["ROI"]*100, 2), marker_color=colours))
    fig.update_layout(
        title="Today ROI",
        xaxis_title="Strategy",
        yaxis_title="ROI(%)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        )
    )
    st.plotly_chart(fig)
