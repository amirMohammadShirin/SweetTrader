# SweetTrader Telegram Bot 🤖📈

A professional Telegram bot for forex trading with MetaTrader5 integration and N8N AI support.

## Features ✨

- 🔗 **MetaTrader5 Integration**: Direct connection to MetaTrader5 account
- 🤖 **AI Analysis**: Intelligent market analysis using OpenAI and N8N
- 📊 **Technical Indicators**: Calculate technical indicators (RSI, MACD, Bollinger Bands, SMA)
- 💹 **Trading Commands**: Complete commands for buying, selling, and managing positions
- 🌐 **English Interface**: User-friendly English interface
- 🔔 **Real-time Signals**: Get trading signals in real-time

## Requirements 📋

- Python 3.8 or higher
- MetaTrader5 account and credentials
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- (Optional) OpenAI API Key for AI analysis
- (Optional) N8N instance with webhook URL

## Installation 🚀

### 1. Clone or download this repository

```bash
cd SweetTrader
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install MetaTrader5 Terminal

Make sure MetaTrader5 is installed on your system. The Python library requires the MT5 terminal to be installed.

**Windows**: Download from [MetaQuotes](https://www.metatrader5.com/en/download)

**Linux/Mac**: You may need to use Wine or a Windows VM. Alternatively, you can use a VPS with Windows.

### 5. Configure the bot

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# MetaTrader5 Configuration
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo  # or YourBroker-Live

# N8N Configuration (Optional)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/trading-ai

# OpenAI Configuration (Optional)
OPENAI_API_KEY=sk-your-openai-api-key

# Bot Settings
ADMIN_USER_ID=123456789  # Your Telegram user ID
```

### 6. Get your Telegram Bot Token

The bot has been created: **[@SweetTraderBot](https://t.me/SweetTraderBot)**

1. Copy the bot token provided by BotFather
2. Paste it in your `.env` file as `TELEGRAM_BOT_TOKEN`
3. ⚠️ **Keep your token secure!** Never commit it to git

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

### 7. Get your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start a chat and it will show your user ID
3. Copy the ID and paste it in `.env` as `ADMIN_USER_ID`

## Usage 💻

### Start the bot

```bash
python bot.py
```

The bot will:
1. Connect to MetaTrader5
2. Start listening for Telegram commands
3. Be ready to process trading requests

### Available Commands 📝

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot | `/start` |
| `/help` | Show help guide | `/help` |
| `/account` | Full account information | `/account` |
| `/balance` | Account balance | `/balance` |
| `/positions` | Open positions | `/positions` |
| `/analyze <SYMBOL>` | Analyze symbol | `/analyze EURUSD` |
| `/signal <SYMBOL>` | Get trading signal | `/signal GBPUSD` |
| `/buy <SYMBOL> <VOLUME>` | Place buy order | `/buy EURUSD 0.01` |
| `/sell <SYMBOL> <VOLUME>` | Place sell order | `/sell EURUSD 0.01` |
| `/close <TICKET>` | Close position | `/close 123456` |

### Advanced Trading Commands

You can also specify Stop Loss and Take Profit:

```
/buy EURUSD 0.01 50 100
```

This means:
- Buy EURUSD
- Volume: 0.01 lots
- Stop Loss: 50 pips
- Take Profit: 100 pips

Same for sell:
```
/sell GBPUSD 0.02 30 60
```

## N8N Integration 🔗

To use N8N for AI analysis:

1. Set up an N8N workflow with a webhook trigger
2. Add AI processing nodes (OpenAI, custom logic, etc.)
3. Configure the webhook to return analysis in this format:

```json
{
  "analysis": "Your AI analysis text in English",
  "signal": {
    "action": "BUY",
    "confidence": 85,
    "reason": "Strong bullish indicators"
  }
}
```

4. Add the webhook URL to your `.env` file

## Project Structure 📁

```
SweetTrader/
├── bot.py              # Main bot file
├── config.py           # Configuration management
├── mt5_handler.py      # MetaTrader5 integration
├── n8n_handler.py      # N8N webhook integration
├── ai_analyzer.py      # AI analysis and indicators
├── utils.py            # Utility functions and bot text messages
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Technical Indicators 📊

The bot calculates the following indicators:

- **RSI (Relative Strength Index)**: Momentum oscillator
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility bands
- **SMA (Simple Moving Average)**: Trend indicator

## Security 🔒

- Never commit your `.env` file to version control
- Keep your MT5 credentials secure
- Use a demo account for testing
- The bot only responds to commands from authorized users

## Troubleshooting 🔧

### Bot not connecting to MT5

- Make sure MetaTrader5 terminal is installed and running
- Verify your login credentials in `.env`
- Check that your broker allows API access
- Ensure the server name matches exactly (case-sensitive)

### Commands not working

- Make sure you've started the bot with `/start`
- Check that the bot token is correct
- Verify your user ID is set as admin

### AI analysis not working

- OpenAI API key is optional but required for AI analysis
- N8N webhook is optional but provides additional AI features
- The bot will still work with basic technical analysis without AI

## Contributing 🤝

Feel free to submit issues and enhancement requests!

## License 📄

This project is open source and available for personal use.

## Disclaimer ⚠️

**Trading involves risk. This bot is a tool to assist with trading decisions, not a guarantee of profits. Always:**

- Test thoroughly on a demo account first
- Use proper risk management
- Never risk more than you can afford to lose
- Understand that past performance doesn't guarantee future results

## Support 💬

For issues or questions, please open an issue on the repository.

---

**Happy Trading! 📈💰**

