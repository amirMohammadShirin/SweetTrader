# SweetTrader Advisor Bot 🤖📈

A Telegram bot that provides reliable trading advice for MetaTrader5, including technical analysis, trading planning, and financial management advice.

## Features ✨

- 📊 **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands
- 📋 **Trading Planning**: Risk management, position sizing, margin advice
- 💵 **Financial Advice**: Capital management, trading psychology
- 🤖 **AI-Powered Insights**: OpenAI integration for comprehensive advice
- 🔐 **Secure Access**: Restricted to authorized users only
- 🔗 **MT5 Integration**: Real-time market data from MetaTrader5

## Requirements 📋

- Python 3.8 or higher
- MetaTrader5 account (for market data)
- Telegram Bot Token
- (Optional) OpenAI API Key for AI advice

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

# OpenAI Configuration (Optional)
OPENAI_API_KEY=sk-your-openai-api-key

# Authorization
ALLOWED_USERNAME=reyi_t
```

### 5. Run the bot

```bash
python bot.py
```

## Available Commands 📝

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot | `/start` |
| `/help` | Show help guide | `/help` |
| `/account` | Account information | `/account` |
| `/advice <SYMBOL>` | Comprehensive trading advice | `/advice EURUSD` |
| `/technical <SYMBOL>` | Technical analysis only | `/technical GBPUSD` |
| `/planning` | Trading plan advice | `/planning` |
| `/financial` | Financial management advice | `/financial` |

## Usage Examples 💡

### Get Comprehensive Advice

```
/advice EURUSD
```

This provides:
- AI-powered analysis (if OpenAI configured)
- Technical indicators
- Trading signals
- Risk management tips

### Get Technical Analysis

```
/technical GBPUSD
```

Shows:
- RSI levels
- MACD signals
- Moving average trends
- Bollinger Bands

### Get Planning Advice

```
/planning
```

Provides:
- Risk management guidelines
- Position sizing recommendations
- Margin level warnings
- Leverage advice

### Get Financial Advice

```
/financial
```

Includes:
- Account health assessment
- Capital management tips
- Trading psychology advice
- Profit/loss analysis

## Security 🔒

- Only authorized users can use the bot (configured via `ALLOWED_USERNAME`)
- Credentials stored securely in `.env` file
- No trading execution - advice only

## Disclaimer ⚠️

**This bot provides trading advice only. It does NOT execute trades.**

- Trading involves risk
- Always use proper risk management
- Test strategies on demo accounts first
- Never risk more than you can afford to lose
- Past performance doesn't guarantee future results

## Support 💬

For issues or questions, please open an issue on the repository.

---

**Happy Trading! 📈💰**
