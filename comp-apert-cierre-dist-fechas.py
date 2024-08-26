import yfinance as yf
import pandas as pd
import datetime as dt
import streamlit as st

# List of tickers
tickers = ["YPFD.BA", "YPF"]

# Function to fetch trading data for the closest next or previous available trading date
def fetch_trading_data_for_ratio(tickers, date, mode="next"):
    data = {}
    
    for ticker in tickers:
        stock_data = yf.Ticker(ticker)
        # Fetch data within a wide range to ensure capturing the desired trading date
        df = stock_data.history(start=date - dt.timedelta(days=30), end=date + dt.timedelta(days=30))
        df = df.dropna()

        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.tz_convert(None)  # Remove timezone information

        trading_date = None
        if mode == "next":
            # Search for the closest next trading date (date on or after the selected date)
            trading_date = df.index[df.index >= pd.Timestamp(date)].min()
        else:
            # Search for the closest previous trading date (date on or before the selected date)
            trading_date = df.index[df.index <= pd.Timestamp(date)].max()

        if pd.isna(trading_date):
            continue  # Skip if no valid date is found

        closest_data = df.loc[trading_date]

        data[ticker] = {
            'open': closest_data['Open'],
            'close': closest_data['Close'],
            'date': trading_date.date()
        }
    
    # Ensure data for all tickers is available
    if len(data) == len(tickers):  # Check if data for both tickers is available
        return data
    else:
        # If data is not available for either ticker, try the next or previous trading day
        if mode == "next":
            return fetch_trading_data_for_ratio(tickers, trading_date + dt.timedelta(days=1), mode="next")
        else:
            return fetch_trading_data_for_ratio(tickers, trading_date - dt.timedelta(days=1), mode="previous")

# Streamlit: User selects two dates
st.title("Análisis del ratio YPFD/YPF en diferentes fechas")
min_date = dt.datetime(2000, 1, 1)
max_date = dt.datetime.now()

selected_date_1 = st.date_input(
    "Choose Date 1",
    value=max_date - dt.timedelta(days=1),
    min_value=min_date,
    max_value=max_date
)

selected_date_2 = st.date_input(
    "Choose Date 2",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Fetch data for Date 1 and Date 2 with the specific logic for the ratio
try:
    data_date_1 = fetch_trading_data_for_ratio(tickers, selected_date_1, mode="next")
    data_date_2 = fetch_trading_data_for_ratio(tickers, selected_date_2, mode="previous")
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Display the fetched data
if data_date_1 and data_date_2:
    st.write(f"Data for Date 1 (Closest Next Trading Day): {data_date_1}")
    st.write(f"Data for Date 2 (Closest Previous Trading Day): {data_date_2}")
else:
    st.warning("Data could not be retrieved for the specified dates.")
