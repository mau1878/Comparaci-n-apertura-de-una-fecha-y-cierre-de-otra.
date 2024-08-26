import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
import streamlit as st

# List of tickers
tickers = [
    "GGAL.BA", "YPFD.BA", "PAMP.BA", "TXAR.BA", "ALUA.BA", "CRES.BA", "SUPV.BA", "CEPU.BA", "BMA.BA",
    "TGSU2.BA", "TRAN.BA", "EDN.BA", "LOMA.BA", "MIRG.BA", "DGCU2.BA", "BBAR.BA", "MOLI.BA", "TGNO4.BA",
    "CGPA2.BA", "COME.BA", "IRSA.BA", "BYMA.BA", "TECO2.BA", "METR.BA", "CECO2.BA", "BHIP.BA", "AGRO.BA",
    "LEDE.BA", "CVH.BA", "HAVA.BA", "AUSO.BA", "VALO.BA", "SEMI.BA", "INVJ.BA", "CTIO.BA", "MORI.BA",
    "HARG.BA", "GCLA.BA", "SAMI.BA", "BOLT.BA", "MOLA.BA", "CAPX.BA", "OEST.BA", "LONG.BA", "GCDI.BA",
    "GBAN.BA", "CELU.BA", "FERR.BA", "CADO.BA", "GAMI.BA", "PATA.BA", "CARC.BA", "BPAT.BA", "RICH.BA",
    "INTR.BA", "GARO.BA", "FIPL.BA", "GRIM.BA", "DYCA.BA", "POLL.BA", "DGCE.BA", "DOME.BA", "ROSE.BA",
    "RIGO.BA", "MTR.BA"
]

# Function to fetch data for the closest next or previous available trading date
def fetch_trading_data(tickers, date, mode="next"):
    data = {}
    
    for ticker in tickers:
        stock_data = yf.Ticker(ticker)
        # Fetch data within a wide range to ensure capturing the desired trading date
        df = stock_data.history(start=date - dt.timedelta(days=7), end=date + dt.timedelta(days=7))
        df = df.dropna()

        # Ensure index is DatetimeIndex and timezone is handled
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.tz_convert(None)  # Remove timezone information

        if mode == "next":
            # Identify the closest next trading date (date on or after the selected date)
            trading_date = df.index[df.index >= pd.Timestamp(date)].min()
        else:
            # Identify the closest previous trading date (date on or before the selected date)
            trading_date = df.index[df.index <= pd.Timestamp(date)].max()

        if pd.isna(trading_date):
            continue  # Skip if no valid date is found

        closest_data = df.loc[trading_date]

        data[ticker] = {
            'open': closest_data['Open'],
            'close': closest_data['Close'],
            'date': trading_date.date()
        }
    
    return data

# Function to handle missing data for specific tickers
def handle_missing_data(tickers, date_1, date_2):
    data_date_1 = fetch_trading_data(tickers, date_1, mode="next")
    data_date_2 = fetch_trading_data(tickers, date_2, mode="previous")
    
    # Ensure that data for both YPFD.BA and YPF is available for calculations
    if "YPFD.BA" not in data_date_1 or "YPF" not in data_date_1:
        data_date_1 = fetch_trading_data(tickers, date_1, mode="previous")
    if "YPFD.BA" not in data_date_2 or "YPF" not in data_date_2:
        data_date_2 = fetch_trading_data(tickers, date_2, mode="next")
    
    return data_date_1, data_date_2

# Streamlit: User selects two dates
st.title("Comparación de precios de acciones en dos fechas diferentes")
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

# Fetch data for the selected dates
try:
    data_date_1, data_date_2 = handle_missing_data(tickers, selected_date_1, selected_date_2)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Function to clean data
def clean_data(data):
    clean_data = {}
    for ticker, d in data.items():
        if not np.isnan(d['open']) and not np.isnan(d['close']):
            clean_data[ticker] = d
    return clean_data

data_date_1 = clean_data(data_date_1)
data_date_2 = clean_data(data_date_2)

# Function to create bar plots
def create_bar_plot(metrics, metric, title, date_1, date_2):
    # Filter out tickers with no data or NaN values for the metric
    metrics = {ticker: info for ticker, info in metrics.items() if not np.isnan(info[metric])}
    
    if not metrics:
        st.warning(f"No data to display for {title}")
        return
    
    # Convert data to DataFrame for easy plotting
    df = pd.DataFrame(metrics).T
    df = df.sort_values(by=metric, ascending=False)
    
    plt.figure(figsize=(14, 18))  # Increased height for better label visibility
    sns.barplot(x=df[metric], y=df.index, palette="viridis")
    plt.title(f'{title} (Data from {date_1} to {date_2})', fontsize=18)
    plt.xlabel(f'{metric} (%)', fontsize=16)
    plt.ylabel('Ticker', fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', linewidth=0.7)
    # Add subtle watermark
    plt.text(0.5, 0.5, "MTaurus - X:MTaurus_ok", fontsize=12, color='gray',
             ha='center', va='center', alpha=0.5, transform=plt.gcf().transFigure)
    st.pyplot(plt)

# Get the actual dates used for data retrieval
actual_date_1 = list(data_date_1.values())[0]['date'] if data_date_1 else selected_date_1
actual_date_2 = list(data_date_2.values())[0]['date'] if data_date_2 else selected_date_2

# Create the first bar plot with actual dates
try:
    create_bar_plot(metrics, 'percent_diff', 'Difference in Percentage Between Open Price on Date 1 and Close Price on Date 2', actual_date_1, actual_date_2)
except Exception as e:
    st.error(f"Error creating the first plot: {e}")

# Fetch the values for the ratio "YPFD/YPF" and update data
def fetch_ratio_values(date):
    data = fetch_trading_data(tickers, date)
    if "YPFD.BA" in data and "YPF" in data:
        ypf_open = data["YPF"]['open']
        ypfd_open = data["YPFD.BA"]['open']
        ratio = ypfd_open / ypf_open
        return ratio
    return np.nan

# Get the ratios for the selected dates
ratio_date_1 = fetch_ratio_values(actual_date_1)
ratio_date_2 = fetch_ratio_values(actual_date_2)

# Update metrics with ratio adjustment
def update_metrics_with_ratio(metrics, ratio_1, ratio_2):
    updated_metrics = {}
    for ticker, info in metrics.items():
        if ratio_1 and ratio_2:
            adjusted_open_price_1 = info['open'] / ratio_1
            adjusted_close_price_2 = info['close'] / ratio_2
            percent_diff = (adjusted_close_price_2 - adjusted_open_price_1) / adjusted_open_price_1 * 100
            updated_metrics[ticker] = {'percent_diff': percent_diff}
    return updated_metrics

# Update metrics with ratio
metrics = update_metrics_with_ratio(metrics, ratio_date_1, ratio_date_2)

# Create the second bar plot with actual dates
try:
    create_bar_plot(metrics, 'percent_diff', 'Difference in Percentage Adjusted by YPFD/YPF Ratio', actual_date_1, actual_date_2)
except Exception as e:
    st.error(f"Error creating the second plot: {e}")
