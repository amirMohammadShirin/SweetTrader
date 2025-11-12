"""
SweetTrader Bot - Trading Advisor
A bot that provides reliable trading advice for MetaTrader5
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from mt5_handler import MT5Handler
from advisor import TradingAdvisor
from utils import check_authorization

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers
mt5 = None
advisor = TradingAdvisor(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else TradingAdvisor()

# Authorization decorator
authorized = check_authorization(Config.ALLOWED_USERNAME)

def initialize_mt5():
    """Initialize MT5 handler if credentials are available"""
    global mt5
    if Config.MT5_LOGIN and Config.MT5_PASSWORD and Config.MT5_SERVER:
        mt5 = MT5Handler(Config.MT5_LOGIN, Config.MT5_PASSWORD, Config.MT5_SERVER)
        if mt5.connect():
            logger.info("Connected to MT5")
        else:
            logger.warning("Failed to connect to MT5")
    else:
        logger.info("MT5 credentials not configured")

# Initialize MT5
initialize_mt5()

@authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_msg = (
        "👋 Welcome to SweetTrader Advisor Bot! 🚀\n\n"
        "I provide reliable trading advice including:\n"
        "• 📊 Technical analysis\n"
        "• 📋 Trading planning\n"
        "• 💵 Financial management\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(welcome_msg)

@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📖 Available Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/account - Account information\n"
        "/advice <SYMBOL> - Get comprehensive trading advice\n"
        "/technical <SYMBOL> - Get technical analysis\n"
        "/planning - Get trading plan advice\n"
        "/financial - Get financial management advice\n\n"
        "Example: /advice EURUSD"
    )
    await update.message.reply_text(help_text)

@authorized
async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /account command"""
    if not mt5 or not mt5.connected:
        await update.message.reply_text(
            "❌ MT5 is not connected.\n"
            "Please configure MT5 credentials in .env file."
        )
        return
    
    account_info = mt5.get_account_info()
    if account_info:
        msg = (
            f"📊 Account Information:\n\n"
            f"Account: {account_info.get('login')}\n"
            f"Balance: {account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}\n"
            f"Equity: {account_info.get('equity', 0):.2f} {account_info.get('currency', 'USD')}\n"
            f"Margin: {account_info.get('margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
            f"Free Margin: {account_info.get('free_margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
            f"Margin Level: {account_info.get('margin_level', 0):.2f}%\n"
            f"Profit/Loss: {account_info.get('profit', 0):.2f} {account_info.get('currency', 'USD')}\n"
            f"Leverage: {account_info.get('leverage', 0)}:1\n"
            f"Server: {account_info.get('server', 'N/A')}"
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ Unable to retrieve account information.")

@authorized
async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /advice command - Comprehensive advice"""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please enter a symbol. Example: /advice EURUSD")
        return
    
    if not mt5 or not mt5.connected:
        await update.message.reply_text("❌ MT5 is not connected.")
        return
    
    symbol = context.args[0].upper()
    analyzing_msg = await update.message.reply_text(f"🔍 Analyzing {symbol}...")
    
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
        indicators = advisor.calculate_technical_indicators(rates)
        
        # Get account info
        account_info = mt5.get_account_info() or {}
        
        # Get market data
        market_data = {
            'current_price': symbol_info.get('bid', 0),
            'bid': symbol_info.get('bid', 0),
            'ask': symbol_info.get('ask', 0),
            'spread': symbol_info.get('spread', 0),
        }
        
        # Get AI advice if available
        ai_advice = advisor.get_ai_advice(symbol, indicators, market_data, account_info)
        
        # Build response
        response = f"🤖 Trading Advice for {symbol}\n\n"
        response += "=" * 30 + "\n\n"
        
        if ai_advice:
            response += f"{ai_advice}\n\n"
            response += "=" * 30 + "\n\n"
        
        # Add technical analysis
        response += advisor.get_technical_advice(symbol, indicators, market_data)
        
        await analyzing_msg.edit_text(response)
        
    except Exception as e:
        logger.error(f"Error in advice command: {e}")
        await analyzing_msg.edit_text(f"❌ Error: {str(e)}")

@authorized
async def technical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /technical command"""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please enter a symbol. Example: /technical EURUSD")
        return
    
    if not mt5 or not mt5.connected:
        await update.message.reply_text("❌ MT5 is not connected.")
        return
    
    symbol = context.args[0].upper()
    analyzing_msg = await update.message.reply_text(f"🔍 Analyzing {symbol}...")
    
    try:
        symbol_info = mt5.get_symbol_info(symbol)
        if not symbol_info:
            await analyzing_msg.edit_text(f"❌ Symbol {symbol} not found.")
            return
        
        rates = mt5.get_rates(symbol, count=100)
        if rates is None or len(rates) == 0:
            await analyzing_msg.edit_text(f"❌ Unable to retrieve price data for {symbol}.")
            return
        
        indicators = advisor.calculate_technical_indicators(rates)
        market_data = {
            'current_price': symbol_info.get('bid', 0),
            'bid': symbol_info.get('bid', 0),
            'ask': symbol_info.get('ask', 0),
            'spread': symbol_info.get('spread', 0),
        }
        
        advice = advisor.get_technical_advice(symbol, indicators, market_data)
        await analyzing_msg.edit_text(advice)
        
    except Exception as e:
        logger.error(f"Error in technical command: {e}")
        await analyzing_msg.edit_text(f"❌ Error: {str(e)}")

@authorized
async def planning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /planning command"""
    if not mt5 or not mt5.connected:
        await update.message.reply_text("❌ MT5 is not connected.")
        return
    
    account_info = mt5.get_account_info()
    if not account_info:
        await update.message.reply_text("❌ Unable to retrieve account information.")
        return
    
    advice = advisor.get_planning_advice(account_info)
    await update.message.reply_text(advice)

@authorized
async def financial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /financial command"""
    if not mt5 or not mt5.connected:
        await update.message.reply_text("❌ MT5 is not connected.")
        return
    
    account_info = mt5.get_account_info()
    if not account_info:
        await update.message.reply_text("❌ Unable to retrieve account information.")
        return
    
    advice = advisor.get_financial_advice(account_info)
    await update.message.reply_text(advice)

def main():
    """Main function to run the bot"""
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        print("❌ TELEGRAM_BOT_TOKEN is required in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("account", account))
    application.add_handler(CommandHandler("advice", advice))
    application.add_handler(CommandHandler("technical", technical))
    application.add_handler(CommandHandler("planning", planning))
    application.add_handler(CommandHandler("financial", financial))
    
    # Start the bot
    logger.info("Starting SweetTrader Advisor Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Cleanup
    if mt5:
        mt5.disconnect()

if __name__ == '__main__':
    main()
