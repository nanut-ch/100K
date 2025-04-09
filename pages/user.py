import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.logo("logo.png", size = "large")

st.text_input("**Your name**", key="checkname")

st.header("Query User Purchase (Today)")

st.metric(label="Current Date", value=st.session_state.current_date.strftime("%Y-%m-%d"))

st.divider()

user_name = st.session_state.checkname

st.header("Query User Purchase (History)")

if "purchase_history" in st.session_state:
    # Get the name from the text input

    # Filter the purchase history for the matching user name
    filtered_data = st.session_state.purchase_history[
        st.session_state.purchase_history["User Name"] == user_name
    ]

    # Display the filtered data
    if not filtered_data.empty:
        st.write(f"### Current Holdings for {user_name}")
        #st.dataframe(filtered_data)

        filtered_data["Select"] = False


        selected_rows = st.data_editor(
            filtered_data,
            column_order=["Select", "User Name", "Stk Price", "Contracts Bought", "Order Filled"],
            use_container_width=True,
            num_rows="fixed",         # 🔒 Prevents adding new rows
            hide_index=True
        )

        st.button("Sell Selected")
    else:
        st.write(f"No purchase history found for {user_name}.")
else:
    st.write("No purchase history available.")




if "daily_orderbook" in st.session_state:
    # Filter the daily order book for the matching user name
    filtered_data = st.session_state.daily_orderbook[
        st.session_state.daily_orderbook["User Name"] == user_name
    ]

    # Replace 1 with check emoji and 0 with cross emoji in the "Order Filled" column
    filtered_data["Status"] = filtered_data["Order Filled"].replace({1: "✅", 0: "❌"})

    # Create a new column 'Outstanding'
    filtered_data["Outstanding"] = filtered_data.apply(
        lambda row: 0 if row["Order Filled"] == 1 else row["Decimal Contracts Outstanding"], axis=1
    )
    filtered_data = filtered_data[["Sim Date", "Exp Date", "Contracts Bought", "Status", "Outstanding"]]

    # Display the filtered data
    if not filtered_data.empty:
        st.write(f"### Daily Purchase Book for {user_name}")
        st.dataframe(filtered_data)
    else:
        st.write(f"No Daily Purchase Book found for {user_name}.")
    
