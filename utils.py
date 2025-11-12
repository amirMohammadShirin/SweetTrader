"""
Utility functions for SweetTrader Bot
"""
from typing import Dict, Any, Callable
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Bot text messages
BOT_TEXTS = {
    'welcome': 'Welcome to SweetTrader Bot! 🚀\n\nThis bot will help you make better trading decisions.',
    'help': '''📖 Bot Usage Guide:

/start - Start the bot
/account - Account information
/balance - Account balance
/positions - Open positions
/analyze <SYMBOL> - Analyze symbol (e.g., /analyze EURUSD)
/signal <SYMBOL> - Get trading signal
/buy <SYMBOL> <VOLUME> - Buy order (e.g., /buy EURUSD 0.01)
/sell <SYMBOL> <VOLUME> - Sell order
/close <TICKET> - Close position
/help - Show this help

💡 Note: Enter all commands in English.''',
    'not_connected': '❌ Not connected to MetaTrader5.',
    'error': '❌ Error: ',
    'success': '✅ Success: ',
    'account_info': '📊 Account Information:',
    'balance': '💰 Balance: ',
    'equity': '💵 Equity: ',
    'margin': '📈 Margin: ',
    'free_margin': '💳 Free Margin: ',
    'profit': '💸 Profit/Loss: ',
    'no_positions': '📭 No open positions.',
    'positions': '📋 Open Positions:',
    'analyzing': '🔍 Analyzing...',
    'signal': '📡 Trading Signal:',
    'buy': '🟢 BUY',
    'sell': '🔴 SELL',
    'hold': '⚪ HOLD',
    'confidence': 'Confidence: ',
    'reason': 'Reason: ',
}

def format_account_info(account_info: Dict) -> str:
    """Format account information"""
    if not account_info:
        return BOT_TEXTS['not_connected']
    
    text = f"{BOT_TEXTS['account_info']}\n\n"
    text += f"{BOT_TEXTS['balance']}{account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{BOT_TEXTS['equity']}{account_info.get('equity', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{BOT_TEXTS['margin']}{account_info.get('margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{BOT_TEXTS['free_margin']}{account_info.get('free_margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
    
    profit = account_info.get('profit', 0)
    profit_emoji = '💚' if profit >= 0 else '❤️'
    text += f"{BOT_TEXTS['profit']}{profit_emoji} {profit:.2f} {account_info.get('currency', 'USD')}\n"
    text += f"\n🔢 Leverage: {account_info.get('leverage', 0)}:1"
    text += f"\n🖥️ Server: {account_info.get('server', 'N/A')}"
    
    return text

def format_positions(positions: list) -> str:
    """Format positions list"""
    if not positions:
        return BOT_TEXTS['no_positions']
    
    text = f"{BOT_TEXTS['positions']}\n\n"
    for pos in positions:
        type_emoji = '🟢' if pos['type'] == 'BUY' else '🔴'
        profit_emoji = '💚' if pos['profit'] >= 0 else '❤️'
        
        text += f"{type_emoji} {pos['symbol']} {pos['type']}\n"
        text += f"   🎫 Ticket: {pos['ticket']}\n"
        text += f"   📊 Volume: {pos['volume']}\n"
        text += f"   💰 Open Price: {pos['price_open']:.5f}\n"
        text += f"   📈 Current Price: {pos['price_current']:.5f}\n"
        text += f"   {profit_emoji} Profit/Loss: {pos['profit']:.2f}\n"
        if pos.get('sl'):
            text += f"   🛑 Stop Loss: {pos['sl']:.5f}\n"
        if pos.get('tp'):
            text += f"   🎯 Take Profit: {pos['tp']:.5f}\n"
        text += "\n"
    
    return text

def format_signal(signal: Dict, symbol: str) -> str:
    """Format trading signal"""
    action_emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '⚪'
    }
    
    action_text = {
        'BUY': BOT_TEXTS['buy'],
        'SELL': BOT_TEXTS['sell'],
        'HOLD': BOT_TEXTS['hold']
    }
    
    emoji = action_emoji.get(signal.get('action', 'HOLD'), '⚪')
    action = action_text.get(signal.get('action', 'HOLD'), BOT_TEXTS['hold'])
    
    text = f"{BOT_TEXTS['signal']} {symbol}\n\n"
    text += f"{emoji} {action}\n"
    text += f"📊 {BOT_TEXTS['confidence']}{signal.get('confidence', 0):.1f}%\n"
    text += f"💡 {BOT_TEXTS['reason']}{signal.get('reason', 'N/A')}\n"
    
    return text

def format_analysis(analysis: str, indicators: Dict) -> str:
    """Format AI analysis"""
    text = "🤖 AI Analysis:\n\n"
    text += analysis + "\n\n"
    text += "📊 Technical Indicators:\n"
    
    if indicators.get('rsi'):
        text += f"RSI: {indicators['rsi']:.2f}\n"
    if indicators.get('macd'):
        text += f"MACD: {indicators['macd']:.5f}\n"
    if indicators.get('sma_20'):
        text += f"SMA 20: {indicators['sma_20']:.5f}\n"
    
    return text

def check_authorization(allowed_username: str):
    """Decorator to check if user is authorized to use the bot"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Get user information
            user = update.effective_user
            if not user:
                await update.message.reply_text("❌ Unable to identify user.")
                return
            
            # Check username (case-insensitive, with or without @)
            user_username = (user.username or '').lower()
            allowed = allowed_username.lower().lstrip('@')
            
            if user_username != allowed:
                await update.message.reply_text("❌ Invalid user")
                logger.warning(f"Unauthorized access attempt by @{user.username} (ID: {user.id})")
                return
            
            # User is authorized, proceed with the command
            return await func(update, context)
        return wrapper
    return decorator

