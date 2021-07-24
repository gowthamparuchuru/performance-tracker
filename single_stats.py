from PIL.Image import alpha_composite
import streamlit as st
from datetime import datetime

# Extrenal packages
import pandas as pd
import matplotlib.pyplot as plt
import calplot
import plotly.graph_objects as go
import numpy as np


def single_stats(selected_strat, df):
    original = df.copy()
    # cumulative pnl
    df['CumPNL'] = df['PNL'].cumsum()
    # drawdown
    df['HighValue'] = df['CumPNL'].cummax()
    df['Drawdown'] = df['CumPNL'] - df['HighValue']
    # roi
    df['ROI'] = round((df['PNL']/df['Capital'])*100, 2)
    # cumulative roi
    df['CumROI'] = df['ROI'].cumsum()

    # monthly pnl
    df['tmp'] = df.index
    df['Month'] = df['tmp'].apply(lambda x: x.strftime("%b, %Y"))
    month_groups = pd.DataFrame()
    month_groups["PNL"] = df.groupby('Month', sort=False)['PNL'].sum()
    month_groups["ROI"] = df.groupby('Month', sort=False)['ROI'].sum()

    # yearly pnl
    df['Year'] = df['tmp'].apply(lambda x: x.strftime('%Y'))
    year_groups = pd.DataFrame()
    year_groups["PNL"] = df.groupby('Year', sort=False)['PNL'].sum()
    year_groups["ROI"] = df.groupby('Year', sort=False)['ROI'].sum()

    # calculate all statistics of model.
    stats = {}
    stats["Start Date"] = datetime.strftime(df.index[0], "%d-%b-%Y")
    stats["Total Days"] = len(df)
    stats["Winning Day"] = df[df['PNL'] >= 0]['PNL'].count()
    stats["Losing Day"] = df[df['PNL'] < 0]['PNL'].count()
    stats["Winning Accuracy %"] = f"{round((stats['Winning Day']/stats['Total Days'])*100, 2)} %"
    stats["Max Profit"] = df["PNL"].max()
    stats["Max Loss"] = df["PNL"].min()
    stats["Max Drawdown"] = df["Drawdown"].min()
    stats["Avg Profit on Win Days"] = round(
        df[df['PNL'] >= 0]['PNL'].mean(), 2)
    stats["Avg Loss on Loss Days"] = round(df[df['PNL'] < 0]['PNL'].mean(), 2)
    stats["Avg Profit Per day"] = round(df['PNL'].mean(), 2)
    stats["Net profit"] = df['PNL'].sum()
    stats["Net Returns %"] = f"{df['ROI'].sum()} %"

    stat_table = pd.DataFrame(stats.items(), columns=["Stat", "Value"])
    stat_table['Value'] = stat_table['Value'].astype(str)
    stat_table.set_index("Stat", inplace=True)

    st.header(f"{selected_strat} statistics")
    st.table(stat_table)

    # Day profit and losses
    st.header(f"Day wise profit and loss")
    colours = np.where(df["PNL"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["PNL"], marker_color=colours))
    fig.update_layout(
        title="Day wise Profit and Loss",
        xaxis_title="Date",
        yaxis_title="P&L(₹)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=500
    )
    st.plotly_chart(fig)

    # calendar heatmap
    st.header(f"Calendar Heatmap")
    max_point = max(abs(min(df['PNL'])), max(df['PNL']))
    calplot.calplot(df["PNL"], cmap='PRGn', colorbar=True, linewidth=3, figsize=(
        60, 6), edgecolor='grey', vmin=-max_point, vmax=max_point)
    st.pyplot()
    plt.clf()

    # plot percentage returns
    st.header(f"Percentage returns plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CumROI'],
                  mode='lines+markers',
                  marker_color='rgba(46, 139, 87, 1)', opacity=0.5,
                  fill='tozeroy', fillcolor='rgba(46, 139, 87, 0.2)'))
    fig.update_layout(
        title="Percentage returns plot",
        xaxis_title="Date",
        yaxis_title="ROI(%)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=400
    )
    st.plotly_chart(fig)

    # plot absolute returns
    st.header(f"Absolute returns plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CumPNL'],
                  mode='lines',
                  marker_color='rgba(0,129,167,1)', opacity=0.5,
                  fill='tozeroy', fillcolor='rgba(0,129,167,0.2)'))
    fig.update_layout(
        title="Absolute returns plot",
        xaxis_title="Date",
        yaxis_title="Return(₹)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=400
    )
    st.plotly_chart(fig)

    # plot Drawdown
    st.header(f"Draw down plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Drawdown'],
                  mode='lines+markers',
                  marker_color='rgba(229,107,111,1)', opacity=0.5,
                  fill='tozeroy', fillcolor='rgba(229,107,111,0.2)'))
    fig.update_layout(
        title="Draw down plot",
        xaxis_title="Date",
        yaxis_title="Drawdown(₹)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=400,
        margin=dict(
            pad=10
        ),
    )
    st.plotly_chart(fig)

    st.header(f"Monthly PNL")
    st.table(month_groups)

    st.header(f"Yearly PNL")
    st.table(year_groups)

    st.header(f"Date-wise PNL (Last 30 Days)")
    original["Date"] = original.index
    original["Date"] = original['Date'].apply(lambda x: x.strftime("%d-%b-%Y"))
    original.set_index("Date", inplace=True)
    original.drop(["Brokerage"], axis=1, inplace=True)
    st.table(original.tail(30))
