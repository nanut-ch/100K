import streamlit as st
import pandas as pd
import datetime
import altair as alt
import math
import uuid


margin_applied = 0.1

st.logo("logo.png", size = "large")

# Initialize an empty DataFrame to store simulation dates
#if "sim_data" not in st.session_state:
#    st.session_state.sim_data = pd.DataFrame(columns=["sim_date"])

# Initialize the current date in session state if not already set
if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2024, 1, 31)

st.header("Guardian")
st.subheader("Information on current day")

# Move the buttons to the sidebar
# with st.sidebar:

#     st.subheader("Date Navigation")

#     # Create two columns for side-by-side buttons
#     col1, col2 = st.columns(2)

#     with col1:
#         # Button to decrement the date
#         if st.button("⬅️ Prev Day"):
#             st.session_state.current_date -= datetime.timedelta(days=1)

#     with col2:
#         # Button to increment the date
#         if st.button("Next Day ➡️"):
#             st.session_state.current_date += datetime.timedelta(days=1)

# Button to increment the date
with st.sidebar:
    if st.button("END DAY ➡️"):
        st.session_state.current_date += datetime.timedelta(days=1)

        # Append the purchase details to the session state DataFrame
        if "daily_orderbook_history" not in st.session_state:
            if "daily_orderbook" in st.session_state:
                st.session_state.daily_orderbook["Contracts Held"] = st.session_state.daily_orderbook.apply(
                    lambda row: row["Whole Contracts"] + (row["Decimal Contracts"] if row["Order Filled"] == 1 else row["Decimal Used From This Row"]),
                    axis=1
                )
                st.session_state.daily_orderbook_history = st.session_state.daily_orderbook.copy()
        else:
            if not st.session_state.daily_orderbook.empty:
                st.session_state.daily_orderbook["Contracts Held"] = st.session_state.daily_orderbook.apply(
                    lambda row: row["Whole Contracts"] + (row["Decimal Contracts"] if row["Order Filled"] == 1 else row["Decimal Used From This Row"]),
                    axis=1
                )
                st.session_state.daily_orderbook_history = pd.concat(
                [st.session_state.daily_orderbook_history, st.session_state.daily_orderbook],
                ignore_index=True
                )

        # Append the sell details to the session state DataFrame
        if "daily_sellbook_history" not in st.session_state:
            if "daily_sellbook" in st.session_state:
                st.session_state.daily_sellbook["Contracts Sold"] = st.session_state.daily_sellbook.apply(
                    lambda row: row["Whole Contracts"] + (row["Decimal Contracts"] if row["Order Filled"] == 1 else row["Decimal Used From This Row"]),
                    axis=1
                )
                st.session_state.daily_sellbook_history = st.session_state.daily_sellbook.copy()
        else:
            if not st.session_state.daily_sellbook.empty:
                st.session_state.daily_sellbook["Contracts Sold"] = st.session_state.daily_sellbook.apply(
                    lambda row: row["Whole Contracts"] + (row["Decimal Contracts"] if row["Order Filled"] == 1 else row["Decimal Used From This Row"]),
                    axis=1
                )
                st.session_state.daily_sellbook_history = pd.concat(
                    [st.session_state.daily_sellbook_history, st.session_state.daily_sellbook],
                    ignore_index=True
                )
        
        for key in ["contract_date_selector", "contract_date", "daily_orderbook", "number_of_barrels"]:
            st.session_state.pop(key, None)

#st.write("📦 Current Session State Keys:")
#st.write(list(st.session_state.keys()))

# Read the file 'clc1' and plot data
try:
        # Load and preprocess
    df = pd.read_csv("clc1.csv")
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date column is datetime

    # Convert current date from session
    current_date = pd.to_datetime(st.session_state.current_date)
    start_date = current_date - pd.Timedelta(days=365)

    # Filter last 1 year
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= current_date)]

    # ✅ Try to get the exact date
    current_date_row = filtered_df[filtered_df['Date'] == current_date]

    if not current_date_row.empty:
        current_price = current_date_row['Close Price'].iloc[0]
    else:
        # ✅ Fallback: Get the most recent available trading day before current_date
        previous_row = filtered_df[filtered_df['Date'] < current_date].sort_values("Date", ascending=False).head(1)
        if not previous_row.empty:
            current_price = previous_row['Close Price'].iloc[0]
        else:
            current_price = None  # No data in the past year

    # Calculate y-axis limits
    y_min = filtered_df['Close Price'].min() - 10
    y_max = filtered_df['Close Price'].max() + 10

    # Create an Altair chart
    chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X(
        'Date:T',
        title='Date',
        axis=alt.Axis(format='%b %y')  # Format to display month and year (e.g., Jan 2024)
    ),
        y=alt.Y('Close Price:Q', title='Close Price', scale=alt.Scale(domain=[y_min, y_max])),
        tooltip=['Date', 'Close Price']
    ).properties(
        title="WTI Crude Oil Prices (1Y)",
        width=700,
        height=400
    )

    # Create two columns for side-by-side display
    col1, col2 = st.columns(2)

    with col1:
        if current_price is not None:
            # Check if it's a fallback day
            if current_date_row.empty and not previous_row.empty:
                price_date = previous_row['Date'].iloc[0].strftime("%A, %b %d")
                st.metric(
                    label="Current Price",
                    value=f"${current_price:.2f}",
                    delta=f"Last available price from {price_date}"
                )
            else:
                st.metric(label="Current Price", value=f"${current_price:.2f}")
        else:
            st.metric(label="Current Price", value="N/A")


    with col2:
        # Display the current date using st.metric
        st.metric(label="Current Date", value=st.session_state.current_date.strftime('%Y-%m-%d'))

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


except FileNotFoundError:
    st.error("The file 'clc1.csv' was not found. Please ensure it exists in the current directory.")
except Exception as e:
    st.error(f"An error occurred: {e}")

st.divider()

st.subheader("Quantity of protection")

# Dropdown to choose between "Number of Contracts" or "Barrels of Oil"
quantity_type = st.selectbox("Choose Quantity Type:", ["Barrels of Oil", "Number of Contracts"])

# Display the appropriate slider based on the dropdown selection
if quantity_type == "Barrels of Oil":
    slider_value = st.number_input("Number of Barrels:", min_value=0, max_value=100000, value=1300, step=1)

    # Display the number of barrels and equivalent contracts using st.metric
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Number of Barrels", value=slider_value)

    with col2:
        st.metric(label="Equivalent in Contracts", value=f"{slider_value / 1000:.2f} contracts")

    st.session_state.number_of_barrels = slider_value  # Store the number of contracts for later use
elif quantity_type == "Number of Contracts":
    slider_value = st.number_input("Number of Contracts:", min_value=1, max_value=100, value=10, step=1)
    
    # Display the number of contracts and equivalent barrels using st.metric
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Number of Contracts", value=slider_value)

    with col2:
        st.metric(label="Equivalent in Barrels", value=f"{slider_value * 1000} barrels")

    st.session_state.number_of_barrels = slider_value * 1000  # Store the number of contracts for later use


st.subheader("Product specification")

# Create four columns for the buttons
col1, col2, col3, col4 = st.columns(4)

# Initialize contract date in session state if not already set
if "contract_date" not in st.session_state:
    st.session_state.contract_date = None

# Replace buttons with a segmented control for contract dates
contract_options = {
    "Jun '24": datetime.date(2024, 6, 1),
    "Sept '24": datetime.date(2024, 9, 1),
    "Dec '24": datetime.date(2024, 12, 1),
    "Mar '25": datetime.date(2025, 3, 1),
}

selected_contract = st.segmented_control(
    label="Select Contract Date",
    options=list(contract_options.keys()),
    default=None,
    key="contract_date_selector",
)

# Update the session state with the selected contract date
if selected_contract:
    st.session_state.contract_date = contract_options[selected_contract]

# Ensure current_price is set (replace with your logic if needed)
if current_price is None:
    current_price = 75.0  # Default value for demonstration

# Function to find the nearest increment of 2.5 greater than the current price
def next_increment(value, step=2.5, min_val=50, max_val=90):
    rounded_value = math.ceil(value / step) * step  # Use math.ceil to always round up
    return max(min(rounded_value, max_val), min_val)  # Ensure the value stays within the range

# Calculate the next increment of 2.5 greater than the current price
next_price = next_increment(current_price)

# Create a select slider for strike prices
strike_options = [next_price + 2.5, next_price + 5.0, next_price + 7.5, next_price + 10.0]

# Define a format function for the slider
def special_internal_function(value):
    return f"{value:.1f}"

selected_strike = st.select_slider(
    label="Select Guarantee Price",
    options=strike_options,
    value=strike_options[1],
    format_func=special_internal_function
)

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

with col1:
    # Display the selected contract date using st.metric
    if st.session_state.contract_date:
        st.metric(label="Protect Until", value=st.session_state.contract_date.strftime('%Y-%m-%d'))
    else:
        st.metric(label="Protect Until", value="N/A")

with col2:
    # Display the selected strike price using st.metric
    if selected_strike is not None:
        st.metric(label="Selected Strike Price", value=f"{selected_strike:.1f}")
    else:
        st.metric(label="Selected Strike Price", value="N/A")

# Map contract dates to corresponding file names
contract_files = {
    datetime.date(2024, 6, 1): "./expired_options_settle/settle_CL_F24.csv",
    datetime.date(2024, 9, 1): "./expired_options_settle/settle_CL_I24.csv",
    datetime.date(2024, 12, 1): "./expired_options_settle/settle_CL_L24.csv",
    datetime.date(2025, 3, 1): "./expired_options_settle/settle_CL_C25.csv",
}

filtered_df_strike = None
filtered_df_strike_date = None

# Check if a contract date is selected
if st.session_state.contract_date:
    # Get the corresponding file name
    selected_file = contract_files.get(st.session_state.contract_date)

    if selected_file:
        try:
            # Read the selected file
            contract_df = pd.read_csv(selected_file)

            # Remove rows where 'Settlement Price' is NA
            contract_df = contract_df.dropna(subset=['Settlement Price'])

            # Remove duplicate rows
            contract_df = contract_df.drop_duplicates()

            # Format the 'Date' column to exclude time (if it exists)
            if 'Date' in contract_df.columns:
                contract_df['Date'] = pd.to_datetime(contract_df['Date']).dt.strftime('%Y-%m-%d')

            # Filter the DataFrame based on the selected strike value
            if selected_strike is not None:
                filtered_df_strike = contract_df[contract_df['Strike'] == selected_strike]
            #   st.write(f"### Strike: {selected_strike:.1f} and Contract Date: {st.session_state.contract_date}")

                filtered_df_strike_date = filtered_df_strike[filtered_df_strike['Date'] == st.session_state.current_date.strftime('%Y-%m-%d')]
            #   st.dataframe(filtered_df_contract_filtered_date)

            #   st.write(f"### Filtered DataFrame: {filtered_df_contract_filtered_date}")


                if not filtered_df_strike_date.empty:
                    st.metric(label="Price of Insurance per Barrel", value=f"${filtered_df_strike_date['Settlement Price'].iloc[0]*margin_applied:.2f}")
                
                    st.text_input("**Your name**", key="name")
                    
                    # fill_choice = st.segmented_control(
                    #     "Fill Strategy",
                    #     options=[
                    #         "✅ Fill full contracts now + match fractions EOD",
                    #         "⏳ Wait to fill full quantity at EOD only"
                    #     ],
                    #     help="Choose whether to immediately fill full contracts and wait to match fractions, or wait until the entire requested amount (including fraction) is available at end of day."
                    # )

                    # # Map the selected option to a corresponding value
                    # fill_choice_value = 0 if fill_choice == "✅ Fill full contracts now + match fractions EOD" else 1

                    fill_choice_value = 0

                    # Button to purchase insurance
                    if st.button("Purchase Insurance"):
                        # Check if the user has entered their name
                        if 'name' not in st.session_state or st.session_state.name == "":
                            st.error("Please enter your name before purchasing insurance.")
                        elif filtered_df_strike_date is not None and not filtered_df_strike_date.empty:
                            # Extract the settlement price
                            settlement_price = filtered_df_strike_date['Settlement Price'].iloc[0]

                            exp_date = filtered_df_strike_date['Expiry_Date'].iloc[0]

                            # Calculate raw cost
                            raw_cost = settlement_price * st.session_state.number_of_barrels

                            # Calculate the total cost
                            total_cost = raw_cost * margin_applied

                            # Record the purchase details
                            purchase_details = {
                                "User Name": st.session_state.name,
                                "Sim Date": st.session_state.current_date,
                                "Exp Date": exp_date,
                                "Stk Price": selected_strike,
                                "Contracts Bought": st.session_state.number_of_barrels / 1000,
                                "Sett. Price": settlement_price,
                                "Raw Cost": raw_cost,
                                "Profit": raw_cost * margin_applied,
                                "Total Cost": total_cost,
                                "Fill Strategy": fill_choice_value
                            }

                            # Append the purchase details to the session state DataFrame
                            if "purchase_history" not in st.session_state:
                                st.session_state.purchase_history = pd.DataFrame(columns=purchase_details.keys())

                            st.session_state.purchase_history = pd.concat(
                                [st.session_state.purchase_history, pd.DataFrame([purchase_details])],
                                ignore_index=True
                            )
                            st.success("Insurance purchased successfully!")

                            # CORE LOGIC
                        if "purchase_history" in st.session_state:
                            # Step 0: Filter for the current Sim Date
                            filtered_data = st.session_state.purchase_history[
                                st.session_state.purchase_history["Sim Date"] == st.session_state.current_date
                            ].copy()

                            # Add row index to preserve original append order
                            filtered_data["Row Index"] = filtered_data.index

                            # Step 1: Split contracts into whole and decimal parts
                            filtered_data["Whole Contracts"] = filtered_data["Contracts Bought"].apply(math.floor)
                            filtered_data["Decimal Contracts"] = filtered_data["Contracts Bought"] - filtered_data["Whole Contracts"]

                            # Step 2: Group by strike and apply pooling logic per group
                            result_frames = []

                            for (strike, exp_date), group in filtered_data.groupby(["Stk Price", "Exp Date"]):
                                group_sorted = group.sort_values("Row Index").copy()

                                pooled_fraction = 0
                                pooled_before = []
                                pooled_after = []
                                needed_list = []
                                used_from_row = []
                                fraction_filled = []
                                residuals = []
                                unique_id = []

                                for idx, row in group_sorted.iterrows():
                                    user_decimal = row["Decimal Contracts"]

                                    # ✅ NEW: If this row has no decimal contracts, skip pooling logic
                                    if user_decimal == 0:
                                        pooled_before.append(pooled_fraction)
                                        needed_list.append(0)
                                        pooled_after.append(pooled_fraction)
                                        used_from_row.append(0)
                                        fraction_filled.append(0)
                                        residuals.append(0)
                                        unique_id.append(str(uuid.uuid4()))  # Generate a unique ID for each row
                                        continue  # Skip to next row

                                    # Normal pooling logic
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
                                    unique_id.append(str(uuid.uuid4()))  # Generate a unique ID for each row

                                # Add debug columns to group
                                group_sorted["Pooled Fraction Before"] = pooled_before
                                group_sorted["Needed to Complete 1"] = needed_list
                                group_sorted["Decimal Used From This Row"] = used_from_row
                                group_sorted["Pooled Fraction After"] = pooled_after
                                group_sorted["Fraction Filled (via Pool)"] = fraction_filled
                                group_sorted["Decimal Contracts Outstanding"] = residuals
                                group_sorted["UniqueID"] = unique_id

                                # ✅ Add Order Filled column
                                dco_list = group_sorted["Decimal Contracts Outstanding"].tolist()
                                fraction_filled_list = group_sorted["Fraction Filled (via Pool)"].tolist()
                                filled_flags = []

                                for i in range(len(group_sorted)):
                                    if dco_list[i] == 0:
                                        filled_flags.append(1)
                                    elif 1 in fraction_filled_list[i+1:]:  # Safe even on last row
                                        filled_flags.append(1)
                                    else:
                                        filled_flags.append(0)

                                group_sorted["Order Filled"] = filled_flags

                                result_frames.append(group_sorted)

                            # Step 3: Combine all grouped results and restore original row order
                            final_df = pd.concat(result_frames).sort_values("Row Index")

                            # Step 4: Display results
                            st.write("### Purchase History with Fill Logic (Grouped by Strike Price)")
                            st.dataframe(final_df)

                            st.session_state.daily_orderbook = final_df

                            for key in ["name", "number_of_barrels", "selected_strike", "fill_choice_value"]:
                                if key in st.session_state:
                                    del st.session_state[key]

                        else:
                            st.error("Unable to purchase insurance. Please ensure all selections are valid.")
                else:
                    st.metric(label="Price of Insurance per Barrel", value="Insurance not available")

        except FileNotFoundError:
            st.error(f"The file '{selected_file}' was not found. Please ensure it exists in the directory.")
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
    else:
        st.warning("No file is mapped to the selected contract date.")

# if filtered_df_strike_date is not None:
#     if not filtered_df_strike_date.empty:
#         # Display the filtered DataFrame    
#         # Extract the Settlement Price
#         settlement_price = filtered_df_strike_date['Settlement Price'].iloc[0]

#         # Calculate the total value
#         total_value = settlement_price * st.session_state.number_of_barrels

#         # Display the result
#         st.write(f"**Settlement Price:** {settlement_price:.2f}")
#         st.write(f"**Number of Barrels:** {st.session_state.number_of_barrels}")
#         st.write(f"**Total Cost (raw):** {total_value}")
        
#         # Display the total value as the most important number
#         st.markdown(
#             f"""
#             <div style="
#                 margin-top: 30px;
#                 width: 100%;
#             ">
#                 <div style="
#                     background: rgba(255, 255, 255, 0.05);
#                     border: 1px solid rgba(255, 255, 255, 0.1);
#                     border-radius: 16px;
#                     padding: 30px 40px;
#                     box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
#                     backdrop-filter: blur(8px);
#                     -webkit-backdrop-filter: blur(8px);
#                     text-align: center;
#                     color: #90ee90;
#                 ">
#                     <h2 style="font-size: 28px; margin-bottom: 10px;">💰 Total Cost</h2>
#                     <div style="font-size: 40px; font-weight: bold;">
#                         ${total_value*1.02:,.2f}
#                     </div>
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

# # Create two columns for side-by-side buttons
# col1, col2 = st.columns(2)

# # Button to save the simulation date to the DataFrame
# with col1:
#     if st.button("Save Simulation Date"):
#         # Create a new DataFrame with the new entry
#         new_entry = pd.DataFrame({"sim_date": [st.session_state.current_date]})
        
#         # Concatenate the new entry with the existing DataFrame
#         st.session_state.sim_data = pd.concat([st.session_state.sim_data, new_entry], ignore_index=True)
#         st.success("Simulation date saved successfully!")

# with col2:
#     # Button to clear the DataFrame
#     if st.button("Clear All Data"):
#         st.session_state.sim_data = pd.DataFrame(columns=["sim_date"])
#         st.success("All data cleared successfully!")

# # Display the DataFrame
# st.write("Current Simulation Data:")
# st.dataframe(st.session_state.sim_data)