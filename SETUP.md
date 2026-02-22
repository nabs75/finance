# Setup Instructions

To run the Alpha-5 bot, you must create a `.env` file in the root directory with your API keys.

1. Create a file named `.env`.
2. Add the following content (replace the placeholders with your actual keys):

```env
ALPACA_API_KEY=<YOUR_ALPACA_API_KEY>
ALPACA_SECRET_KEY=<YOUR_ALPACA_SECRET_KEY>
ALPACA_BASE_URL=<YOUR_ALPACA_BASE_URL> # e.g. https://paper-api.alpaca.markets
POLYGON_API_KEY=<YOUR_POLYGON_API_KEY>
```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the bot:

   To run in the foreground (terminal stays open):
   ```bash
   ./start_bot.sh
   ```

   To run as a **daemon** (keeps running after closing terminal):
   ```bash
   nohup ./start_bot.sh > bot.log 2>&1 &
   ```

# Environment Configuration

This bot is designed to run in a secure environment.

**Secrets:**
- `ALPACA_API_KEY`: Your Alpaca API Key ID.
- `ALPACA_SECRET_KEY`: Your Alpaca Secret Key.
- `ALPACA_BASE_URL`: The API base URL (Paper or Live).
- `POLYGON_API_KEY`: Your Polygon.io API Key (usually included with Alpaca).

**Note:** Never commit your `.env` file to version control.
