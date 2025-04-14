import streamlit as st
from datetime import datetime
import pandas as pd
import altair as alt
import math

st.logo("logo.png", size = "large")

with st.sidebar:
    st.metric(label="Current Date", value=st.session_state.current_date.strftime("%Y-%m-%d"))

if "purchase_history" in st.session_state:
    # Filter the purchase history for the current date
    filtered_data = st.session_state.purchase_history[
        st.session_state.purchase_history["Sim Date"] == st.session_state.current_date
    ]

    # Display the filtered data
    if not filtered_data.empty:
        st.write(f"### Purchase History for {st.session_state.current_date}")
        st.dataframe(filtered_data)

        # Sum up the Contracts Bought
        total_contracts = filtered_data["Contracts Bought"].sum()

        # Separate whole numbers and decimals
        whole_numbers = math.floor(total_contracts)
        decimals = total_contracts - whole_numbers

        # Create columns for displaying whole numbers and decimals
        col1, col2 = st.columns(2)

        with col1:
            st.metric(label="Whole contract fufilled", value=whole_numbers)

        with col2:
            st.metric(label="Fractional contract outstanding", value=f"{decimals:.2f}")

        # Display the decimal portion as a percentage
        st.write("### Fractional Shares Outstanding")
        st.progress(decimals, text=f"{decimals:.2%}")
    else:
        st.write(f"No purchase history found for {st.session_state.current_date}.")
else:
    st.write("No purchase history available.")