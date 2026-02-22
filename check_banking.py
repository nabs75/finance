import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL')
)

try:
    print("Checking Account...")
    account = api.get_account()
    print(f"Account ID: {account.id}")
    print(f"Status: {account.status}")

    print("\nChecking ACH Relationships (v2 client)...")
    try:
        achs = api.get('/ach_relationships')
        print("ACH Relationships found:", achs)
    except Exception as e:
        print(f"Error fetching ACH (v2): {e}")

    print("\nChecking ACH Relationships (v1 client)...")
    try:
        api_v1 = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            os.getenv('ALPACA_BASE_URL'),
            api_version='v1'
        )
        achs = api_v1.get('/ach_relationships')
        print("ACH Relationships found (v1):", achs)
    except Exception as e:
        print(f"Error fetching ACH (v1): {e}")

    print("\nChecking Transfers (Bank)...")
    try:
        transfers = api.get('/v1/transfers') # or /v1/accounts/{id}/transfers
        print("Transfers found:", transfers)
    except Exception as e:
        print(f"Error fetching Transfers: {e}")

except Exception as e:
    print(f"Fatal Error: {e}")
