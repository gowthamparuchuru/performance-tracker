import numpy as np
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import timedelta, date, datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')

# Extrenal packages


def today_stats(json_obj):

    # Date selector
    now = datetime.now(IST)
    today330pm = now.replace(hour=15, minute=30, second=0, microsecond=0)

    min_date = datetime(2021, 6, 7)
    max_date = date.today()

    if now.weekday() == 5:  # saturday
        value_date = date.today() - timedelta(days=1)
    elif now.weekday() == 6:  # sunday
        value_date = date.today() - timedelta(days=2)
    elif now < today330pm:
        value_date = date.today() - timedelta(days=1)
    else:
        value_date = date.today()

    select_date = st.sidebar.date_input(
        "select a date", value=value_date, min_value=min_date, max_value=max_date)

    # process the json_obj and combine curr day stats.
    stats = {}
    for strat in json_obj.keys():
        try:
            row = json_obj[strat].loc[datetime.strftime(
                select_date, "%d-%b-%Y")]
            stats[strat] = row
        except Exception:
            pass

    if len(stats) == 0:
        st.header(
            f"No Data for {datetime.strftime(select_date, '%d-%b-%Y (%a)')}")
        return

    # combine all rows.
    df = pd.concat(stats, axis=1)
    # st.table(df)
    df = df.T

    # caluclate net and roi.
    df.loc["Net"] = df.sum()
    df["ROI"] = round(100 * df["PNL"]/df["Capital"], 2)

    # print the dataframe.
    st.header(f"Date: {datetime.strftime(select_date, '%d-%b-%Y (%a)')}")
    st.table(df.style.format({'Capital': '₹ {:20,.0f}',
                              'Lot': '{:.0f}',
                              'Brokerage': '₹ {:20,.0f}',
                              'ROI': '{:.2f} %',
                              'PNL': '₹ {:20,.2f}'}))

    # plot PnL chart.
    st.header(f"PNL plots")

    colours = np.where(df["PNL"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["PNL"], marker_color=colours))
    fig.update_layout(
        title="Profit and Loss plot",
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
    fig.add_trace(go.Bar(x=df.index, y=df["ROI"], marker_color=colours))
    fig.update_layout(
        title="ROI plot",
        xaxis_title="Strategy",
        yaxis_title="ROI(%)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        )
    )
    st.plotly_chart(fig)
