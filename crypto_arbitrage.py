import ccxt
import time
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Initialize US-based exchange connections
binance_us = ccxt.binanceus()
coinbase = ccxt.coinbase()  # Fixed Coinbase API
kraken = ccxt.kraken()

# Connect to SQLite Database
conn = sqlite3.connect("crypto_arbitrage.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS price_history (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    exchange TEXT,
    symbol TEXT,
    price REAL
)
""")
conn.commit()

# Function to fetch prices from multiple US-based exchanges
def fetch_prices(symbol="BTC/USDT"):
    prices = {}

    try:
        prices["Binance US"] = binance_us.fetch_ticker(symbol)['last']
    except Exception as e:
        print(f"Error fetching Binance US price: {e}")
        prices["Binance US"] = None

    try:
        prices["Coinbase"] = coinbase.fetch_ticker(symbol)['last']
    except Exception as e:
        print(f"Error fetching Coinbase price: {e}")
        prices["Coinbase"] = None

    try:
        prices["Kraken"] = kraken.fetch_ticker(symbol)['last']
    except Exception as e:
        print(f"Error fetching Kraken price: {e}")
        prices["Kraken"] = None

    print(f"Fetching prices... {prices}")  # Single print statement for fetching
    return prices

# Store prices in SQLite
def store_prices(symbol="BTC/USDT"):
    prices = fetch_prices(symbol)
    for exchange, price in prices.items():
        if price is not None:
            cursor.execute("INSERT INTO price_history (exchange, symbol, price) VALUES (?, ?, ?)", (exchange, symbol, price))
    conn.commit()
    return prices  # Return prices for reuse

# Check arbitrage opportunities
def check_arbitrage(symbol="BTC/USDT", threshold=0.005, prices=None):  # 0.5% threshold
    if prices is None:
        prices = fetch_prices(symbol)

    # Filter out None values
    valid_prices = {ex: price for ex, price in prices.items() if price is not None}
    
    if len(valid_prices) < 2:
        print("Not enough valid prices for arbitrage detection.")
        return
    
    # Find min and max prices
    min_ex, min_price = min(valid_prices.items(), key=lambda x: x[1])
    max_ex, max_price = max(valid_prices.items(), key=lambda x: x[1])

    price_diff = max_price - min_price
    percentage_diff = price_diff / min_price

    if percentage_diff > threshold:
        print(f"🚀 Arbitrage Opportunity Detected!")
        print(f"Buy from {min_ex} at ${min_price} and sell on {max_ex} at ${max_price}")
        print(f"Profit: {price_diff:.2f} USD ({percentage_diff*100:.2f}%)")
    else:
        print("No arbitrage opportunity.")


# Function to analyze price trends from the database
def analyze_price_trends():
    df = pd.read_sql_query("SELECT timestamp, exchange, price FROM price_history", conn)

    if df.empty:
        print("No data available for analysis.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    plt.figure(figsize=(10, 5))
    for exchange in df['exchange'].unique():
        subset = df[df['exchange'] == exchange]
        plt.plot(subset['timestamp'], subset['price'], label=exchange)

    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.title("Crypto Price Trend Across Exchanges")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Run every 10 seconds and store prices in the database
if __name__ == "__main__":
    for _ in range(10):  # Collect data 10 times (~100 seconds)
        prices = store_prices()  # Store and get prices
        check_arbitrage(prices=prices)  # Pass the already fetched prices
        time.sleep(10)
    
    # Analyze trends after collecting data
    analyze_price_trends()

    # Close DB connection
    conn.close()
