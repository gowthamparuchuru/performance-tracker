# Internal packages
import json
import streamlit as st
import hashlib
import time

# Custom packages
from all_stats import all_stats
from today_stats import today_stats
from single_stats import single_stats

# Extrenal packages
import pandas as pd
import zmq

st.set_option('deprecation.showPyplotGlobalUse', False)

# pas
pswd = st.sidebar.text_input("Enter Password:", type="password")
st.sidebar.button("Enter")

st.title("**📊PERFORMANCE TRACKER🤫**")
if pswd == "":
    st.info('Enter password!👋')
elif hashlib.sha256(pswd.encode()).hexdigest() != st.secrets["PSWD"]:
    st.error('Enter correct password!✋')
else:

    # should add corner cases.
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{st.secrets['IP']}:{st.secrets['PORT']}")
    socket.send(pswd.encode())
    message = socket.recv()

    # load data.
    fetched_data = json.loads(message)

    # select box
    strategies = ['Today', "Portfolio"]
    strategies += list(fetched_data.keys())

    selected_strat = st.sidebar.selectbox(
        'Select strategy',
        strategies, 0
    )

    # brokerage radio button
    chosen = st.sidebar.radio(
        'Brokerage',
        ("Yes", "No"))

    # select analysis type.
    analysis_type = st.sidebar.selectbox(
        'Analysis',
        ("Absolute", "Per lot"), 0
    )

    # create pandas dataframes
    json_obj = {}
    for k, v in fetched_data.items():
        json_obj[k] = pd.read_json(v)

    # process based on analysis.
    if analysis_type == "Absolute":
        pass
    elif analysis_type == "Per lot":
        for v in json_obj.values():
            v["Capital"] = round(v["Capital"]/v["Lot"], 2)
            v["Brokerage"] = round(v["Brokerage"]/v["Lot"], 2)
            v["PNL"] = round(v["PNL"]/v["Lot"], 2)
            v["Lot"] = 1

    # process based on brokerage.
    if chosen == "Yes":
        for v in json_obj.values():
            v["PNL"] = v["PNL"] - v["Brokerage"]

    # render page based by selected option.
    if selected_strat == "Today":
        today_stats(json_obj)
    elif selected_strat == "Portfolio":
        all_stats(json_obj)
    else:
        df = json_obj[selected_strat]
        single_stats(selected_strat, df)
