import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

try:
    pos = api.get_position('AAPL')
    entry_price = float(pos.avg_entry_price)
    target_price = entry_price * 1.05

    print(f"AAPL Position Found:")
    print(f"- Entry Price: ${entry_price:.2f}")
    print(f"- Target Price (+5%): ${target_price:.2f}")
    print(f"- Current Price: ${float(pos.current_price):.2f}")

    # Calculate 1% alert threshold
    upper_threshold = entry_price * 1.01
    lower_threshold = entry_price * 0.99
    print(f"- Alert Thresholds (1%): > ${upper_threshold:.2f} or < ${lower_threshold:.2f}")

except Exception as e:
    print(f"Error fetching AAPL position: {e}")
