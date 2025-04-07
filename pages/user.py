import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.logo("logo.png", size = "large")

st.header("Query User Purchase History")

st.text_input("**Your name**", key="checkname")

if "purchase_history" in st.session_state:
    # Get the name from the text input
    user_name = st.session_state.checkname

    # Filter the purchase history for the matching user name
    filtered_data = st.session_state.purchase_history[
        st.session_state.purchase_history["User Name"] == user_name
    ]

    # Display the filtered data
    if not filtered_data.empty:
        st.write(f"### Purchase History for {user_name}")
        st.dataframe(filtered_data)
    else:
        st.write(f"No purchase history found for {user_name}.")
else:
    st.write("No purchase history available.")


