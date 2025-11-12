"""
Utility functions for SweetTrader Bot
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Persian translations
PERSIAN_TEXTS = {
    'welcome': 'خوش آمدید به ربات معاملاتی SweetTrader! 🚀\n\nاین ربات به شما کمک می‌کند تا معاملات بهتری انجام دهید.',
    'help': '''📖 راهنمای استفاده از ربات:

/start - شروع ربات
/account - اطلاعات حساب
/balance - موجودی حساب
/positions - موقعیت‌های باز
/analyze <SYMBOL> - تحلیل نماد (مثال: /analyze EURUSD)
/signal <SYMBOL> - دریافت سیگنال معاملاتی
/buy <SYMBOL> <VOLUME> - خرید (مثال: /buy EURUSD 0.01)
/sell <SYMBOL> <VOLUME> - فروش
/close <TICKET> - بستن موقعیت
/help - نمایش این راهنما

💡 نکته: تمام دستورات را به انگلیسی وارد کنید.''',
    'not_connected': '❌ اتصال به MetaTrader5 برقرار نشده است.',
    'error': '❌ خطا: ',
    'success': '✅ موفق: ',
    'account_info': '📊 اطلاعات حساب:',
    'balance': '💰 موجودی: ',
    'equity': '💵 سرمایه: ',
    'margin': '📈 مارجین: ',
    'free_margin': '💳 مارجین آزاد: ',
    'profit': '💸 سود/زیان: ',
    'no_positions': '📭 موقعیت باز وجود ندارد.',
    'positions': '📋 موقعیت‌های باز:',
    'analyzing': '🔍 در حال تحلیل...',
    'signal': '📡 سیگنال معاملاتی:',
    'buy': '🟢 خرید',
    'sell': '🔴 فروش',
    'hold': '⚪ نگه‌داری',
    'confidence': 'اعتماد: ',
    'reason': 'دلیل: ',
}

def format_account_info(account_info: Dict) -> str:
    """Format account information in Persian"""
    if not account_info:
        return PERSIAN_TEXTS['not_connected']
    
    text = f"{PERSIAN_TEXTS['account_info']}\n\n"
    text += f"{PERSIAN_TEXTS['balance']}{account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{PERSIAN_TEXTS['equity']}{account_info.get('equity', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{PERSIAN_TEXTS['margin']}{account_info.get('margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
    text += f"{PERSIAN_TEXTS['free_margin']}{account_info.get('free_margin', 0):.2f} {account_info.get('currency', 'USD')}\n"
    
    profit = account_info.get('profit', 0)
    profit_emoji = '💚' if profit >= 0 else '❤️'
    text += f"{PERSIAN_TEXTS['profit']}{profit_emoji} {profit:.2f} {account_info.get('currency', 'USD')}\n"
    text += f"\n🔢 اهرم: {account_info.get('leverage', 0)}:1"
    text += f"\n🖥️ سرور: {account_info.get('server', 'N/A')}"
    
    return text

def format_positions(positions: list) -> str:
    """Format positions list in Persian"""
    if not positions:
        return PERSIAN_TEXTS['no_positions']
    
    text = f"{PERSIAN_TEXTS['positions']}\n\n"
    for pos in positions:
        type_emoji = '🟢' if pos['type'] == 'BUY' else '🔴'
        profit_emoji = '💚' if pos['profit'] >= 0 else '❤️'
        
        text += f"{type_emoji} {pos['symbol']} {pos['type']}\n"
        text += f"   🎫 تیکت: {pos['ticket']}\n"
        text += f"   📊 حجم: {pos['volume']}\n"
        text += f"   💰 قیمت باز: {pos['price_open']:.5f}\n"
        text += f"   📈 قیمت فعلی: {pos['price_current']:.5f}\n"
        text += f"   {profit_emoji} سود/زیان: {pos['profit']:.2f}\n"
        if pos.get('sl'):
            text += f"   🛑 Stop Loss: {pos['sl']:.5f}\n"
        if pos.get('tp'):
            text += f"   🎯 Take Profit: {pos['tp']:.5f}\n"
        text += "\n"
    
    return text

def format_signal(signal: Dict, symbol: str) -> str:
    """Format trading signal in Persian"""
    action_emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '⚪'
    }
    
    action_text = {
        'BUY': PERSIAN_TEXTS['buy'],
        'SELL': PERSIAN_TEXTS['sell'],
        'HOLD': PERSIAN_TEXTS['hold']
    }
    
    emoji = action_emoji.get(signal.get('action', 'HOLD'), '⚪')
    action = action_text.get(signal.get('action', 'HOLD'), PERSIAN_TEXTS['hold'])
    
    text = f"{PERSIAN_TEXTS['signal']} {symbol}\n\n"
    text += f"{emoji} {action}\n"
    text += f"📊 {PERSIAN_TEXTS['confidence']}{signal.get('confidence', 0):.1f}%\n"
    text += f"💡 {PERSIAN_TEXTS['reason']}{signal.get('reason', 'N/A')}\n"
    
    return text

def format_analysis(analysis: str, indicators: Dict) -> str:
    """Format AI analysis in Persian"""
    text = "🤖 تحلیل هوش مصنوعی:\n\n"
    text += analysis + "\n\n"
    text += "📊 شاخص‌های فنی:\n"
    
    if indicators.get('rsi'):
        text += f"RSI: {indicators['rsi']:.2f}\n"
    if indicators.get('macd'):
        text += f"MACD: {indicators['macd']:.5f}\n"
    if indicators.get('sma_20'):
        text += f"SMA 20: {indicators['sma_20']:.5f}\n"
    
    return text

