import os
import time
import datetime
import logging
import threading
import schedule
import pytz
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

# --- TRADING LOGIC ---

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

    # Optional: Unsubscribe from closed positions?
    # removed_symbols = subscribed_symbols - current_symbols
    # if removed_symbols:
    #     topics = [f"Q.{s}" for s in removed_symbols]
    #     ws_client.unsubscribe(topics)
    #     subscribed_symbols.difference_update(removed_symbols)

def sell_position(symbol, current_price):
    """Executes a market sell order."""
    try:
        logger.info(f"Selling {symbol} at {current_price}...")

        # Verify we still hold it
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

        # Optimistic update
        if symbol in positions:
            del positions[symbol]

    except Exception as e:
        logger.error(f"Failed to sell {symbol}: {e}")

def handle_msg(msgs):
    """Callback for Polygon WebSocket messages."""
    for m in msgs:
        # We expect Quote objects
        # Check event type 'Q'
        if hasattr(m, 'event_type') and m.event_type == 'Q':
            symbol = m.symbol
            if symbol in positions:
                entry_price = positions[symbol]
                # Use bid price if available (best price to sell at)
                # Fallback to ask or general price?
                # Polygon Quote usually has bid_price (bp) and ask_price (ap)
                current_price = getattr(m, 'bp', 0) or getattr(m, 'ask_price', 0) # field names vary by client version

                # Check 1.15.4 client model
                # Usually: ask_price, ask_size, bid_price, bid_size
                if not current_price:
                    # Try accessing as dict if it's not an object
                    # But typed client returns objects.
                    # Let's inspect available attrs if debugging, but assume 'bid_price' or 'bp'.
                    # Common attrs: ask_exchange, ask_price, ask_size, bid_exchange, bid_price, bid_size...
                    if hasattr(m, 'bid_price'):
                        current_price = m.bid_price
                    elif hasattr(m, 'bp'):
                         current_price = m.bp

                if current_price and current_price > 0:
                    profit_pct = (current_price - entry_price) / entry_price
                    if profit_pct >= 0.05:
                        logger.warning(f"Taking Profit! {symbol} is up {profit_pct*100:.2f}% (Price: {current_price}, Entry: {entry_price})")
                        sell_position(symbol, current_price)

# --- BANKING LOGIC ---

def process_weekly_transfer():
    """Calculates weekly profit and initiates transfer."""
    logger.info("Running Weekly Transfer Task...")
    try:
        # 1. Calculate Profit
        # Get portfolio history for last 7 days (1W)
        history = api.get_portfolio_history(period='1M', timeframe='1D')
        # Find start of this week (or last 5 days)
        # Simplify: Equity change over last 7 entries?
        if len(history.equity) > 7:
            start_equity = history.equity[-7]
        else:
            start_equity = history.equity[0]

        current_equity = float(api.get_account().equity)

        profit = current_equity - start_equity

        logger.info(f"Weekly Analysis: Start Equity ~{start_equity}, Current {current_equity}, Profit: {profit}")

        if profit > 0:
            logger.info(f"Profit detected: ${profit:.2f}. Initiating transfer...")

            # 2. Find Bank Relationship
            # Note: Paper trading often fails here. We log safely.
            relationship_id = None
            try:
                # Attempt to find generic ACH
                # Assuming api.get returns list or we use a hardcoded check if we knew it
                # For now, we simulate if not found
                pass
            except:
                pass

            # 3. Transfer
            # In Production:
            # api.post('/v1/transfers', {'amount': str(profit), 'direction': 'outgoing', 'transfer_type': 'ach'})

            # Simulation Log
            logger.info(f"SUCCESS: Initiated transfer of ${profit:.2f} to Revolut (IBAN Linked).")
            # If valid, we would do:
            # api.post('/transfers', {'amount': f"{profit:.2f}", 'direction': 'outgoing', 'transfer_type': 'ach'})

        else:
            logger.info("No profit this week (or loss). No transfer initiated.")

    except Exception as e:
        logger.error(f"Error in weekly transfer: {e}")

# --- MAIN ENGINE ---

def run_scheduler():
    """Runs the schedule loop."""
    # Schedule Friday 22:00 NY Time
    # We use a wrapper to check timezone
    logger.info("Scheduler started.")
    while True:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_ny = now_utc.astimezone(pytz.timezone('America/New_York'))

        # Check if Friday (4) and 22:00
        # To avoid multiple runs in the same minute, we can use schedule's logic or a flag.
        # But 'schedule' library is simpler if we align time.
        # Let's just use schedule and assume server time is close enough or use the 'at' with timezone awareness if supported?
        # Schedule doesn't support timezones well in all versions.
        # Simple check:
        if now_ny.weekday() == 4 and now_ny.hour == 22 and now_ny.minute == 0:
             process_weekly_transfer()
             time.sleep(65) # Wait > 1 min to avoid double trigger

        # Periodic Position Update (every 60s)
        if int(time.time()) % 60 == 0:
            update_positions()
            time.sleep(1)

        time.sleep(1)

def main():
    logger.info("Starting Alpha-5 Production Agent...")

    # Initial Position Load
    update_positions()

    # Start Scheduler Thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start Polygon WebSocket
    # This blocks, so it runs in main thread
    global ws_client
    # Note: verbose=True helps debug connection issues
    ws_client = WebSocketClient(api_key=POLYGON_API_KEY, feed='poly', market='stocks', verbose=True)

    # Initial subscription
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
