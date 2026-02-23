import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import json, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL')

WATCHLIST = ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMD', 'META', 'GOOGL']
WEB_PATH = 'status.json'

alpaca = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def get_quant_metrics(df):
    if len(df) < 15: return 50, 0, 0

    # ATR
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    loss_val = loss.iloc[-1]
    if loss_val == 0: rsi = 100
    else: rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss_val)))

    return rsi, atr

print("Forcing Refresh of ALL 7 Assets...")
dashboard_data = []

for symbol in WATCHLIST:
    try:
        bars = alpaca.get_bars(symbol, "15Min", limit=50)
        df = pd.DataFrame([b._raw for b in bars])
        if not df.empty:
            df['t'] = pd.to_datetime(df['t'])
            df.set_index('t', inplace=True)
            df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'o': 'open', 'v': 'volume'}, inplace=True)

            rsi, atr = get_quant_metrics(df)
            price = df['close'].iloc[-1]

            dashboard_data.append({
                "symbol": symbol, "price": round(price, 2),
                "rsi": round(rsi, 2), "atr": round(atr, 2), "status": "SCANNING"
            })
            print(f"✅ Processed {symbol}")
        else:
            print(f"⚠️ No data for {symbol}")
    except Exception as e:
        print(f"❌ Error {symbol}: {e}")

with open(WEB_PATH, 'w') as f:
    json.dump({"update": datetime.now().strftime("%H:%M"), "assets": dashboard_data}, f)
print("Refresh Complete.")
