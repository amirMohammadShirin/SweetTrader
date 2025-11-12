# SweetTrader Signal Bot 🤖📈

A Telegram bot that automatically sends reliable trading signals for MetaTrader5.

## Features ✨

- 🔔 **Automatic Signals**: Automatically sends trading signals when strong opportunities are detected
- 📊 **Technical Analysis**: Uses RSI, MACD, Moving Averages, and Bollinger Bands
- 🎯 **High Confidence**: Only sends signals with 70%+ confidence
- 🔐 **Secure Access**: Restricted to authorized users only
- 🔗 **MT5 Integration**: Real-time market data from MetaTrader5
- 📱 **Multiple Symbols**: Monitors EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD

## Requirements 📋

- Python 3.8 or higher
- MetaTrader5 account (for market data)
- Telegram Bot Token

## Installation 🚀

### 1. Clone the repository

```bash
cd SweetTrader
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the bot

Create a `.env` file:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# MetaTrader5 Configuration (for market data)
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo

# Authorization (comma-separated)
ALLOWED_USERNAMES=reyi_t,sweetamirmohamad
```

### 5. Run the bot

```bash
python bot.py
```

## Usage 💡

### Start the Bot

1. Open Telegram and find your bot
2. Send `/start` command
3. The bot will automatically start monitoring markets
4. You will receive signals automatically when strong trading opportunities are detected

### Signal Format

When a signal is detected, you'll receive a message like:

```
🟢 TRADING SIGNAL 🟢

📊 Symbol: EURUSD
🎯 Action: BUY
💰 Price: 1.08500
📈 Confidence: 85%

🛑 Stop Loss: 1.06330
🎯 Take Profit: 1.10670

📋 Reasons:
• RSI oversold (<30)
• MACD bullish crossover
• Price above SMA 20

⚠️ Always use proper risk management!
```

## How It Works 🔧

1. **Monitoring**: Bot checks major currency pairs every 5 minutes
2. **Analysis**: Calculates technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
3. **Signal Generation**: Generates signals based on multiple indicator confirmations
4. **Filtering**: Only sends signals with 70%+ confidence
5. **Delivery**: Automatically sends signals to all registered users

## Signal Criteria 📊

Signals are generated when:
- Multiple technical indicators align
- Confidence level is 70% or higher
- Strong buy/sell signals detected (3+ confirmations)

## Security 🔒

- Only authorized users can use the bot
- Credentials stored securely in `.env` file
- No trading execution - signals only

## Disclaimer ⚠️

**This bot provides trading signals only. It does NOT execute trades.**

- Trading involves risk
- Always use proper risk management
- Use stop losses on all trades
- Never risk more than you can afford to lose
- Past performance doesn't guarantee future results
- Test signals on demo accounts first

## Support 💬

For issues or questions, please open an issue on the repository.

---

**Happy Trading! 📈💰**
