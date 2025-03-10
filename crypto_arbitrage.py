import ccxt
import time

# Initialize exchange connections
binance = ccxt.binance()
kraken = ccxt.kraken()

def fetch_prices(symbol="BTC/USDT"):
    binance_price = binance.fetch_ticker(symbol)['last']
    kraken_price = kraken.fetch_ticker(symbol)['last']
    
    return {"Binance": binance_price, "Kraken": kraken_price}

while True:
    try:
        prices = fetch_prices()
        print(f"Binance: {prices['Binance']}, Kraken: {prices['Kraken']}")
        time.sleep(5)  # Fetch data every 5 seconds
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
        time.sleep(10)  # Wait before retrying
    except ccxt.BaseError as e:
        print(f"Exchange error: {e}")
        time.sleep(10)
