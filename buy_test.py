import os
import alpaca_trade_api as tradeapi

api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL')
)

try:
    print("Buying AAPL...")
    order = api.submit_order(
        symbol='AAPL',
        qty=1,
        side='buy',
        type='market',
        time_in_force='day'
    )
    print(f"Order submitted: {order.id} Status: {order.status}")
except Exception as e:
    print(f"Error: {e}")
