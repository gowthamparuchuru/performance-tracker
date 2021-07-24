import streamlit as st
from datetime import datetime

# Extrenal packages
import pandas as pd
import matplotlib.pyplot as plt


def today_stats(json_obj):
    stats = {}
    for strat in json_obj.keys():
        row = json_obj[strat].iloc[-1]
        date = json_obj[strat].index[-1]
        stats[strat] = row

    date = datetime.strftime(date, "%d-%b-%Y")
    st.header(f"Date: {date}")

    df = pd.concat(stats, axis=1)
    df = df.T

    df.loc["Net"] = df.sum()

    df["ROI"] = round(100*df["PNL"]/df["Capital"], 2)

    st.table(df)

    st.header(f"Today profit and loss")
    plt.figure(figsize=(15, 7))
    plt.bar(df.index, df["PNL"], color=(
        df["PNL"] > 0).map({True: 'g', False: 'r'}))
    plt.title("Today profit and loss")
    plt.xlabel("Strategy")
    plt.ylabel("Profit and Loss")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()

    st.header(f"Today ROI")
    plt.figure(figsize=(15, 7))
    plt.bar(df.index, df["ROI"], color=(
        df["PNL"] > 0).map({True: 'g', False: 'r'}))
    plt.title("Today ROI")
    plt.xlabel("Strategy")
    plt.ylabel("ROI")
    plt.grid('on', linestyle='--')
    st.pyplot()
    plt.clf()
