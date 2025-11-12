"""
Utility functions for SweetTrader Bot
"""
from typing import Dict, Callable
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def check_authorization(allowed_username: str):
    """Decorator to check if user is authorized to use the bot"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            if not user:
                await update.message.reply_text("❌ Unable to identify user.")
                return
            
            user_username = (user.username or '').lower()
            allowed = allowed_username.lower().lstrip('@')
            
            if user_username != allowed:
                await update.message.reply_text("❌ Invalid user")
                logger.warning(f"Unauthorized access attempt by @{user.username} (ID: {user.id})")
                return
            
            return await func(update, context)
        return wrapper
    return decorator
