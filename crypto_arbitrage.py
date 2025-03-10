import ccxt
import time

# Initialize US-based exchange connections
binance_us = ccxt.binanceus()
coinbase = ccxt.coinbase()  # Fixed Coinbase API
kraken = ccxt.kraken()

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

    return prices

# Check arbitrage opportunities
def check_arbitrage(symbol="BTC/USDT", threshold=0.005):  # 0.5% threshold
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

# Run every 10 seconds
while True:
    check_arbitrage()
    time.sleep(10)
