from PIL.Image import alpha_composite
import streamlit as st
from datetime import datetime

# Extrenal packages
import pandas as pd
import calplot
import plotly.graph_objects as go
import numpy as np


def single_stats(selected_strat, df):
    # save a copy of dataframe.
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

    # weekday wise pnl
    df['tmp'] = df.index
    weekDays = ("Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday")
    df['Week'] = df['tmp'].apply(
        lambda x: weekDays[x.to_pydatetime().weekday()])
    week_groups = pd.DataFrame()
    week_groups["PNL"] = df.groupby('Week', sort=True)['PNL'].sum()
    week_groups["ROI"] = df.groupby('Week', sort=True)['ROI'].sum()

    # monthly pnl
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
    stats["Net Returns %"] = f"{round(df['ROI'].sum(), 2)} %"

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
    # st.header(f"Calendar Heatmap")
    # max_point = max(abs(min(df['PNL'])), max(df['PNL']))
    # calplot.calplot(df["PNL"], cmap='PRGn', colorbar=True, linewidth=3, figsize=(
    #     60, 6), edgecolor='grey', vmin=-max_point, vmax=max_point)
    # st.pyplot()
    # plt.clf()

    # plot percentage returns
    st.header(f"Returns plots")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CumROI'],
                  mode='lines+markers',
                  marker=dict(size=4),
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
        height=600
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    st.plotly_chart(fig)

    # plot absolute returns
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['CumPNL'],
                  mode='lines+markers',
                  marker=dict(size=4),
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
        height=600
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    st.plotly_chart(fig)

    # plot Drawdown
    st.header(f"Drawdown plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Drawdown'],
                  mode='lines+markers',
                  marker=dict(size=4),
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
        height=600,
        margin=dict(
            pad=3
        ),
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    st.plotly_chart(fig)

    st.header(f"Weekday wise PNL")
    cats = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday']
    week_groups = week_groups.loc[cats]

    colours = np.where(week_groups["PNL"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=week_groups.index,
                  y=week_groups["PNL"], marker_color=colours))
    fig.update_layout(
        title="Week Day wise Profit and Loss",
        xaxis_title="Day",
        yaxis_title="P&L(₹)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=500
    )
    st.plotly_chart(fig)

    colours = np.where(week_groups["ROI"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=week_groups.index,
                  y=week_groups["ROI"], marker_color=colours))
    fig.update_layout(
        title="Week Day wise ROI",
        xaxis_title="Day",
        yaxis_title="ROI(%)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=500
    )
    st.plotly_chart(fig)

    st.header(f"Monthly PNL")
    st.table(month_groups.style.format({
        "PNL": '₹ {:20,.0f}',
        "ROI": '{:.2f}%'
    }))

    st.header(f"Yearly PNL")
    st.table(year_groups.style.format({
        "PNL": '₹ {:20,.0f}',
        "ROI": '{:.2f}%'
    }))

    st.header(f"Date-wise PNL (Last 30 Days)")
    original["Date"] = original.index
    original["Date"] = original['Date'].apply(lambda x: x.strftime("%d-%b-%Y"))
    original.set_index("Date", inplace=True)
    original.drop(["Brokerage"], axis=1, inplace=True)
    original['ROI'] = (original['PNL']/original['Capital']) * 100
    st.table(original.iloc[::-1].head(30).style.format({
        "Capital": '₹ {:20,.0f}',
        "PNL": '₹ {:.2f}',
        "ROI": '{:.2f}%',
    }))
