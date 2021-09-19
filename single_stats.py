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
    df['cum_pnl'] = df['pnl'].cumsum()
    # drawdown
    df['high_value'] = df['cum_pnl'].cummax()
    df['drawdown'] = df['cum_pnl'] - df['high_value']
    # roi
    df['roi'] = round((df['pnl']/df['capital'])*100, 2)
    # cumulative roi
    df['cum_roi'] = df['roi'].cumsum()
    # drawdown roi
    df['roi_high_value'] = df['cum_roi'].cummax()
    df['roi_drawdown'] = df['cum_roi'] - df['roi_high_value']

    # weekday wise pnl
    df['tmp'] = df.index
    weekDays = ("Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday")
    df['week'] = df['tmp'].apply(
        lambda x: weekDays[x.to_pydatetime().weekday()])
    week_groups = pd.DataFrame()
    week_groups["pnl"] = df.groupby('week', sort=True)['pnl'].sum()
    week_groups["roi"] = df.groupby('week', sort=True)['roi'].sum()

    # monthly pnl
    df['month'] = df['tmp'].apply(lambda x: x.strftime("%b, %Y"))
    month_groups = pd.DataFrame()
    month_groups["pnl"] = df.groupby('month', sort=False)['pnl'].sum()
    month_groups["roi"] = df.groupby('month', sort=False)['roi'].sum()

    # yearly pnl
    df['year'] = df['tmp'].apply(lambda x: x.strftime('%Y'))
    year_groups = pd.DataFrame()
    year_groups["pnl"] = df.groupby('year', sort=False)['pnl'].sum()
    year_groups["roi"] = df.groupby('year', sort=False)['roi'].sum()

    # calculate all statistics of model.
    stats = {}
    stats["Start Date"] = datetime.strftime(df.index[0], "%d-%b-%Y")
    stats["Total Days"] = len(df)
    stats["Winning Day"] = df[df['pnl'] >= 0]['pnl'].count()
    stats["Losing Day"] = df[df['pnl'] < 0]['pnl'].count()
    stats["Winning Accuracy %"] = f"{round((stats['Winning Day']/stats['Total Days'])*100, 2)} %"
    stats["Max Profit"] = "{:.2f}".format(df["pnl"].max())
    stats["Max Loss"] = "{:.2f}".format(df["pnl"].min())
    stats["Max Drawdown"] = "{:.2f}".format(df["drawdown"].min())
    stats["Avg Profit on Win Days"] = round(
        df[df['pnl'] >= 0]['pnl'].mean(), 2)
    stats["Avg Loss on Loss Days"] = round(df[df['pnl'] < 0]['pnl'].mean(), 2)
    stats["Avg Profit Per day"] = round(df['pnl'].mean(), 2)
    stats["Net profit"] = "{:.2f}".format(df['pnl'].sum())
    stats["Net Returns %"] = f"{round(df['roi'].sum(), 2)} %"
    stats["Sharpe Ratio"] = "{:.2f}".format(
        (252 ** 0.5) * (df["pnl"].mean() / df["pnl"].std()))
    win_days_acc = (stats['Winning Day']/stats['Total Days'])*100
    loss_days_acc = 100 - win_days_acc
    risk_to_reward = stats["Avg Profit on Win Days"] / \
        (- stats["Avg Loss on Loss Days"])
    stats["Expectancy"] = "{:.2f}".format(
        ((risk_to_reward * win_days_acc) - loss_days_acc)/100)

    stat_table = pd.DataFrame(stats.items(), columns=["Stat", "Value"])
    stat_table['Value'] = stat_table['Value'].astype(str)
    stat_table.set_index("Stat", inplace=True)

    st.header(f"{selected_strat} statistics")
    st.table(stat_table)

    ####################
    ### Day wise PNL ###
    ####################
    st.header(f"Daily profit and loss")
    # ROI
    colours = np.where(df["roi"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["roi"], marker_color=colours))
    fig.update_layout(
        title="Day wise ROI",
        xaxis_title="Date",
        yaxis_title="ROI(%)",
        font=dict(
            family="Courier New, monospace",
            size=14,
        ),
        height=500
    )
    st.plotly_chart(fig)

    # Absolute

    colours = np.where(df["pnl"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["pnl"], marker_color=colours))
    fig.update_layout(
        title="Day wise PNL",
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
    # max_point = max(abs(min(df['pnl'])), max(df['pnl']))
    # calplot.calplot(df["pnl"], cmap='PRGn', colorbar=True, linewidth=3, figsize=(
    #     60, 6), edgecolor='grey', vmin=-max_point, vmax=max_point)
    # st.pyplot()
    # plt.clf()

    ###################
    ### Equity Plot ###
    ###################
    # Percentage
    st.header(f"Returns plots")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['cum_roi'],
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

    # Absolute
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['cum_pnl'],
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

    ###################
    ###  Draw Down  ###
    ###################
    # Percentage Drawdown
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['roi_drawdown'],
                  mode='lines+markers',
                  marker=dict(size=4),
                  marker_color='rgba(229,107,111,1)', opacity=0.5,
                  fill='tozeroy', fillcolor='rgba(229,107,111,0.2)'))
    fig.update_layout(
        title="Draw down plot in ROI",
        xaxis_title="Date",
        yaxis_title="Drawdown(%)",
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

    # Absolute Drawdown
    st.header(f"Drawdown plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['drawdown'],
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

    ###################
    ###   Returns   ###
    ###################

    st.header(f"Weekday wise PNL")
    cats = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday']
    week_groups = week_groups.loc[cats]

    colours = np.where(week_groups["pnl"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=week_groups.index,
                  y=week_groups["pnl"], marker_color=colours))
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

    colours = np.where(week_groups["roi"] < 0, 'crimson', 'SeaGreen')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=week_groups.index,
                  y=week_groups["roi"], marker_color=colours))
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
    st.table(month_groups.iloc[::-1].style.format({
        "pnl": '₹ {:20,.0f}',
        "roi": '{:.2f} %'
    }))

    st.header(f"Yearly PNL")
    st.table(year_groups.iloc[::-1].style.format({
        "pnl": '₹ {:20,.0f}',
        "roi": '{:.2f} %'
    }))

    st.header(f"Date-wise PNL (Last 30 Days)")
    original["date"] = original.index
    original["date"] = original['date'].apply(lambda x: x.strftime("%d-%b-%Y"))
    original.set_index("date", inplace=True)
    original.drop(["brokerage"], axis=1, inplace=True)
    original['roi'] = (original['pnl']/original['capital']) * 100
    st.table(original.iloc[::-1].head(10).style.format({
        "capital": '{:20,.0f}',
        "lot": '{:.0f}',
        "pnl": "{:.0f}",
        "roi": '{:.2f} %',
    }))
