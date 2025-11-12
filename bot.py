"""
SweetTrader Telegram Bot - Main Bot File
"""
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from config import Config
from mt5_handler import MT5Handler
from n8n_handler import N8NHandler
from ai_analyzer import AIAnalyzer
from utils import (
    BOT_TEXTS, format_account_info, format_positions, 
    format_signal, format_analysis, check_authorization
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers - will be updated with user credentials
mt5 = None
n8n = N8NHandler(Config.N8N_WEBHOOK_URL) if Config.N8N_WEBHOOK_URL else None
ai_analyzer = AIAnalyzer(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None

# User credentials storage (in-memory, can be persisted to file)
user_credentials = {}

# Conversation states for setup
MT5_LOGIN_STATE, MT5_PASSWORD_STATE, MT5_SERVER_STATE = range(3)

# Authorization decorator
authorized = check_authorization(Config.ALLOWED_USERNAME)

def initialize_mt5(login=None, password=None, server=None):
    """Initialize or update MT5 handler with credentials"""
    global mt5
    login = login or Config.MT5_LOGIN
    password = password or Config.MT5_PASSWORD
    server = server or Config.MT5_SERVER
    
    if login and password and server:
        mt5 = MT5Handler(login, password, server)
        return True
    return False

# Initialize MT5 if credentials are available
if Config.MT5_LOGIN and Config.MT5_PASSWORD and Config.MT5_SERVER:
    initialize_mt5()

@authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not mt5:
        await update.message.reply_text(
            BOT_TEXTS['welcome'] + "\n\n"
            "⚠️ MT5 is not configured yet.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(
                BOT_TEXTS['not_connected'] + "\n" + 
                BOT_TEXTS['error'] + "Please check your MT5 settings.\n"
                "Use /setup to reconfigure."
            )
            return
    
    await update.message.reply_text(BOT_TEXTS['welcome'])

@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = BOT_TEXTS['help'] + "\n\n/setup - Configure MT5 credentials"
    await update.message.reply_text(help_text)

@authorized
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start MT5 setup conversation"""
    await update.message.reply_text(
        "🔧 MT5 Configuration Setup\n\n"
        "Please provide your MetaTrader5 credentials.\n\n"
        "📝 Step 1/3: Enter your MT5 Login (account number):\n"
        "Example: 12345678\n\n"
        "Type /cancel to cancel setup."
    )
    return MT5_LOGIN_STATE

@authorized
async def receive_mt5_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive MT5 login"""
    try:
        login = int(update.message.text.strip())
        context.user_data['mt5_login'] = login
        
        await update.message.reply_text(
            f"✅ Login saved: {login}\n\n"
            "📝 Step 2/3: Enter your MT5 Password:\n"
            "⚠️ This will be stored securely.\n\n"
            "Type /cancel to cancel setup."
        )
        return MT5_PASSWORD_STATE
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid login. Please enter a valid number.\n"
            "Example: 12345678\n\n"
            "Type /cancel to cancel setup."
        )
        return MT5_LOGIN_STATE

@authorized
async def receive_mt5_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive MT5 password"""
    password = update.message.text.strip()
    context.user_data['mt5_password'] = password
    
    await update.message.reply_text(
        "✅ Password saved.\n\n"
        "📝 Step 3/3: Enter your MT5 Server name:\n"
        "Examples: ICMarkets-Demo, FXTM-Demo, XMGlobal-Demo\n"
        "⚠️ Server name must match exactly (case-sensitive).\n\n"
        "Type /cancel to cancel setup."
    )
    return MT5_SERVER_STATE

@authorized
async def receive_mt5_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive MT5 server and test connection"""
    server = update.message.text.strip()
    context.user_data['mt5_server'] = server
    
    # Get credentials from context
    login = context.user_data.get('mt5_login')
    password = context.user_data.get('mt5_password')
    
    # Test connection
    await update.message.reply_text("🔄 Testing connection to MT5...")
    
    # Initialize MT5 with new credentials
    test_mt5 = MT5Handler(login, password, server)
    if test_mt5.connect():
        # Connection successful
        global mt5
        mt5 = test_mt5
        
        # Save to .env file
        save_credentials_to_env(login, password, server)
        
        account_info = mt5.get_account_info()
        account_text = ""
        if account_info:
            account_text = f"\n\n✅ Connected successfully!\n"
            account_text += f"Account: {account_info.get('login')}\n"
            account_text += f"Balance: {account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}\n"
            account_text += f"Server: {account_info.get('server', 'N/A')}"
        
        await update.message.reply_text(
            f"✅ Configuration saved successfully!{account_text}\n\n"
            "You can now use all trading commands."
        )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Connection failed. Please check your credentials:\n"
            f"Login: {login}\n"
            f"Server: {server}\n\n"
            "Common issues:\n"
            "• Server name doesn't match exactly\n"
            "• Wrong password\n"
            "• Account doesn't allow API access\n"
            "• MT5 terminal not running\n\n"
            "Type /setup to try again."
        )
        context.user_data.clear()
        return ConversationHandler.END

@authorized
async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel setup conversation"""
    context.user_data.clear()
    await update.message.reply_text("❌ Setup cancelled.")
    return ConversationHandler.END

def save_credentials_to_env(login, password, server):
    """Save credentials to .env file"""
    env_file = '.env'
    
    # Read existing .env if it exists
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Update MT5 credentials
    env_vars['MT5_LOGIN'] = str(login)
    env_vars['MT5_PASSWORD'] = password
    env_vars['MT5_SERVER'] = server
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.write("# ============================================\n")
        f.write("# SweetTrader Bot Configuration\n")
        f.write("# ============================================\n\n")
        
        # Write Telegram config
        f.write("# Telegram Bot Configuration\n")
        f.write(f"TELEGRAM_BOT_TOKEN={env_vars.get('TELEGRAM_BOT_TOKEN', '')}\n")
        f.write(f"ADMIN_USER_ID={env_vars.get('ADMIN_USER_ID', '')}\n\n")
        
        # Write MT5 config
        f.write("# MetaTrader5 Configuration\n")
        f.write(f"MT5_LOGIN={env_vars['MT5_LOGIN']}\n")
        f.write(f"MT5_PASSWORD={env_vars['MT5_PASSWORD']}\n")
        f.write(f"MT5_SERVER={env_vars['MT5_SERVER']}\n\n")
        
        # Write optional configs
        f.write("# N8N Configuration (Optional)\n")
        f.write(f"N8N_WEBHOOK_URL={env_vars.get('N8N_WEBHOOK_URL', '')}\n\n")
        f.write("# OpenAI Configuration (Optional)\n")
        f.write(f"OPENAI_API_KEY={env_vars.get('OPENAI_API_KEY', '')}\n\n")
        f.write("# Authorization\n")
        f.write(f"ALLOWED_USERNAME={env_vars.get('ALLOWED_USERNAME', 'reyi_t')}\n")
    
    logger.info("MT5 credentials saved to .env file")

@authorized
async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /account command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    account_info = mt5.get_account_info()
    if account_info:
        await update.message.reply_text(format_account_info(account_info))
    else:
        await update.message.reply_text(BOT_TEXTS['error'] + "Unable to retrieve account information.")

@authorized
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    account_info = mt5.get_account_info()
    if account_info:
        balance_text = f"{BOT_TEXTS['balance']}{account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}"
        await update.message.reply_text(balance_text)
    else:
        await update.message.reply_text(BOT_TEXTS['error'] + "Unable to retrieve balance.")

@authorized
async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /positions command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    positions_list = mt5.get_positions()
    await update.message.reply_text(format_positions(positions_list))

@authorized
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please enter a symbol. Example: /analyze EURUSD")
        return
    
    symbol = context.args[0].upper()
    
    # Send analyzing message
    analyzing_msg = await update.message.reply_text(BOT_TEXTS['analyzing'] + f" {symbol}...")
    
    try:
        # Get market data
        symbol_info = mt5.get_symbol_info(symbol)
        if not symbol_info:
            await analyzing_msg.edit_text(f"❌ Symbol {symbol} not found.")
            return
        
        # Get historical data
        rates = mt5.get_rates(symbol, count=100)
        if rates is None or len(rates) == 0:
            await analyzing_msg.edit_text(f"❌ Unable to retrieve price data for {symbol}.")
            return
        
        # Calculate indicators
        indicators = ai_analyzer.calculate_technical_indicators(rates) if ai_analyzer else {}
        
        # Get AI analysis
        market_data = {
            'current_price': symbol_info.get('bid', 0),
            'bid': symbol_info.get('bid', 0),
            'ask': symbol_info.get('ask', 0),
            'spread': symbol_info.get('spread', 0),
        }
        
        analysis_text = None
        if ai_analyzer:
            analysis_text = ai_analyzer.generate_ai_analysis(symbol, indicators, market_data)
        
        # Try N8N analysis
        if n8n:
            n8n_result = n8n.send_analysis_request(symbol, 'H1', market_data)
            if n8n_result and n8n_result.get('analysis'):
                analysis_text = n8n_result.get('analysis')
        
        # Format response
        if analysis_text:
            response = format_analysis(analysis_text, indicators)
        else:
            response = f"📊 Analysis for {symbol}:\n\n"
            if indicators:
                response += f"RSI: {indicators.get('rsi', 'N/A')}\n"
                response += f"MACD: {indicators.get('macd', 'N/A')}\n"
                response += f"Current Price: {market_data['current_price']:.5f}\n"
        
        await analyzing_msg.edit_text(response)
        
    except Exception as e:
        logger.error(f"Error in analyze command: {e}")
        await analyzing_msg.edit_text(BOT_TEXTS['error'] + str(e))

@authorized
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /signal command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please enter a symbol. Example: /signal EURUSD")
        return
    
    symbol = context.args[0].upper()
    
    try:
        # Get market data
        symbol_info = mt5.get_symbol_info(symbol)
        if not symbol_info:
            await update.message.reply_text(f"❌ Symbol {symbol} not found.")
            return
        
        # Get historical data
        rates = mt5.get_rates(symbol, count=100)
        if rates is None or len(rates) == 0:
            await update.message.reply_text(f"❌ Unable to retrieve price data for {symbol}.")
            return
        
        # Calculate indicators
        indicators = {}
        if ai_analyzer:
            indicators = ai_analyzer.calculate_technical_indicators(rates)
        
        # Get signal from AI analyzer
        signal_data = {}
        if ai_analyzer:
            signal_data = ai_analyzer.analyze_signal(indicators)
        
        # Try N8N for signal
        if n8n:
            market_data = {
                'current_price': symbol_info.get('bid', 0),
                'bid': symbol_info.get('bid', 0),
                'ask': symbol_info.get('ask', 0),
                'spread': symbol_info.get('spread', 0),
            }
            n8n_signal = n8n.get_trading_signal(symbol, market_data)
            if n8n_signal:
                signal_data = n8n_signal
        
        if signal_data:
            await update.message.reply_text(format_signal(signal_data, symbol))
        else:
            await update.message.reply_text(f"❌ Unable to get signal for {symbol}.")
            
    except Exception as e:
        logger.error(f"Error in signal command: {e}")
        await update.message.reply_text(BOT_TEXTS['error'] + str(e))

@authorized
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buy command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Please enter symbol and volume. Example: /buy EURUSD 0.01")
        return
    
    symbol = context.args[0].upper()
    try:
        volume = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Volume must be a number.")
        return
    
    # Optional SL and TP
    sl = float(context.args[2]) if len(context.args) > 2 else None
    tp = float(context.args[3]) if len(context.args) > 3 else None
    
    result = mt5.place_order(symbol, 'BUY', volume, sl=sl, tp=tp)
    
    if result and result.get('success'):
        await update.message.reply_text(
            f"{BOT_TEXTS['success']} Buy order placed.\n"
            f"🎫 Ticket: {result.get('order')}\n"
            f"📊 Volume: {result.get('volume')}\n"
            f"💰 Price: {result.get('price')}"
        )
    else:
        error_msg = result.get('error', 'Unknown error') if result else 'Unknown error'
        await update.message.reply_text(f"{BOT_TEXTS['error']}{error_msg}")

@authorized
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sell command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Please enter symbol and volume. Example: /sell EURUSD 0.01")
        return
    
    symbol = context.args[0].upper()
    try:
        volume = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Volume must be a number.")
        return
    
    # Optional SL and TP
    sl = float(context.args[2]) if len(context.args) > 2 else None
    tp = float(context.args[3]) if len(context.args) > 3 else None
    
    result = mt5.place_order(symbol, 'SELL', volume, sl=sl, tp=tp)
    
    if result and result.get('success'):
        await update.message.reply_text(
            f"{BOT_TEXTS['success']} Sell order placed.\n"
            f"🎫 Ticket: {result.get('order')}\n"
            f"📊 Volume: {result.get('volume')}\n"
            f"💰 Price: {result.get('price')}"
        )
    else:
        error_msg = result.get('error', 'Unknown error') if result else 'Unknown error'
        await update.message.reply_text(f"{BOT_TEXTS['error']}{error_msg}")

@authorized
async def close_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /close command"""
    if not mt5:
        await update.message.reply_text(
            "❌ MT5 is not configured.\n"
            "Use /setup to configure your MT5 credentials."
        )
        return
    
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please enter position ticket number. Example: /close 123456")
        return
    
    try:
        ticket = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Ticket number must be a number.")
        return
    
    result = mt5.close_position(ticket)
    
    if result and result.get('success'):
        await update.message.reply_text(
            f"{BOT_TEXTS['success']} Position closed.\n"
            f"🎫 Ticket: {result.get('order')}\n"
            f"💰 Price: {result.get('price')}"
        )
    else:
        error_msg = result.get('error', 'Unknown error') if result else 'Unknown error'
        await update.message.reply_text(f"{BOT_TEXTS['error']}{error_msg}")

def main():
    """Main function to run the bot"""
    # Validate only Telegram token (MT5 can be configured via bot)
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        print("❌ TELEGRAM_BOT_TOKEN is required in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Setup conversation handler
    setup_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setup", setup)],
        states={
            MT5_LOGIN_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_mt5_login)],
            MT5_PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_mt5_password)],
            MT5_SERVER_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_mt5_server)],
        },
        fallbacks=[CommandHandler("cancel", cancel_setup)],
    )
    
    # Register command handlers
    application.add_handler(setup_conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("account", account))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("positions", positions))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("signal", signal))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("sell", sell))
    application.add_handler(CommandHandler("close", close_position))
    
    # Connect to MT5 if credentials are available
    if mt5:
        logger.info("Connecting to MetaTrader5...")
        if mt5.connect():
            logger.info("Successfully connected to MetaTrader5")
        else:
            logger.warning("Failed to connect to MetaTrader5. Use /setup to configure credentials.")
    else:
        logger.info("MT5 not configured. Use /setup command to configure MT5 credentials.")
    
    # Start the bot
    logger.info("Starting SweetTrader Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Cleanup
    if mt5:
        mt5.disconnect()

if __name__ == '__main__':
    main()

