import streamlit as st


def all_stats(json_obj):
    for s_name, df in json_obj.items():
        st.write(s_name)
        st.table(df)
