import json
import os
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
REPO_PATH = "." # Current directory in sandbox (adjust to /root/jules_bot/ on VPS)
STATUS_FILE = "status.json"
HTML_FILE = "index.html"
TARGET_WATCHLIST = ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMD', 'META', 'GOOGL']

def generate_html(data):
    """Generates the static index.html forcing 7 rows."""

    last_update = data.get("update", datetime.now().strftime("%H:%M"))
    assets_list = data.get("assets", [])

    # Convert list to dict for easy lookup
    assets_map = {a['symbol']: a for a in assets_list}

    rows_html = ""
    for symbol in TARGET_WATCHLIST:
        asset = assets_map.get(symbol, {})

        # Data Extraction with "En attente" fallback
        price = asset.get("price", "En attente")
        if isinstance(price, (int, float)): price = f"{price} $"

        rsi = asset.get("rsi", "-")
        atr = asset.get("atr", "-")
        status = asset.get("status", "OFFLINE")

        # Styling
        rsi_val = float(rsi) if isinstance(rsi, (int, float)) else 100
        rsi_class = "text-red-500 font-bold" if rsi_val < 30 else "text-green-400"
        badge_class = "bg-red-900" if rsi_val < 30 else "bg-blue-900"
        status_text = "SIGNAL" if rsi_val < 30 else (status if status != "OFFLINE" else "WAITING")

        rows_html += f"""
        <tr>
            <td class="px-4 py-2 border-b border-gray-700">{symbol}</td>
            <td class="px-4 py-2 border-b border-gray-700">{price}</td>
            <td class="px-4 py-2 border-b border-gray-700 {rsi_class}">{rsi}</td>
            <td class="px-4 py-2 border-b border-gray-700">{atr}</td>
            <td class="px-4 py-2 border-b border-gray-700">
                <span class="px-2 py-1 rounded text-xs {badge_class}">
                    {status_text}
                </span>
            </td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jules Trading Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0f172a; color: white; font-family: sans-serif; }}
    </style>
</head>
<body class="p-6">
    <div class="max-w-4xl mx-auto">
        <header class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-blue-400">🚀 Alpha-5 Trading Bot</h1>
            <div class="text-gray-400 text-sm">
                Last Update: <span class="font-mono text-white">{last_update}</span>
            </div>
        </header>

        <div class="overflow-x-auto bg-gray-900 rounded-lg shadow-xl">
            <table class="min-w-full bg-gray-800 text-white">
                <thead>
                    <tr class="bg-gray-700">
                        <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Valeur</th>
                        <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Prix</th>
                        <th class="text-left py-3 px-4 uppercase font-semibold text-sm">RSI</th>
                        <th class="text-left py-3 px-4 uppercase font-semibold text-sm">ATR (Vol)</th>
                        <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Statut</th>
                    </tr>
                </thead>
                <tbody id="trading-body">
                    {rows_html}
                </tbody>
            </table>
        </div>

        <footer class="mt-8 text-center text-gray-500 text-xs">
            Powered by Jules V8.1 • Force Web 7
        </footer>
    </div>
</body>
</html>"""
    return html_content

def main():
    try:
        # 1. Read Data
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {"update": "Wait...", "assets": []}

        # 2. Generate HTML
        html = generate_html(data)
        with open(HTML_FILE, 'w') as f:
            f.write(html)
        print(f"✅ Generated {HTML_FILE} with strict 7-asset layout.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
