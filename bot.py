import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import time, json, os
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURATION EXPERT (Architecture Low-RAM) ---
load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('ALPACA_BASE_URL')

WATCHLIST = ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMD', 'META', 'GOOGL']
WEB_PATH = 'status.json' # Adjusted for local sandbox permissions

if not all([API_KEY, SECRET_KEY, BASE_URL]):
    print("❌ Erreur: Clés API manquantes dans .env")
    exit(1)

alpaca = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def get_bars_df(symbol, timeframe, limit):
    """Helper to convert Alpaca Bars to DataFrame"""
    try:
        bars = alpaca.get_bars(symbol, timeframe, limit=limit)
        df = pd.DataFrame([b._raw for b in bars])
        if not df.empty:
            df['t'] = pd.to_datetime(df['t'])
            df.set_index('t', inplace=True)
            df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'o': 'open', 'v': 'volume'}, inplace=True)
        return df
    except Exception as e:
        print(f"Data fetch error for {symbol}: {e}")
        return pd.DataFrame()

def get_quant_metrics(df):
    """ Moteur de calcul vectorisé (Optimisé CPU) """
    if len(df) < 15: return 50, 0, 0 # Not enough data

    # 1. ATR (Average True Range) pour Stop-Loss dynamique
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]

    # 2. RSI & EMA
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    # Handle division by zero for RSI
    loss_val = loss.iloc[-1]
    if loss_val == 0:
        rsi = 100
    else:
        rs = gain.iloc[-1] / loss_val
        rsi = 100 - (100 / (1 + rs))

    ema = df['close'].ewm(span=9).mean().iloc[-1]

    return rsi, ema, atr

def compute_position_size(cash, price, atr):
    """ Application stricte de la Règle des 3% et Kelly """
    risk_per_trade = cash * 0.03  # Risque max 3% du capital
    stop_loss_dist = atr * 2      # SL à 2x l'ATR (volatilité réelle)

    if stop_loss_dist == 0: return 0, 0, 0

    qty = int(risk_per_trade / stop_loss_dist)

    # Limite Kelly Fractionnaire (Sécurité - Max 10% allocation)
    if price > 0:
        kelly_limit = int((cash * 0.10) / price)
        final_qty = min(qty, kelly_limit)
    else:
        final_qty = 0

    sl = round(price - stop_loss_dist, 2)
    tp = round(price + (stop_loss_dist * 2), 2) # Ratio R/R de 2.0

    return final_qty, sl, tp

# --- BOUCLE DE CONTRÔLE ---
print(f"🚀 JULES V8.0 STARTING... [Mode: Quantitative Risk Management]")

# Verify connection
try:
    acct = alpaca.get_account()
    print(f"Connected: {acct.status} | Cash: ${acct.cash}")
except Exception as e:
    print(f"Connection Failed: {e}")
    exit(1)

while True:
    try:
        account = alpaca.get_account()
        cash = float(account.cash)
        dashboard_data = []

        for symbol in WATCHLIST:
            # Fix: Use helper to get DataFrame
            bars = get_bars_df(symbol, "15Min", limit=50)
            if bars.empty: continue

            rsi, ema, atr = get_quant_metrics(bars)
            price = bars['close'].iloc[-1]

            # Logique d'entrée V8.0
            # RSI < 30 (Oversold) AND Price > EMA (Trend)
            if rsi < 30 and price > ema:
                try:
                    # Check if position exists
                    pos = alpaca.get_position(symbol)
                    print(f"Position held for {symbol}. Skipping.")
                except:
                    # No position, calculate size
                    qty, sl, tp = compute_position_size(cash, price, atr)
                    if qty > 0:
                        print(f"🎯 SIGNAL DETECTÉ: {symbol} | Price: {price} | Qty: {qty} | SL: {sl} | TP: {tp}")
                        try:
                            alpaca.submit_order(
                                symbol=symbol, qty=qty, side='buy', type='market',
                                time_in_force='gtc', order_class='bracket',
                                take_profit={'limit_price': tp},
                                stop_loss={'stop_price': sl}
                            )
                            print(f"✅ Order Sent for {symbol}")
                        except Exception as order_err:
                            print(f"❌ Order Failed: {order_err}")

            dashboard_data.append({
                "symbol": symbol, "price": round(price, 2),
                "rsi": round(rsi, 2), "atr": round(atr, 2), "status": "SCANNING"
            })
            time.sleep(1) # API Rate limit protection

        # Sync Dashboard
        with open(WEB_PATH, 'w') as f:
            json.dump({"update": datetime.now().strftime("%H:%M"), "assets": dashboard_data}, f)

    except Exception as e:
        print(f"⚠️ Alerte Jules: {e}")

    # Wait before next scan loop
    time.sleep(60)
