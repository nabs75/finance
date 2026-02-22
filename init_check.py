import os
import time
import logging
import threading
import alpaca_trade_api as tradeapi
from polygon import WebSocketClient
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("InitCheck")

load_dotenv()
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def check_polygon():
    logger.info("Checking Polygon Stream...")
    ws = WebSocketClient(api_key=POLYGON_API_KEY, feed='poly', market='stocks', verbose=False)
    ws.subscribe("Q.NVDA")

    received_event = threading.Event()

    def handle(msgs):
        logger.info(f"Received Polygon Message sample: {msgs[0]}")
        received_event.set()
        # We can't easily close strictly from here if run() catches it?
        # But we can try relying on thread join or exception.
        raise Exception("StopStream")

    t = threading.Thread(target=ws.run, args=(handle,), daemon=True)
    t.start()

    # Wait for up to 15 seconds
    if received_event.wait(timeout=15):
        logger.info("✅ Polygon Stream Verified.")
    else:
        logger.warning("⚠️ Timeout waiting for Polygon message. Market might be closed or stream issues.")

def buy_fractional():
    logger.info("Buying $1 of NVDA...")
    try:
        # Check current status
        clock = api.get_clock()
        logger.info(f"Market Open: {clock.is_open}")

        order = api.submit_order(
            symbol='NVDA',
            notional=1, # $1 value
            side='buy',
            type='market',
            time_in_force='day'
        )
        logger.info(f"✅ Order submitted: {order.id} Status: {order.status}")

        time.sleep(2)
        orders = api.list_orders(status='all', limit=1)
        if orders and orders[0].id == order.id:
             logger.info(f"Order Check: {orders[0].symbol} {orders[0].side} Status: {orders[0].status}")

    except Exception as e:
        logger.error(f"❌ Buy failed: {e}")

if __name__ == "__main__":
    check_polygon()
    buy_fractional()
