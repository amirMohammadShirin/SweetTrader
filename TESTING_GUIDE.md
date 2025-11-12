# 🧪 Testing Guide - How to Run and Test SweetTrader Bot

## Prerequisites Checklist ✅

Before running the bot, make sure you have:

- [ ] Python 3.8 or higher installed
- [ ] MetaTrader5 terminal installed on your system
- [ ] Telegram Bot Token (from @BotFather)
- [ ] MT5 account credentials (login, password, server)
- [ ] (Optional) OpenAI API key for AI advice

---

## Step 1: Install Dependencies 📦

### 1.1 Create Virtual Environment (Recommended)

```bash
cd SweetTrader
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Required Packages

```bash
pip install -r requirements.txt
```

This will install:
- `python-telegram-bot` - Telegram bot framework
- `MetaTrader5` - MT5 Python API
- `pandas` - Data analysis
- `numpy` - Numerical computing
- `python-dotenv` - Environment variables
- `openai` - OpenAI API (optional)

---

## Step 2: Configure the Bot ⚙️

### 2.1 Create .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env  # If .env.example exists
# OR create manually
touch .env
```

### 2.2 Add Your Configuration

Edit `.env` file with your credentials:

```env
# Telegram Bot Configuration (REQUIRED)
TELEGRAM_BOT_TOKEN=8454476033:AAG3tOPNIzGWHsc7B5H5zgCQIR2o6JUPltU

# MetaTrader5 Configuration (REQUIRED for market data)
MT5_LOGIN=12345678
MT5_PASSWORD=your_mt5_password
MT5_SERVER=YourBroker-Demo

# OpenAI Configuration (OPTIONAL - for AI advice)
OPENAI_API_KEY=sk-your-openai-api-key

# Authorization (REQUIRED)
ALLOWED_USERNAME=reyi_t
```

### 2.3 Get Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the token and add to `.env`

### 2.4 Get Your MT5 Credentials

1. Open MetaTrader5 terminal
2. Go to Tools → Options → Server
3. Find your:
   - **Login**: Account number (usually 8 digits)
   - **Server**: Broker server name (e.g., `ICMarkets-Demo`)
   - **Password**: Your trading password

---

## Step 3: Run the Bot 🚀

### 3.1 Start the Bot

```bash
python bot.py
```

Or if using Python 3 explicitly:

```bash
python3 bot.py
```

### 3.2 Expected Output

You should see:

```
INFO - Starting SweetTrader Advisor Bot...
INFO - Connected to MT5. Account: 12345678
```

If MT5 is not configured, you'll see:

```
INFO - MT5 credentials not configured
INFO - Starting SweetTrader Advisor Bot...
```

The bot will keep running and listening for Telegram messages.

---

## Step 4: Test the Bot 📱

### 4.1 Open Telegram

1. Open Telegram app
2. Search for your bot (e.g., `@SweetTraderBot`)
3. Click "Start" or send `/start`

### 4.2 Test Basic Commands

#### Test 1: Start Command
```
/start
```
**Expected**: Welcome message with bot description

#### Test 2: Help Command
```
/help
```
**Expected**: List of all available commands

#### Test 3: Account Information
```
/account
```
**Expected**: 
- If MT5 connected: Account details (balance, equity, margin, etc.)
- If MT5 not connected: Error message

#### Test 4: Technical Analysis
```
/technical EURUSD
```
**Expected**: Technical analysis with RSI, MACD, Moving Averages, Bollinger Bands

#### Test 5: Comprehensive Advice
```
/advice GBPUSD
```
**Expected**: 
- AI advice (if OpenAI configured)
- Technical analysis
- Trading recommendations

#### Test 6: Planning Advice
```
/planning
```
**Expected**: Risk management, position sizing, margin advice

#### Test 7: Financial Advice
```
/financial
```
**Expected**: Capital management, trading psychology, account health

### 4.3 Test Authorization

Try accessing the bot from an unauthorized account:
- **Expected**: "❌ Invalid user" message
- Bot should log the unauthorized attempt

---

## Step 5: Verify Features ✅

### 5.1 Technical Indicators

Test with different symbols:
```
/technical EURUSD
/technical GBPUSD
/technical USDJPY
```

Verify that indicators are calculated:
- RSI values (0-100)
- MACD values
- Moving averages
- Bollinger Bands

### 5.2 AI Advice (if OpenAI configured)

```
/advice EURUSD
```

Verify:
- AI-generated analysis appears
- Advice is relevant to the symbol
- Includes technical, planning, and financial aspects

### 5.3 Account Information

```
/account
```

Verify:
- Balance is displayed correctly
- Equity matches MT5 terminal
- Margin level is calculated
- All values are in correct currency

---

## Troubleshooting 🔧

### Issue 1: Bot Not Starting

**Error**: `TELEGRAM_BOT_TOKEN is required`

**Solution**:
- Check `.env` file exists
- Verify `TELEGRAM_BOT_TOKEN` is set
- Make sure no extra spaces in token

### Issue 2: MT5 Connection Failed

**Error**: `MT5 initialization failed` or `MT5 login failed`

**Solutions**:
1. Make sure MT5 terminal is installed and running
2. Verify credentials in `.env` match MT5 terminal
3. Check server name is exact (case-sensitive)
4. Ensure account allows API access
5. Try connecting manually in MT5 first

### Issue 3: "Invalid user" Error

**Error**: Bot responds with "❌ Invalid user"

**Solution**:
- Check `ALLOWED_USERNAME` in `.env`
- Make sure your Telegram username matches exactly
- Username is case-insensitive but must match

### Issue 4: Symbol Not Found

**Error**: `Symbol EURUSD not found`

**Solutions**:
1. Check symbol name is correct (e.g., `EURUSD`, not `EUR/USD`)
2. Verify symbol is available in your MT5 account
3. Make sure MT5 is connected

### Issue 5: No Price Data

**Error**: `Unable to retrieve price data`

**Solutions**:
1. Check MT5 connection
2. Verify symbol is available
3. Make sure market is open (for live accounts)
4. Check internet connection

### Issue 6: AI Advice Not Working

**Error**: No AI advice in `/advice` command

**Solutions**:
1. Check `OPENAI_API_KEY` is set in `.env`
2. Verify API key is valid
3. Check you have OpenAI credits
4. Bot will still work with technical analysis only

---

## Testing Checklist 📋

Use this checklist to verify all features:

- [ ] Bot starts without errors
- [ ] `/start` command works
- [ ] `/help` command shows all commands
- [ ] `/account` shows account information
- [ ] `/technical EURUSD` shows technical analysis
- [ ] `/advice EURUSD` shows comprehensive advice
- [ ] `/planning` shows planning advice
- [ ] `/financial` shows financial advice
- [ ] Unauthorized users get "Invalid user" message
- [ ] All indicators are calculated correctly
- [ ] AI advice appears (if OpenAI configured)
- [ ] Error messages are clear and helpful

---

## Advanced Testing 🧪

### Test with Different Symbols

```bash
# Major pairs
/technical EURUSD
/technical GBPUSD
/technical USDJPY
/technical AUDUSD

# Cross pairs
/technical EURGBP
/technical GBPJPY
```

### Test Error Handling

1. **Invalid symbol**: `/technical INVALID`
2. **Missing symbol**: `/technical`
3. **MT5 disconnected**: Stop MT5 terminal, then try commands

### Test Authorization

1. Try from different Telegram account
2. Verify unauthorized access is blocked
3. Check logs for unauthorized attempts

---

## Monitoring & Logs 📊

### View Logs

The bot logs important events:
- Connection status
- Command execution
- Errors
- Unauthorized access attempts

Logs appear in console when running the bot.

### Check Bot Status

While bot is running, you can:
- Check console for errors
- Monitor Telegram for responses
- Verify MT5 connection status

---

## Quick Test Script 🚀

Create a simple test script to verify setup:

```python
# test_setup.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Configuration...")
print(f"Telegram Token: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Missing'}")
print(f"MT5 Login: {'✅ Set' if os.getenv('MT5_LOGIN') else '❌ Missing'}")
print(f"MT5 Password: {'✅ Set' if os.getenv('MT5_PASSWORD') else '❌ Missing'}")
print(f"MT5 Server: {'✅ Set' if os.getenv('MT5_SERVER') else '❌ Missing'}")
print(f"OpenAI Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '⚠️ Optional'}")
print(f"Allowed User: {os.getenv('ALLOWED_USERNAME', 'Not set')}")
```

Run it:
```bash
python test_setup.py
```

---

## Next Steps 🎯

After successful testing:

1. ✅ Verify all commands work
2. ✅ Test with real market data
3. ✅ Check AI advice quality (if using OpenAI)
4. ✅ Monitor bot performance
5. ✅ Keep bot running for continuous advice

---

## Support 💬

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review bot logs for error messages
3. Verify all configuration is correct
4. Test MT5 connection separately
5. Check Telegram bot token is valid

---

**Happy Testing! 🚀**

