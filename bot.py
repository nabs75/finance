import os
import time
import logging
import threading
import schedule
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from polygon import WebSocketClient

# --- CONFIGURATION (V7.2.5) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='bot.log', filemode='w')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger("Jules-V7.2.5")

load_dotenv()
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Check keys
if not all([ALPACA_API_KEY, ALPACA_SECRET_KEY, POLYGON_API_KEY]):
    logger.error("Missing API Keys in .env")
    exit(1)

# Initialize APIs
try:
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    account = api.get_account()
    logger.info(f"Connected to Alpaca: {account.status} (ID: {account.id})")
except Exception as e:
    logger.error(f"Failed to connect to Alpaca: {e}")
    exit(1)

# Global State
positions = {} # {symbol: avg_entry_price}
target_asset = "TSLA"
EMA_PERIOD = 20 # Can be adjusted
RSI_PERIOD = 14

# --- MARKET DATA & INDICATORS ---

def get_market_data(api, symbol):
    """
    Fetches market data (15m bars) for indicator calculation.
    """
    try:
        # Fetch 15m Bars (need enough for RSI 14 + EMA 20)
        # Using string '15Min' which is compatible
        bars_15m_raw = api.get_bars(symbol, '15Min', limit=100)
        bars_15m = pd.DataFrame([b._raw for b in bars_15m_raw])
        if not bars_15m.empty:
             bars_15m['timestamp'] = pd.to_datetime(bars_15m['t'])
             bars_15m.set_index('timestamp', inplace=True)
             bars_15m.rename(columns={'c': 'close', 'v': 'volume', 'o': 'open', 'h': 'high', 'l': 'low'}, inplace=True)
             return bars_15m
        else:
             return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    """Calculates RSI (Wilder 14) and EMA."""
    if df.empty or len(df) < RSI_PERIOD + 1: return df

    close = df['close'].values

    # RSI Wilder 14
    # Trying TA-Lib first
    try:
        import talib
        df['RSI'] = talib.RSI(close, timeperiod=RSI_PERIOD)
        df['EMA'] = talib.EMA(close, timeperiod=EMA_PERIOD)
    except ImportError:
        # Manual Calculation (Pandas)
        delta = df['close'].diff()

        # Wilder's Smoothing for RSI
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EMA for RSI (Wilder uses EMA-like smoothing, alpha=1/14)
        roll_up = up.ewm(com=RSI_PERIOD - 1, adjust=False).mean()
        roll_down = down.abs().ewm(com=RSI_PERIOD - 1, adjust=False).mean()

        RS = roll_up / roll_down
        df['RSI'] = 100.0 - (100.0 / (1.0 + RS))

        # Simple EMA for Price
        df['EMA'] = df['close'].ewm(span=EMA_PERIOD, adjust=False).mean()

    return df

# --- TRADING LOGIC (V7.2.5 RSI + EMA + TSLA) ---

def scan_and_trade():
    """Scans TSLA and attempts to trade based on RSI/EMA."""
    logger.info(f"Scanning {target_asset} (V7.2.5 Strategy)...")
    global positions
    update_positions()

    symbol = target_asset

    # Don't buy if already held
    if symbol in positions:
        logger.info(f"Already holding {symbol}. Skipping buy scan.")
        return

    df_15m = get_market_data(api, symbol)
    if df_15m.empty: return

    df_15m = calculate_indicators(df_15m)
    last_rsi = df_15m['RSI'].iloc[-1]
    last_ema = df_15m['EMA'].iloc[-1]
    last_close = df_15m['close'].iloc[-1]

    logger.info(f"{symbol} Analysis: RSI={last_rsi:.2f}, EMA={last_ema:.2f}, Close={last_close:.2f}")

    # Strategy: Buy if RSI < 30 (Oversold) AND Price > EMA (Trend Support? Or maybe Mean Reversion?)
    # "RSI Wilder 14 + EMA + TSLA" implies using them together.
    # Common Mean Reversion: RSI < 30 (Buy).
    # Common Trend Following: Price > EMA (Buy).
    # Let's combine: Buy if RSI < 40 (Dip in Trend) AND Price > EMA (Up Trend)
    # Or strict RSI < 30.
    # User said "RSI Wilder 14 + EMA". I will use:
    # BUY: RSI < 30 (Oversold condition)
    # FILTER: Price > EMA (Trend is up, buying the dip)

    # V7.2.5 Strategy:
    # Buy when RSI dips below 30 and price is above EMA (Pullback in uptrend)
    buy_signal = (last_rsi < 30) and (last_close > last_ema)

    if buy_signal:
        logger.info(f"✅ {symbol} BUY SIGNAL (RSI < 30 & Price > EMA). Placing Bracket Order.")

        # Native V7.2.5 Quantity: 1 Share (Standard)
        qty = 1

        try:
            # Native V7.2.5 Bracket Management
            # TP: +5%, SL: -3%
            take_profit_price = round(last_close * 1.05, 2)
            stop_loss_price = round(last_close * 0.97, 2)

            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market', # V7.2.5 used Market execution for speed
                time_in_force='gtc',
                order_class='bracket',
                take_profit={'limit_price': take_profit_price},
                stop_loss={'stop_price': stop_loss_price}
            )
            logger.info(f"Bracket Order Submitted: {order.id} | TP: {take_profit_price} | SL: {stop_loss_price}")
        except Exception as e:
            logger.error(f"Failed to submit bracket order for {symbol}: {e}")
    else:
        logger.info(f"No signal for {symbol}.")

def update_positions():
    """Fetches open positions from Alpaca."""
    global positions
    try:
        pos_list = api.list_positions()
        new_positions = {}
        for p in pos_list:
            new_positions[p.symbol] = float(p.avg_entry_price)
        positions = new_positions
    except Exception as e:
        logger.error(f"Error updating positions: {e}")

# --- MAIN ENGINE ---

def run_scheduler():
    logger.info("Scheduler started.")
    # Frequent scan for RSI strategy
    schedule.every(5).minutes.do(scan_and_trade)
    schedule.every(1).minutes.do(update_positions)

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    logger.info("Starting Jules V7.2.5 (RSI+EMA TSLA)...")
    update_positions()

    # Run scan immediately on startup
    scan_and_trade()

    threading.Thread(target=run_scheduler, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
