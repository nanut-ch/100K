import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.logo("logo.png", size = "large")

st.header("Backend")

# Clear session state button
if st.button("Clear Session State"):
    st.session_state.clear()

st.divider()
st.header("Monthly Summary")

# Check if purchase history exists
if "purchase_history" in st.session_state:
    # Ensure Sim Date is datetime
    st.session_state.purchase_history["Sim Date"] = pd.to_datetime(st.session_state.purchase_history["Sim Date"])

    # User selects a month
    selected_month = st.selectbox(
        "Select a Month",
        pd.date_range(start="2024-01-01", end="2025-03-31", freq="MS").strftime("%Y-%m").tolist()
    )

    # Get start and end of selected month
    start_of_month = pd.to_datetime(selected_month + "-01")
    end_of_month = (start_of_month + pd.offsets.MonthEnd(1))

    # Filter data for selected month
    filtered_data = st.session_state.purchase_history[
        (st.session_state.purchase_history["Sim Date"] >= start_of_month) &
        (st.session_state.purchase_history["Sim Date"] <= end_of_month)
    ]

    if not filtered_data.empty:
        # Group by day and sum profit
        profit_by_date = filtered_data.groupby(filtered_data["Sim Date"].dt.date)["Profit"].sum().reset_index()
        profit_by_date.columns = ["Date", "Total Profit"]

        # Create full date range for the selected month
        full_dates = pd.DataFrame({
            "Date": pd.date_range(start=start_of_month, end=end_of_month).date
        })

        # Merge with profit data (fill missing days with 0)
        full_profit = pd.merge(full_dates, profit_by_date, on="Date", how="left").fillna(0)

        # Display the filtered data
        st.write(f"### Purchase History for {selected_month}")
        st.dataframe(filtered_data)

        # Create bar chart
        chart = alt.Chart(full_profit).mark_bar().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%b %d")),
            y=alt.Y("Total Profit:Q", title="Total Profit"),
            tooltip=["Date:T", "Total Profit:Q"]
        ).properties(
            title=f"Profit Breakdown for {selected_month}",
            width=700,
            height=400
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.write(f"No purchase history found for {selected_month}.")
else:
    st.write("No purchase history found.")
