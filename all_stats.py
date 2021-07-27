import streamlit as st
import pandas as pd


def all_stats(json_obj):

    tot_df = pd.DataFrame()

    tot_df["PNL"] = []

    for s_name, df in json_obj.items():
        tot_df["PNL"] += df["PNL"]
        # st.write(s_name)
        # st.table(df)

    st.table(tot_df)
