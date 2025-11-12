# 🔑 Setup Guide - How to Get API Keys and Tokens

This guide will walk you through getting all the necessary API keys and tokens for SweetTrader Bot.

## 📋 Required Configuration

You need to create a `.env` file in the project root with the following values:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/trading-ai
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_USER_ID=your_telegram_user_id
```

---

## 1. 🤖 Telegram Bot Token (REQUIRED)

### ✅ Bot Already Created!

The Telegram bot has been created: **[@SweetTraderBot](https://t.me/SweetTraderBot)**

### Setup Instructions:

1. **Copy the bot token** (provided by BotFather)
   - ⚠️ **Keep this token secure!** Never commit it to git or share it publicly
   - The token looks like: `8454476033:AAG3tOPNIzGWHsc7B5H5zgCQIR2o6JUPltU`

2. **Create your `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Add the token to your `.env` file**:
   ```env
   TELEGRAM_BOT_TOKEN=8454476033:AAG3tOPNIzGWHsc7B5H5zgCQIR2o6JUPltU
   ```

4. **Optional: Customize your bot** (via @BotFather):
   - `/setdescription` - Set what your bot does
   - `/setuserpic` - Set a profile picture
   - `/setcommands` - Set command descriptions
   - `/setabouttext` - Set about section

### Creating a New Bot (Alternative):

If you want to create your own bot instead:

1. **Open Telegram** and search for **[@BotFather](https://t.me/BotFather)**
2. **Start a chat** with BotFather and send: `/start`
3. **Create a new bot** by sending: `/newbot`
4. **Choose a name** and **username** for your bot
5. **Copy the token** and add it to your `.env` file

### Optional: Customize Your Bot

You can also set a description and profile picture:
- `/setdescription` - Set what your bot does
- `/setuserpic` - Set a profile picture
- `/setcommands` - Set command descriptions

---

## 2. 👤 Telegram User ID (REQUIRED)

You need your Telegram User ID to use the bot.

### Method 1: Using @userinfobot

1. **Search for [@userinfobot](https://t.me/userinfobot)** on Telegram
2. **Start a chat** with it
3. It will immediately show your user ID
4. **Copy the ID** (it's a number like `123456789`)
5. **Paste it in your `.env` file**:
   ```env
   ADMIN_USER_ID=123456789
   ```

### Method 2: Using @getidsbot

1. Search for **[@getidsbot](https://t.me/getidsbot)**
2. Start a chat
3. It will show your user ID

### Method 3: Using @RawDataBot

1. Search for **[@RawDataBot](https://t.me/RawDataBot)**
2. Start a chat
3. Look for `"id":` in the JSON response

---

## 3. 💼 MetaTrader5 Credentials (REQUIRED)

You need your MT5 account login credentials.

### Getting Your MT5 Credentials:

1. **Open MetaTrader5** on your computer
2. **Go to Tools → Options → Server** (or right-click on your account)
3. **Find your account information**:
   - **Login**: Your account number (usually 8 digits)
   - **Server**: Your broker's server name (e.g., `ICMarkets-Demo`, `FXTM-Demo`)
   - **Password**: Your trading password (NOT your investor password)

4. **Add to `.env` file**:
   ```env
   MT5_LOGIN=12345678
   MT5_PASSWORD=your_trading_password
   MT5_SERVER=YourBroker-Demo
   ```

### Important Notes:

- ⚠️ Use a **Demo Account** for testing first!
- The **Server name** must match exactly (case-sensitive)
- Use your **Trading Password**, not the Investor Password
- Make sure MT5 terminal is installed and running when using the bot

### Common Server Names:

- **IC Markets**: `ICMarkets-Demo` or `ICMarkets-Live`
- **FXTM**: `FXTM-Demo` or `FXTM-Live`
- **XM**: `XMGlobal-Demo` or `XMGlobal-Live`
- **Exness**: `Exness-Demo` or `Exness-Live`

Check with your broker for the exact server name.

---

## 4. 🔗 N8N Webhook URL (OPTIONAL but Recommended)

N8N is a workflow automation tool that can provide AI analysis.

### Option A: Using N8N Cloud (Easiest)

1. **Sign up** at [n8n.io](https://n8n.io)
2. **Create a new workflow**
3. **Add a Webhook node**:
   - Drag "Webhook" from the nodes panel
   - Set it to "POST" method
   - Click "Listen for Test Event"
   - Copy the webhook URL (looks like: `https://your-instance.n8n.cloud/webhook/abc123`)

4. **Add processing nodes** (OpenAI, HTTP Request, etc.)
5. **Add a Respond to Webhook node** to return results
6. **Activate the workflow**
7. **Copy the webhook URL** to your `.env`:
   ```env
   N8N_WEBHOOK_URL=https://your-instance.n8n.cloud/webhook/abc123
   ```

### Option B: Self-Hosted N8N

1. **Install N8N** on your server:
   ```bash
   npm install n8n -g
   n8n start
   ```

2. **Access N8N** at `http://localhost:5678`
3. **Create workflow** as described above
4. **Use your server's public URL** for the webhook

### N8N Workflow Example:

Your N8N workflow should:
1. Receive webhook with market data
2. Process with AI (OpenAI, custom logic, etc.)
3. Return JSON response:
   ```json
   {
     "analysis": "Your analysis text in Persian",
     "signal": {
       "action": "BUY",
       "confidence": 85,
       "reason": "Strong bullish indicators"
     }
   }
   ```

### If You Don't Have N8N:

- Leave `N8N_WEBHOOK_URL` empty in `.env`
- The bot will still work with basic technical analysis
- You can add N8N later

---

## 5. 🤖 OpenAI API Key (OPTIONAL)

For AI-powered analysis, you can use OpenAI.

### Getting OpenAI API Key:

1. **Go to** [platform.openai.com](https://platform.openai.com)
2. **Sign up** or **Log in**
3. **Click on your profile** (top right) → **View API keys**
4. **Click "Create new secret key"**
5. **Name it** (e.g., "SweetTrader Bot")
6. **Copy the key** immediately (you won't see it again!)
   - It looks like: `sk-proj-ABC123...xyz`
7. **Add to `.env`**:
   ```env
   OPENAI_API_KEY=sk-proj-ABC123...xyz
   ```

### Important Notes:

- ⚠️ **Keep your API key secret!** Never share it
- OpenAI charges per API call (very cheap, ~$0.002 per analysis)
- You can set usage limits in OpenAI dashboard
- The bot works without OpenAI, but AI analysis won't be available

### If You Don't Have OpenAI:

- Leave `OPENAI_API_KEY` empty in `.env`
- The bot will use basic technical indicators only
- You can add OpenAI later

---

## 📝 Complete .env File Example

Here's a complete example of what your `.env` file should look like:

```env
# Telegram Bot Configuration (REQUIRED)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_ID=987654321

# MetaTrader5 Configuration (REQUIRED)
MT5_LOGIN=12345678
MT5_PASSWORD=MySecurePassword123
MT5_SERVER=ICMarkets-Demo

# N8N Configuration (OPTIONAL)
N8N_WEBHOOK_URL=https://my-instance.n8n.cloud/webhook/trading-ai

# OpenAI Configuration (OPTIONAL)
OPENAI_API_KEY=sk-proj-ABC123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

## ✅ Verification Checklist

Before running the bot, make sure:

- [ ] `.env` file exists in the project root
- [ ] Telegram Bot Token is set (from @BotFather)
- [ ] Telegram User ID is set (from @userinfobot)
- [ ] MT5 Login is set (your account number)
- [ ] MT5 Password is set (your trading password)
- [ ] MT5 Server is set (exact server name from MT5)
- [ ] (Optional) N8N Webhook URL is set
- [ ] (Optional) OpenAI API Key is set

---

## 🚀 Quick Start

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your credentials (use any text editor)

3. **Test the configuration**:
   ```bash
   python bot.py
   ```

4. **If you see errors**, check:
   - All required fields are filled
   - No extra spaces in values
   - Server name matches exactly
   - Telegram token is correct

---

## 🔒 Security Tips

1. **Never commit `.env` to Git** (it's already in `.gitignore`)
2. **Use Demo accounts** for testing
3. **Keep API keys secret**
4. **Use strong passwords**
5. **Enable 2FA** on your accounts when possible

---

## ❓ Troubleshooting

### "Missing required configuration" error
- Check that all required fields in `.env` are filled
- Make sure there are no typos in variable names

### "MT5 login failed"
- Verify login credentials
- Check server name matches exactly (case-sensitive)
- Make sure MT5 terminal is installed and running
- Try connecting manually in MT5 first

### "Telegram bot not responding"
- Verify bot token is correct
- Make sure you started the bot with `/start`
- Check that your user ID is correct

### "N8N/AI not working"
- These are optional features
- Bot will still work with basic analysis
- Check webhook URL is accessible
- Verify API keys are correct

---

## 📞 Need Help?

If you're stuck:
1. Check the main README.md
2. Verify all credentials are correct
3. Test each service individually
4. Check logs for specific error messages

---

**Good luck with your trading bot! 📈💰**

