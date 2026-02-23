import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

try:
    api = tradeapi.REST(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), os.getenv('ALPACA_BASE_URL'))
    account = api.get_account()
    print(f"Verified Alpaca Connection. Status: {account.status}")
except Exception as e:
    print(f"Verification Failed: {e}")
