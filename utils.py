"""
Utility functions for SweetTrader Bot
"""
from typing import Dict, Callable
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def check_authorization(allowed_usernames: list):
    """Decorator to check if user is authorized to use the bot"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            if not user:
                await update.message.reply_text("❌ Unable to identify user.")
                return
            
            user_username = (user.username or '').lower()
            
            if user_username not in allowed_usernames:
                await update.message.reply_text("❌ Invalid user")
                logger.warning(f"Unauthorized access attempt by @{user.username} (ID: {user.id})")
                return
            
            return await func(update, context)
        return wrapper
    return decorator
