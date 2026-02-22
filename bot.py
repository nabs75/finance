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

# Initialize Alpaca API
try:
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    account = api.get_account()
    logger.info(f"Connected to Alpaca: {account.status} (ID: {account.id})")
except Exception as e:
    logger.error(f"Failed to connect to Alpaca: {e}")
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
        # Fetch Daily Bars (need at least 50 for SMA50)
        # Using string '1Day' which is compatible
        daily_bars_raw = api.get_bars(symbol, '1Day', limit=100)
        daily_bars = pd.DataFrame([b._raw for b in daily_bars_raw])
        if not daily_bars.empty:
             daily_bars['timestamp'] = pd.to_datetime(daily_bars['t'])
             daily_bars.set_index('timestamp', inplace=True)
             # Rename columns to match filter expectations (lowercase) if needed
             # Alpaca v2 raw keys are 'c', 'v', 'o', 'h', 'l'.
             daily_bars.rename(columns={'c': 'close', 'v': 'volume', 'o': 'open', 'h': 'high', 'l': 'low'}, inplace=True)

        # Fetch 15m Bars (need at least 21 for volume avg)
        # Using string '15Min' which is compatible
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

class SecurityFilters:
    """
    Bouclier Anti-Pièges (Security Filters)
    """
    def __init__(self, api):
        self.api = api

    def is_safe_asset(self, symbol, df_daily):
        """
        Rejette les Penny Stocks et les Pump & Dump.
        Condition: Prix > 5$ ET Volume quotidien > 1 000 000.
        """
        if df_daily.empty:
            return False

        last_close = df_daily['close'].iloc[-1]
        last_volume = df_daily['volume'].iloc[-1] # or average volume? Prompt says "Volume quotidien" -> usually avg daily volume is safer, but "Volume quotidien" implies current/last daily volume.
        # Let's use average daily volume over last 20 days for safety, or just last day as requested?
        # "Volume quotidien > 1 000 000" usually implies "Average Daily Volume".
        avg_volume = df_daily['volume'].tail(20).mean()

        if last_close > 5 and avg_volume > 1_000_000:
            return True

        logger.warning(f"Filter Fail (Safe Asset): {symbol} (Price: {last_close}, Vol: {avg_volume})")
        return False

    def confirm_volume_breakout(self, df_15m):
        """
        Évite les fausses cassures.
        Condition: Le volume de la dernière bougie 15m doit être strictement supérieur à 1.5 fois la moyenne des volumes des 20 dernières bougies 15m.
        """
        if df_15m.empty or len(df_15m) < 21:
            return False

        last_volume = df_15m['volume'].iloc[-1]
        # Average of previous 20 bars (excluding the last one which is current)
        avg_volume_20 = df_15m['volume'].iloc[-21:-1].mean()

        if last_volume > 1.5 * avg_volume_20:
            return True

        logger.warning(f"Filter Fail (Volume Breakout): Last Vol {last_volume} <= 1.5 * Avg {avg_volume_20}")
        return False

    def is_global_trend_bullish(self, df_daily):
        """
        Ne trade pas contre la tendance.
        Condition: Le prix actuel doit être au-dessus de la Moyenne Mobile 50 jours (SMA 50) sur le graphique Daily.
        """
        if df_daily.empty or len(df_daily) < 50:
            return False

        df_daily['SMA50'] = df_daily['close'].rolling(window=50).mean()
        last_close = df_daily['close'].iloc[-1]
        last_sma50 = df_daily['SMA50'].iloc[-1]

        if last_close > last_sma50:
            return True

        logger.warning(f"Filter Fail (Trend): Price {last_close} <= SMA50 {last_sma50}")
        return False

# --- TRADING LOGIC (Buying & Selling) ---

security_filters = SecurityFilters(api)

def scan_and_trade():
    """Scans watchlist and attempts to buy if filters pass."""
    logger.info("Scanning watchlist for opportunities...")
    global positions

    # Refresh positions first
    update_positions()

    for symbol in watchlist:
        # Don't buy if already held
        if symbol in positions:
            continue

        logger.info(f"Analyzing {symbol}...")
        df_15m, df_daily = get_market_data(api, symbol)

        if df_15m.empty or df_daily.empty:
            continue

        # Check Filters
        if not security_filters.is_safe_asset(symbol, df_daily):
            continue

        if not security_filters.is_global_trend_bullish(df_daily):
            continue

        if not security_filters.confirm_volume_breakout(df_15m):
            continue

        # If all pass, BUY!
        logger.info(f"✅ {symbol} PASSED ALL FILTERS! Placing BUY Order.")
        try:
            order = api.submit_order(
                symbol=symbol,
                qty=1, # Start small or calculate based on risk
                side='buy',
                type='market',
                time_in_force='day'
            )
            logger.info(f"Order Submitted: {order.id}")
        except Exception as e:
            logger.error(f"Failed to submit buy order for {symbol}: {e}")

def update_positions():
    """Fetches open positions from Alpaca and updates the global list."""
    global positions
    try:
        pos_list = api.list_positions()
        new_positions = {}
        for p in pos_list:
            new_positions[p.symbol] = float(p.avg_entry_price)

        positions = new_positions
        logger.info(f"Positions updated: {len(positions)} held. Symbols: {list(positions.keys())}")

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

def sell_position(symbol, current_price):
    """Executes a market sell order."""
    try:
        logger.info(f"Selling {symbol} at {current_price}...")

        pos = api.get_position(symbol)
        qty = pos.qty

        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        logger.info(f"Order submitted: {order.id} for {qty} shares of {symbol}")

        if symbol in positions:
            del positions[symbol]

    except Exception as e:
        logger.error(f"Failed to sell {symbol}: {e}")

def handle_msg(msgs):
    """Callback for Polygon WebSocket messages."""
    for m in msgs:
        if hasattr(m, 'event_type') and m.event_type == 'Q':
            symbol = m.symbol
            if symbol in positions:
                entry_price = positions[symbol]
                current_price = getattr(m, 'bp', 0) or getattr(m, 'ask_price', 0)

                # Check 1.15.4 client model
                if not current_price:
                    if hasattr(m, 'bid_price'):
                        current_price = m.bid_price
                    elif hasattr(m, 'bp'):
                         current_price = m.bp

                if current_price and current_price > 0:
                    profit_pct = (current_price - entry_price) / entry_price

                    # --- INTENSIVE SURVEILLANCE: AAPL ---
                    if symbol == 'AAPL' and abs(profit_pct) >= 0.01:
                         logger.warning(f"⚠️ INTENSIVE WATCH: AAPL variation > 1%! Current: {profit_pct*100:.2f}% (Price: {current_price})")

                    if profit_pct >= 0.05:
                        logger.warning(f"Taking Profit! {symbol} is up {profit_pct*100:.2f}% (Price: {current_price}, Entry: {entry_price})")
                        sell_position(symbol, current_price)

# --- BANKING LOGIC ---

def process_weekly_transfer():
    """Calculates weekly profit and initiates transfer."""
    logger.info("Running Weekly Transfer Task...")
    try:
        history = api.get_portfolio_history(period='1M', timeframe='1D')

        if len(history.equity) > 7:
            start_equity = history.equity[-7]
        else:
            start_equity = history.equity[0] if history.equity else 0

        account_info = api.get_account()
        current_equity = float(account_info.equity)

        profit = current_equity - start_equity

        logger.info(f"Weekly Analysis: Start Equity ~{start_equity}, Current {current_equity}, Profit: {profit}")

        if profit > 0:
            logger.info(f"Profit detected: ${profit:.2f}. Initiating transfer...")

            try:
                transfer_data = {
                    'transfer_type': 'ach',
                    'amount': str(round(profit, 2)),
                    'direction': 'outgoing'
                }

                try:
                    rels = api.get('/ach_relationships')
                    if rels:
                        transfer_data['relationship_id'] = rels[0]['id']
                        logger.info(f"Using Bank Relationship ID: {transfer_data['relationship_id']}")
                except Exception as e:
                    logger.warning(f"Could not fetch ACH relationships: {e}")

                response = api.post('/transfers', data=transfer_data)
                logger.info(f"SUCCESS: Transfer Response: {response}")

            except Exception as e:
                logger.error(f"Transfer failed (Expected in Paper Trading): {e}")
                logger.info(f"[SIMULATION] Would have transferred ${profit:.2f} to linked Revolut account.")

        else:
            logger.info("No profit this week (or loss). No transfer initiated.")

    except Exception as e:
        logger.error(f"Error in weekly transfer: {e}")

# --- MAIN ENGINE ---

def run_scheduler():
    """Runs the schedule loop."""
    logger.info("Scheduler started.")

    # Schedule Weekly Transfer (Friday 22:00)
    schedule.every().friday.at("22:00").do(process_weekly_transfer)

    # Schedule Position Updates (Every 1 minute)
    schedule.every(1).minutes.do(update_positions)

    # Schedule Market Scanner (Every 15 minutes to match bar time?)
    # Or more frequently? The filter relies on 15m bars.
    schedule.every(15).minutes.do(scan_and_trade)

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    logger.info("Starting Alpha-5 Production Agent...")

    # Initial Position Load
    update_positions()

    # Initial Scan (Optional)
    # scan_and_trade()

    # Start Scheduler Thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start Polygon WebSocket
    global ws_client
    # Using polygon-api-client structure
    ws_client = WebSocketClient(api_key=POLYGON_API_KEY, verbose=True)

    current_symbols = list(positions.keys())
    if current_symbols:
        topics = [f"Q.{s}" for s in current_symbols]
        ws_client.subscribe(topics)
        subscribed_symbols.update(current_symbols)
        logger.info(f"Subscribed to: {topics}")
    else:
        logger.info("No positions to monitor initially.")

    logger.info("Connecting to Polygon Stream...")
    try:
        ws_client.run(handle_msg)
    except Exception as e:
        logger.error(f"WebSocket crashed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
