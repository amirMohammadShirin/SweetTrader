"""
SweetTrader Telegram Bot - Main Bot File
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from mt5_handler import MT5Handler
from n8n_handler import N8NHandler
from ai_analyzer import AIAnalyzer
from utils import (
    BOT_TEXTS, format_account_info, format_positions, 
    format_signal, format_analysis
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers
mt5 = MT5Handler(Config.MT5_LOGIN, Config.MT5_PASSWORD, Config.MT5_SERVER)
n8n = N8NHandler(Config.N8N_WEBHOOK_URL) if Config.N8N_WEBHOOK_URL else None
ai_analyzer = AIAnalyzer(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(
                BOT_TEXTS['not_connected'] + "\n" + 
                BOT_TEXTS['error'] + "Please check your MT5 settings."
            )
            return
    
    await update.message.reply_text(BOT_TEXTS['welcome'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(BOT_TEXTS['help'])

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /account command"""
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    account_info = mt5.get_account_info()
    if account_info:
        await update.message.reply_text(format_account_info(account_info))
    else:
        await update.message.reply_text(BOT_TEXTS['error'] + "Unable to retrieve account information.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
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

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /positions command"""
    if not mt5.connected:
        if not mt5.connect():
            await update.message.reply_text(BOT_TEXTS['not_connected'])
            return
    
    positions_list = mt5.get_positions()
    await update.message.reply_text(format_positions(positions_list))

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command"""
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

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /signal command"""
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

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buy command"""
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

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sell command"""
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

async def close_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /close command"""
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
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        print("Please create .env file and enter your settings.")
        return
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
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
    
    # Connect to MT5
    logger.info("Connecting to MetaTrader5...")
    if mt5.connect():
        logger.info("Successfully connected to MetaTrader5")
    else:
        logger.warning("Failed to connect to MetaTrader5. Bot will still run but MT5 features won't work.")
    
    # Start the bot
    logger.info("Starting SweetTrader Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Cleanup
    mt5.disconnect()

if __name__ == '__main__':
    main()

