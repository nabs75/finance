import os
import time
import logging
import threading
import schedule
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, time as dtime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from polygon import WebSocketClient, RESTClient

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Alpha5-Bot")

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
    poly_rest = RESTClient(api_key=POLYGON_API_KEY)
    account = api.get_account()
    logger.info(f"Connected to Alpaca: {account.status} (ID: {account.id})")
except Exception as e:
    logger.error(f"Failed to connect to APIs: {e}")
    exit(1)

# Global State
positions = {} # {symbol: avg_entry_price}
subscribed_symbols = set()
watchlist = ["AAPL", "TSLA", "AMD", "NVDA", "META"] # Example Watchlist

# --- MARKET DATA & SECURITY FILTERS ---

def get_market_data(api, symbol):
    """
    Fetches market data (15m and Daily bars) for a given symbol.
    Returns two DataFrames: df_15m, df_daily.
    """
    try:
        # Fetch Daily Bars
        daily_bars_raw = api.get_bars(symbol, '1Day', limit=100)
        daily_bars = pd.DataFrame([b._raw for b in daily_bars_raw])
        if not daily_bars.empty:
             daily_bars['timestamp'] = pd.to_datetime(daily_bars['t'])
             daily_bars.set_index('timestamp', inplace=True)
             daily_bars.rename(columns={'c': 'close', 'v': 'volume', 'o': 'open', 'h': 'high', 'l': 'low'}, inplace=True)

        # Fetch 15m Bars
        bars_15m_raw = api.get_bars(symbol, '15Min', limit=50)
        bars_15m = pd.DataFrame([b._raw for b in bars_15m_raw])
        if not bars_15m.empty:
             bars_15m['timestamp'] = pd.to_datetime(bars_15m['t'])
             bars_15m.set_index('timestamp', inplace=True)
             bars_15m.rename(columns={'c': 'close', 'v': 'volume', 'o': 'open', 'h': 'high', 'l': 'low'}, inplace=True)

        return bars_15m, daily_bars

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(), pd.DataFrame()

def check_earnings(symbol):
    """
    Checks if the company has earnings announced for today.
    Uses Polygon Benzinga Earnings endpoint.
    """
    try:
        today = datetime.now().date().isoformat()
        # Note: This endpoint might require a paid Polygon tier.
        earnings = poly_rest.list_benzinga_earnings(date=today, ticker=symbol)

        # Check if iterator has any items
        for e in earnings:
            logger.warning(f"⚠️ EARNINGS ALERT: {symbol} has earnings today!")
            return True # Has earnings

        return False # No earnings found
    except Exception as e:
        logger.warning(f"Earnings check failed/skipped (API limit?): {e}")
        return False

def is_market_open_volatility():
    """
    Returns True if current NY time is between 09:30 and 10:00 (Kill Zone).
    """
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz).time()
    start_kill = dtime(9, 30)
    end_kill = dtime(10, 00)

    if start_kill <= now_ny <= end_kill:
        return True
    return False

class SecurityFilters:
    """
    Bouclier Anti-Pièges (Security Filters)
    """
    def __init__(self, api):
        self.api = api

    def is_safe_asset(self, symbol, df_daily):
        if df_daily.empty: return False
        last_close = df_daily['close'].iloc[-1]
        avg_volume = df_daily['volume'].tail(20).mean()
        if last_close > 5 and avg_volume > 1_000_000:
            return True
        logger.warning(f"Filter Fail (Safe Asset): {symbol}")
        return False

    def confirm_volume_breakout(self, df_15m):
        if df_15m.empty or len(df_15m) < 21: return False
        last_volume = df_15m['volume'].iloc[-1]
        avg_volume_20 = df_15m['volume'].iloc[-21:-1].mean()
        if last_volume > 1.5 * avg_volume_20:
            return True
        logger.warning(f"Filter Fail (Volume Breakout): {last_volume} vs {avg_volume_20}")
        return False

    def is_global_trend_bullish(self, df_daily):
        if df_daily.empty or len(df_daily) < 50: return False
        df_daily['SMA50'] = df_daily['close'].rolling(window=50).mean()
        last_close = df_daily['close'].iloc[-1]
        last_sma50 = df_daily['SMA50'].iloc[-1]
        if last_close > last_sma50:
            return True
        logger.warning(f"Filter Fail (Trend): Price <= SMA50")
        return False

# --- TRADING LOGIC (Buying & Selling) ---

security_filters = SecurityFilters(api)

def scan_and_trade():
    """Scans watchlist and attempts to buy if filters pass."""

    # 2. Filtre Temporel (Zone de la mort)
    if is_market_open_volatility():
        logger.warning("⛔ KILL ZONE (09:30-10:00 NY): No new positions.")
        return

    logger.info("Scanning watchlist for opportunities...")
    global positions
    update_positions()

    # 1. Money Management (20% Limit)
    try:
        account = api.get_account()
        cash_available = float(account.cash)
        max_trade_val = cash_available * 0.20
    except Exception as e:
        logger.error(f"Failed to get account info: {e}")
        return

    for symbol in watchlist:
        if symbol in positions: continue

        # 5. Filtre d'Earnings
        if check_earnings(symbol):
            logger.warning(f"Skipping {symbol} due to Earnings today.")
            continue

        df_15m, df_daily = get_market_data(api, symbol)
        if df_15m.empty or df_daily.empty: continue

        # Security Filters
        if not security_filters.is_safe_asset(symbol, df_daily): continue
        if not security_filters.is_global_trend_bullish(df_daily): continue
        if not security_filters.confirm_volume_breakout(df_15m): continue

        # ALL FILTERS PASSED -> PREPARE ORDER
        last_close_15m = float(df_15m['close'].iloc[-1])

        # Calc Quantity based on Money Management
        if last_close_15m <= 0: continue
        qty = int(max_trade_val / last_close_15m)
        if qty < 1:
            logger.warning(f"Insufficient funds for {symbol} (Max: ${max_trade_val:.2f}, Price: ${last_close_15m})")
            continue

        logger.info(f"✅ {symbol} BUY SIGNAL. Qty: {qty} @ Limit ${last_close_15m}")

        # 3. & 4. Limit Order with Bracket (TP/SL)
        try:
            take_profit_price = round(last_close_15m * 1.05, 2)
            stop_loss_price = round(last_close_15m * 0.97, 2)

            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                limit_price=last_close_15m,
                time_in_force='day',
                order_class='bracket',
                take_profit={'limit_price': take_profit_price},
                stop_loss={'stop_price': stop_loss_price}
            )
            logger.info(f"Bracket Order Submitted: {order.id} | TP: {take_profit_price} | SL: {stop_loss_price}")
        except Exception as e:
            logger.error(f"Failed to submit bracket order for {symbol}: {e}")

def update_positions():
    """Fetches open positions from Alpaca and updates the global list."""
    global positions
    try:
        pos_list = api.list_positions()
        new_positions = {}
        for p in pos_list:
            new_positions[p.symbol] = float(p.avg_entry_price)
        positions = new_positions
        # Update Subscriptions
        update_subscriptions()
    except Exception as e:
        logger.error(f"Error updating positions: {e}")

def update_subscriptions():
    """Subscribes to Polygon quotes for new positions."""
    global subscribed_symbols, ws_client
    current_symbols = set(positions.keys())
    new_symbols = current_symbols - subscribed_symbols
    if new_symbols:
        topics = [f"Q.{s}" for s in new_symbols]
        logger.info(f"Subscribing to: {topics}")
        try:
            ws_client.subscribe(topics)
            subscribed_symbols.update(new_symbols)
        except Exception as e:
            logger.error(f"Error subscribing: {e}")

def handle_msg(msgs):
    """Callback for Polygon WebSocket messages."""
    for m in msgs:
        if hasattr(m, 'event_type') and m.event_type == 'Q':
            symbol = m.symbol
            if symbol in positions:
                entry_price = positions[symbol]
                current_price = getattr(m, 'bp', 0) or getattr(m, 'ask_price', 0) or getattr(m, 'bid_price', 0)

                # Check 1.15.4 client model
                if not current_price:
                    if hasattr(m, 'bid_price'): current_price = m.bid_price
                    elif hasattr(m, 'bp'): current_price = m.bp

                if current_price and current_price > 0:
                    profit_pct = (current_price - entry_price) / entry_price

                    # --- INTENSIVE SURVEILLANCE: AAPL ---
                    if symbol == 'AAPL' and abs(profit_pct) >= 0.01:
                         logger.warning(f"⚠️ INTENSIVE WATCH: AAPL variation > 1%! Current: {profit_pct*100:.2f}%")

                    # Note: TP is handled by Bracket Order. We just log here or trigger backup sell.
                    if profit_pct >= 0.05:
                        logger.warning(f"Target Hit (+5%) for {symbol}. Bracket Order should trigger.")

# --- BANKING LOGIC ---

def process_weekly_transfer():
    """Calculates weekly profit and initiates transfer."""
    logger.info("Running Weekly Transfer Task...")
    try:
        history = api.get_portfolio_history(period='1M', timeframe='1D')
        start_equity = history.equity[-7] if len(history.equity) > 7 else (history.equity[0] if history.equity else 0)
        current_equity = float(api.get_account().equity)
        profit = current_equity - start_equity

        if profit > 0:
            logger.info(f"Profit detected: ${profit:.2f}. Initiating transfer...")
            try:
                transfer_data = {'transfer_type': 'ach', 'amount': str(round(profit, 2)), 'direction': 'outgoing'}
                rels = api.get('/ach_relationships')
                if rels: transfer_data['relationship_id'] = rels[0]['id']
                api.post('/transfers', data=transfer_data)
                logger.info("SUCCESS: Transfer Initiated.")
            except Exception as e:
                logger.error(f"Transfer failed: {e}")
    except Exception as e:
        logger.error(f"Error in weekly transfer: {e}")

# --- MAIN ENGINE ---

def run_scheduler():
    logger.info("Scheduler started.")
    schedule.every().friday.at("22:00").do(process_weekly_transfer)
    schedule.every(1).minutes.do(update_positions)
    schedule.every(15).minutes.do(scan_and_trade)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    logger.info("Starting Alpha-5 Production Agent...")
    update_positions()

    threading.Thread(target=run_scheduler, daemon=True).start()

    global ws_client
    ws_client = WebSocketClient(api_key=POLYGON_API_KEY, verbose=True)

    current_symbols = list(positions.keys())
    if current_symbols:
        topics = [f"Q.{s}" for s in current_symbols]
        ws_client.subscribe(topics)
        subscribed_symbols.update(current_symbols)

    logger.info("Connecting to Polygon Stream...")
    try:
        ws_client.run(handle_msg)
    except Exception as e:
        logger.error(f"WebSocket crashed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
