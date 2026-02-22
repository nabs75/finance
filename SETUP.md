# Setup Instructions

To run the Alpha-5 bot, you must create a `.env` file in the root directory with your API keys.

1. Create a file named `.env`.
2. Add the following content:

```env
ALPACA_API_KEY=PK7PTVUJEBA5AWR65XTNOITDZL
ALPACA_SECRET_KEY=G6MaT3u16TPK258xx22PJCt3yvMRtP5V5CN63NDsapAY
ALPACA_BASE_URL=https://paper-api.alpaca.markets
POLYGON_API_KEY=UDcT_hdW0JPrUz9Rx0N2TktVc5JD1KVO
```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the bot:
   ```bash
   ./start_bot.sh
   ```
