import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
import streamlit as st

# List of tickers and shares outstanding data
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

# Function to fetch data for a specific date, using the next available trading date if necessary
def fetch_data_for_date(tickers, date):
    data = {}
    
    for ticker in tickers:
        stock_data = yf.Ticker(ticker)
        df = stock_data.history(start=date - dt.timedelta(days=30), end=date + dt.timedelta(days=1))
        df = df.dropna()

        # If no data is found, pick the next available trading date
        if len(df) < 1:
            continue
        else:
            df = df[df.index >= date]  # Filter out dates earlier than the selected date
            if len(df) < 1:  # If no data is available after filtering, skip to the next ticker
                continue

        closest_data = df.iloc[0]  # Use the first available date after filtering
        actual_date = df.index[0].date()

        data[ticker] = {
            'open': closest_data['Open'],
            'close': closest_data['Close'],
            'date': actual_date
        }
    
    return data

# Set the minimum and maximum dates for the calendar widget
min_date = dt.datetime(2000, 1, 1)
max_date = dt.datetime.now()

# Streamlit: User selects two dates
st.title("Comparación de precios de acciones en dos fechas diferentes")
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

# Fetch data for both dates
try:
    data_date_1 = fetch_data_for_date(tickers, selected_date_1)
    data_date_2 = fetch_data_for_date(tickers, selected_date_2)
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

# Calculate percentage differences and quotients
def calculate_metrics(data_1, data_2):
    metrics = {}
    for ticker in data_1:
        if ticker in data_2:
            open_price_1 = data_1[ticker]['open']
            close_price_2 = data_2[ticker]['close']
            
            # Calculate percentage difference between open price of Date 1 and close price of Date 2
            percent_diff = (close_price_2 - open_price_1) / open_price_1 * 100
            
            # Calculate quotients for Date 1 and Date 2
            if "YPFD.BA" in data_1 and "YPF" in data_1:
                quotient_1 = open_price_1 / (data_1["YPFD.BA"]['open'] / data_1["YPF"]['open'])
                quotient_2 = close_price_2 / (data_2["YPFD.BA"]['close'] / data_2["YPF"]['close'])
                quotient_diff = (quotient_2 - quotient_1) / quotient_1 * 100
            else:
                quotient_diff = np.nan
            
            metrics[ticker] = {
                'percent_diff': percent_diff,
                'quotient_diff': quotient_diff
            }
    
    return metrics

metrics = calculate_metrics(data_date_1, data_date_2)

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
    plt.title(f"{title} (Data from {date_1} to {date_2})", fontsize=18)
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

# Create the first bar plot
try:
    create_bar_plot(metrics, 'percent_diff', 'Difference in Percentage Between Open Price on Date 1 and Close Price on Date 2', actual_date_1, actual_date_2)
except Exception as e:
    st.error(f"Error creating the first plot: {e}")

# Create the second bar plot
try:
    create_bar_plot(metrics, 'quotient_diff', 'Difference in Percentage Between Quotient 1 and Quotient 2', actual_date_1, actual_date_2)
except Exception as e:
    st.error(f"Error creating the second plot: {e}")
