"""
SweetTrader Bot - Automatic Trading Signals
A bot that automatically sends reliable trading signals
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from mt5_handler import MT5Handler
from signal_generator import SignalGenerator
from utils import check_authorization

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers
mt5 = None
signal_generator = SignalGenerator()

# Store user chat IDs for sending signals
user_chat_ids = set()

# Authorization decorator
authorized = check_authorization(Config.ALLOWED_USERNAMES)

# Symbols to monitor
MONITORED_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']

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
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Store user chat ID for sending signals
    user_chat_ids.add(chat_id)
    logger.info(f"User @{user.username} (ID: {chat_id}) started the bot")
    
    welcome_msg = (
        "👋 Welcome to SweetTrader Signal Bot! 🚀\n\n"
        "I will automatically send you reliable trading signals for better trading opportunities.\n\n"
        "📊 Monitoring major currency pairs:\n"
        "• EURUSD\n"
        "• GBPUSD\n"
        "• USDJPY\n"
        "• AUDUSD\n"
        "• USDCAD\n\n"
        "🔔 You will receive signals automatically when strong trading opportunities are detected.\n\n"
        "⚠️ Always use proper risk management and stop losses!"
    )
    await update.message.reply_text(welcome_msg)

async def check_and_send_signals(application: Application):
    """Periodically check for trading signals and send to users"""
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            if not mt5 or not mt5.connected:
                logger.warning("MT5 not connected, skipping signal check")
                continue
            
            if not user_chat_ids:
                logger.info("No users registered, skipping signal check")
                continue
            
            logger.info(f"Checking for signals... ({len(user_chat_ids)} users)")
            
            for symbol in MONITORED_SYMBOLS:
                try:
                    # Get market data
                    symbol_info = mt5.get_symbol_info(symbol)
                    if not symbol_info:
                        continue
                    
                    # Get historical data
                    rates = mt5.get_rates(symbol, count=100)
                    if rates is None or len(rates) == 0:
                        continue
                    
                    # Calculate indicators
                    indicators = signal_generator.calculate_indicators(rates)
                    
                    # Get market data
                    market_data = {
                        'current_price': symbol_info.get('bid', 0),
                        'bid': symbol_info.get('bid', 0),
                        'ask': symbol_info.get('ask', 0),
                        'spread': symbol_info.get('spread', 0),
                    }
                    
                    # Generate signal
                    signal = signal_generator.generate_signal(symbol, indicators, market_data)
                    
                    if signal and signal['confidence'] >= 70:  # Only send high-confidence signals
                        message = signal_generator.format_signal_message(signal)
                        
                        # Send to all registered users
                        for chat_id in user_chat_ids.copy():
                            try:
                                await application.bot.send_message(
                                    chat_id=chat_id,
                                    text=message,
                                    parse_mode='Markdown'
                                )
                                logger.info(f"Sent {signal['action']} signal for {symbol} to user {chat_id}")
                            except Exception as e:
                                logger.error(f"Error sending message to {chat_id}: {e}")
                                # Remove invalid chat IDs
                                user_chat_ids.discard(chat_id)
                        
                        # Wait a bit between signals
                        await asyncio.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in signal checking loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

async def post_init(application: Application):
    """Start signal checking after bot initialization"""
    asyncio.create_task(check_and_send_signals(application))
    logger.info("Signal checking task started")

def main():
    """Main function to run the bot"""
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        print("❌ TELEGRAM_BOT_TOKEN is required in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Start the bot
    logger.info("Starting SweetTrader Signal Bot...")
    logger.info("Signal checking will start automatically after bot initialization...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Cleanup
    if mt5:
        mt5.disconnect()

if __name__ == '__main__':
    main()
