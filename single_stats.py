import streamlit as st
from datetime import datetime

# Extrenal packages
import pandas as pd
import matplotlib.pyplot as plt
import calplot


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
    # stats["Start Date"] = datetime.strftime(df.index[0], "%d-%b-%Y")
    stats["Total Days"] = len(df)
    stats["Winning Day"] = df[df['PNL'] >= 0]['PNL'].count()
    stats["Losing Day"] = df[df['PNL'] < 0]['PNL'].count()
    stats["Winning Accuracy %"] = round(
        (stats["Winning Day"]/stats["Total Days"])*100, 2)
    stats["Max Profit"] = df["PNL"].max()
    stats["Max Loss"] = df["PNL"].min()
    stats["Max Drawdown"] = df["Drawdown"].min()
    stats["Avg Profit on Win Days"] = df[df['PNL'] >= 0]['PNL'].mean()
    stats["Avg Loss on Loss Days"] = df[df['PNL'] < 0]['PNL'].mean()
    stats["Avg Profit Per day"] = df['PNL'].mean()
    stats["Net profit"] = df['PNL'].sum()
    stats["Net Returns %"] = df['ROI'].sum()

    stat_table = pd.DataFrame(stats.items(), columns=["Stat", "Value"])
    stat_table['Value'] = round(stat_table['Value'], 2)
    stat_table.set_index("Stat", inplace=True)
    st.header(f"{selected_strat} statistics")
    st.table(stat_table)

    # Day profit and losses
    st.header(f"Day wise profit and loss")
    plt.figure(figsize=(15, 5))
    plt.bar(df.index, df["PNL"], color=(
        df["PNL"] > 0).map({True: 'g', False: 'r'}))
    plt.title("Day wise Profit and Loss")
    plt.xlabel("Date")
    plt.ylabel("Profit and Loss")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()

    st.header(f"Calendar Heatmap")
    max_point = max(abs(min(df['PNL'])), max(df['PNL']))
    calplot.calplot(df["PNL"], cmap='PRGn', colorbar=True, linewidth=3, figsize=(
        60, 6), edgecolor='grey', vmin=-max_point, vmax=max_point)
    st.pyplot()
    plt.clf()

    # plot percentage returns
    st.header(f"Percentage returns plot")
    plt.figure(figsize=(15, 5))
    plt.plot(df['CumROI'], '.', alpha=0.8)
    plt.fill_between(df.index, df['CumROI'], color='#0081a7', alpha=0.20)
    plt.title("Percentage Returns")
    plt.xlabel("Date")
    plt.ylabel("ROI")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()

    # plot absolute returns
    st.header(f"Absolute returns plot")
    plt.figure(figsize=(15, 5))
    plt.plot(df['CumPNL'], alpha=0.8)
    plt.fill_between(df.index, df['CumPNL'], color='#0081a7', alpha=0.20)
    plt.title("Absolute Returns")
    plt.xlabel("Date")
    plt.ylabel("Return")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()

    # plot Drawdown
    st.header(f"Draw down plot")
    plt.figure(figsize=(15, 5))
    plt.plot(df['Drawdown'], 'k--', alpha=0.5)
    plt.fill_between(df.index, df['Drawdown'], color='#e56b6f', alpha=0.30)
    plt.title("Drawdown")
    plt.xlabel("Date")
    plt.ylabel("DD")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()

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
