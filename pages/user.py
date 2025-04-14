import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import uuid
import math

st.logo("logo.png", size = "large")

st.text_input("**Your name**", key="checkname")

st.header("Query User Purchase (Today)")

st.metric(label="Current Date", value=st.session_state.current_date.strftime("%Y-%m-%d"))

st.divider()

user_name = st.session_state.checkname

st.header("Query User Purchase (History)")

if "daily_orderbook_history" in st.session_state:
        # Get the name from the text input

    # Filter the purchase history for the matching user name
    filtered_data = st.session_state.daily_orderbook_history[
        st.session_state.daily_orderbook_history["User Name"] == user_name
    ]

    # Display the filtered data
    if not filtered_data.empty:
        st.write(f"### Current Holdings for {user_name}")
        #st.dataframe(filtered_data)

        filtered_data["Select"] = False

        selected_rows = st.data_editor(
            filtered_data,
            column_order=["Select", "User Name", "Stk Price", "Contracts Held", "UniqueID"],
            use_container_width=True,
            num_rows="fixed",         # 🔒 Prevents adding new rows
            hide_index=True
        )

        if st.button("Sell Selected"):
            # Step 1: Grab the selected rows
            selected_to_sell = selected_rows[selected_rows["Select"] == True]

            if selected_to_sell.empty:
                st.warning("No orders selected to sell.")
            else:
                if "sale_history" in st.session_state and selected_rows["UniqueID"].isin(st.session_state.sale_history["UniqueID"]).any():
                    st.warning("Sell order already exists. Please select a different order.")
                else:
                    st.success("Processing Sale(s)...")

                    # Step 2: Invert and append to a new session log
                    for _, row in selected_to_sell.iterrows():
                        sale_details = {
                            "User Name": row["User Name"],
                            "UniqueID": row["UniqueID"],
                            "Sim Date": st.session_state.current_date,
                            "Exp Date": row["Exp Date"],
                            "Stk Price": row["Stk Price"],
                            "Contracts Held": row["Contracts Held"],
                            #"Contracts Sold": row["Contracts Bought"],
                            "Sett. Price": None,  # you can update with real price logic if needed
                            "Fill Strategy": "Immediate + Pool",
                        }

                        if "sale_history" not in st.session_state:
                            st.session_state.sale_history = pd.DataFrame(columns=sale_details.keys())

                        st.session_state.sale_history = pd.concat(
                            [st.session_state.sale_history, pd.DataFrame([sale_details])],
                            ignore_index=True
                        )

                    # Step 3: Apply fractional sell logic (mirroring core logic)
                    sale_data = st.session_state.sale_history[
                        st.session_state.sale_history["Sim Date"] == st.session_state.current_date
                    ].copy()

                    sale_data["Row Index"] = sale_data.index
                    sale_data["Whole Contracts"] = sale_data["Contracts Held"].apply(math.floor)
                    sale_data["Decimal Contracts"] = sale_data["Contracts Held"] - sale_data["Whole Contracts"]

                    result_frames = []

                    for (strike, exp_date), group in sale_data.groupby(["Stk Price", "Exp Date"]):
                        group_sorted = group.sort_values("Row Index").copy()

                        pooled_fraction = 0
                        pooled_before = []
                        pooled_after = []
                        needed_list = []
                        used_from_row = []
                        fraction_filled = []
                        residuals = []

                        for idx, row in group_sorted.iterrows():
                            user_decimal = row["Decimal Contracts"]

                            if user_decimal == 0:
                                pooled_before.append(pooled_fraction)
                                needed_list.append(0)
                                pooled_after.append(pooled_fraction)
                                used_from_row.append(0)
                                fraction_filled.append(0)
                                residuals.append(0)
                                continue

                            pooled_before.append(pooled_fraction)
                            needed = 1 - pooled_fraction if pooled_fraction > 0 else 0
                            needed_list.append(needed)

                            if user_decimal >= needed and pooled_fraction > 0:
                                used = needed
                                pooled_fraction = user_decimal - used
                                fraction_filled.append(1)
                            else:
                                used = 0
                                pooled_fraction += user_decimal
                                fraction_filled.append(0)

                            pooled_after.append(pooled_fraction)
                            used_from_row.append(used)
                            residuals.append(user_decimal - used)

                        group_sorted["Pooled Fraction Before"] = pooled_before
                        group_sorted["Needed to Complete 1"] = needed_list
                        group_sorted["Decimal Used From This Row"] = used_from_row
                        group_sorted["Pooled Fraction After"] = pooled_after
                        group_sorted["Fraction Filled (via Pool)"] = fraction_filled
                        group_sorted["Decimal Contracts Outstanding"] = residuals

                        # Determine if order is filled
                        dco_list = group_sorted["Decimal Contracts Outstanding"].tolist()
                        fraction_filled_list = group_sorted["Fraction Filled (via Pool)"].tolist()
                        filled_flags = []

                        for i in range(len(group_sorted)):
                            if dco_list[i] == 0:
                                filled_flags.append(1)
                            elif 1 in fraction_filled_list[i+1:]:
                                filled_flags.append(1)
                            else:
                                filled_flags.append(0)

                        group_sorted["Order Filled"] = filled_flags

                        result_frames.append(group_sorted)

                    final_sell_df = pd.concat(result_frames).sort_values("Row Index")
                    st.session_state.daily_sellbook = final_sell_df

                    # Optional: Show results
                    st.write("### Sale Orderbook with Fill Logic")
                    st.dataframe(final_sell_df)

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
    
