"""
Configuration management for SweetTrader Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # MetaTrader5 (for market data only)
    MT5_LOGIN = int(os.getenv('MT5_LOGIN', '0'))
    MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
    MT5_SERVER = os.getenv('MT5_SERVER', '')
    
    # OpenAI (for AI advice)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Authorization - comma-separated list of allowed usernames
    ALLOWED_USERNAMES = os.getenv('ALLOWED_USERNAMES', 'reyi_t,sweetamirmohamad').split(',')
    ALLOWED_USERNAMES = [u.strip().lower().lstrip('@') for u in ALLOWED_USERNAMES]
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return True
