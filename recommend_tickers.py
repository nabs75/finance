import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

def recommend():
    print("Analyzing Market Conditions...")
    # Simulation of market analysis based on sector rotation and volatility
    # In a real scenario, this would query Polygon aggregates for top gainers/losers

    recommendations = [
        {"symbol": "TSLA", "reason": "High Beta, strong momentum in EV sector."},
        {"symbol": "AMD", "reason": "Semiconductor volatility, competitor to NVDA."},
        {"symbol": "META", "reason": "AI-driven growth, recovering from recent dips."}
    ]

    print("\nRecommended Watchlist for Tomorrow:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['symbol']} - {rec['reason']}")

if __name__ == "__main__":
    recommend()
