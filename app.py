import streamlit as st
import pandas as pd
import datetime
import altair as alt
import math

# Initialize an empty DataFrame to store simulation dates
if "sim_data" not in st.session_state:
    st.session_state.sim_data = pd.DataFrame(columns=["sim_date"])

# Initialize the current date in session state if not already set
if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2024, 1, 2)

st.write("# Welcome to Guardian")

st.text_input("**Your name**", key="name")

# Display the current date
st.write(f"**Current Date:** {st.session_state.current_date}")

# Create three columns for better alignment
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Adjust column widths as needed

# Button to decrement the date
with col1:
    st.write("")  # Center column left intentionally blank

# Empty middle column for spacing
with col2:
    if st.button("⬅️ Previous Day"):
        st.session_state.current_date -= datetime.timedelta(days=1)

# Empty middle column for spacing
with col3:
    if st.button("Next Day ➡️"):
        st.session_state.current_date += datetime.timedelta(days=1)

# Button to increment the date
with col4:
    st.write("")  # Center column left intentionally blank


# Read the file 'clc1' and plot data
try:
    df = pd.read_csv("clc1.csv")
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure the 'Date' column is in datetime format

    # Convert current_date to datetime for comparison
    current_date = pd.to_datetime(st.session_state.current_date)
    start_date = current_date - pd.Timedelta(days=365)

    # Filter data for the last year
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= current_date)]

    # Filter data for the current date
    current_date_row = filtered_df[filtered_df['Date'] == current_date]

    # Check if the row exists and extract the value, otherwise set current_price to None
    if not current_date_row.empty:
        current_price = current_date_row['Close Price'].iloc[0]
    else:
        current_price = None

    # Format the 'Date' column to display only the date (YYYY-MM-DD)
    filtered_df['Date'] = filtered_df['Date'].dt.date

    #st.write("### Filtered Data (Last Year):")
    #st.dataframe(filtered_df)

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

    if current_price is not None:
        st.write(f"### Current Price: {current_price:.2f}")
    else:
        st.write(f"### Current Price: N/A")


    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


except FileNotFoundError:
    st.error("The file 'clc1.csv' was not found. Please ensure it exists in the current directory.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# Dropdown to choose between "Number of Contracts" or "Barrels of Oil"
quantity_type = st.selectbox("Choose Quantity Type:", ["Number of Contracts", "Barrels of Oil"])

# Display the appropriate slider based on the dropdown selection
if quantity_type == "Number of Contracts":
    slider_value = st.slider("Number of Contracts:", min_value=1, max_value=100, value=10)
    st.write(f"Number of Contracts: {slider_value}")
    st.write(f"Equivalent in Barrels: {slider_value * 1000} barrels")

    st.session_state.number_of_barrels = slider_value * 1000  # Store the number of contracts for later use
elif quantity_type == "Barrels of Oil":
    slider_value = st.slider("Number of Barrels:", min_value=0, max_value=10000, value=5000)
    st.write(f"Number of Barrels: {slider_value}")
    st.write(f"Equivalent in Contracts: {slider_value / 1000:.2f} contracts")

    st.session_state.number_of_barrels = slider_value # Store the number of contracts for later use


st.write("## Select Contract Date")

# Create four columns for the buttons
col1, col2, col3, col4 = st.columns(4)

# Initialize contract date in session state if not already set
if "contract_date" not in st.session_state:
    st.session_state.contract_date = None

# Button for Jun '24
with col1:
    if st.button("Jun '24"):
        st.session_state.contract_date = datetime.date(2024, 6, 1)

# Button for Sept '24
with col2:
    if st.button("Sept '24"):
        st.session_state.contract_date = datetime.date(2024, 9, 1)

# Button for Dec '24
with col3:
    if st.button("Dec '24"):
        st.session_state.contract_date = datetime.date(2024, 12, 1)

# Button for Mar '25
with col4:
    if st.button("Mar '25"):
        st.session_state.contract_date = datetime.date(2025, 3, 1)

# Display the selected contract date
if st.session_state.contract_date:
    st.write(f"**Selected Contract Date:** {st.session_state.contract_date}")
else:
    st.write("No contract date selected yet.")

# Ensure current_price is set (replace with your logic if needed)
if current_price is None:
    current_price = 75.0  # Default value for demonstration

# Function to find the nearest increment of 2.5 greater than the current price
def next_increment(value, step=2.5, min_val=50, max_val=90):
    rounded_value = math.ceil(value / step) * step  # Use math.ceil to always round up
    return max(min(rounded_value, max_val), min_val)  # Ensure the value stays within the range

# Calculate the next increment of 2.5 greater than the current price
next_price = next_increment(current_price)

st.write("## Select Strike Price")

# Create 4 buttons
col1, col2, col3, col4 = st.columns(4)

selected_strike = None  # Variable to store the selected strike value

with col1:
    if st.button(f"{next_price + 2.5:.1f}"):
        selected_strike = next_price + 2.5

with col2:
    if st.button(f"{next_price + 5.0:.1f}"):
        selected_strike = next_price + 5.0

with col3:
    if st.button(f"{next_price + 7.5:.1f}"):
        selected_strike = next_price + 7.5

with col4:
    if st.button(f"{next_price + 10.0:.1f}"):
        selected_strike = next_price + 10.0

st.write(f"**Selected Strike Price:** {selected_strike:.1f}" if selected_strike is not None else "No strike price selected yet.")

# Map contract dates to corresponding file names
contract_files = {
    datetime.date(2024, 6, 1): "./expired_options_settle/settle_CL_F24.csv",
    datetime.date(2024, 9, 1): "./expired_options_settle/settle_CL_I24.csv",
    datetime.date(2024, 12, 1): "./expired_options_settle/settle_CL_L24.csv",
    datetime.date(2025, 3, 1): "./expired_options_settle/settle_CL_C25.csv",
}

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
                filtered_df = contract_df[contract_df['Strike'] == selected_strike]
                st.write(f"### Strike: {selected_strike:.1f} and Contract Date: {st.session_state.contract_date}")
                st.dataframe(filtered_df[filtered_df['Date'] == st.session_state.current_date.strftime('%Y-%m-%d')])
            #else:
            #    st.write(f"### Data for {st.session_state.contract_date}:")
            #    st.dataframe(contract_df)

        except FileNotFoundError:
            st.error(f"The file '{selected_file}' was not found. Please ensure it exists in the directory.")
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
    else:
        st.warning("No file is mapped to the selected contract date.")
else:
    st.write("Please select a contract date and strike price to view the data.")


# Check if the filtered DataFrame is not empty
filtered_data = filtered_df[filtered_df['Date'] == st.session_state.current_date.strftime('%Y-%m-%d')]

if not filtered_data.empty:
    # Display the filtered DataFrame
    #st.dataframe(filtered_data)

    # Extract the Settlement Price
    settlement_price = filtered_data['Settlement Price'].iloc[0]

    # Calculate the total value
    total_value = settlement_price * st.session_state.number_of_barrels

    # Display the result
    st.write(f"**Settlement Price:** {settlement_price:.2f}")
    st.write(f"**Number of Barrels:** {st.session_state.number_of_barrels}")
    st.write(f"**Total Cost (raw):** {total_value}")
    
    # Display the total value as the most important number
    st.markdown(
        f"""
        <div style="
            border: 2px solid #4CAF50; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center; 
            background-color: #f9f9f9; 
            color: #4CAF50; 
            font-size: 32px; 
            font-weight: bold;">
            Total Cost: ${total_value*1.02:.2f}
        </div>
        """,
        unsafe_allow_html=True
)
else:
    st.write("No data available for the selected date.")

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