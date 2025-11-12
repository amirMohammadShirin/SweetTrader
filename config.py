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
    
    # MetaTrader5
    MT5_LOGIN = int(os.getenv('MT5_LOGIN', '0'))
    MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
    MT5_SERVER = os.getenv('MT5_SERVER', '')
    
    # N8N
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Admin
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))
    
    # Authorization
    ALLOWED_USERNAME = os.getenv('ALLOWED_USERNAME', 'reyi_t')  # Default to reyi_t
    
    # Trading Settings
    DEFAULT_SYMBOL = 'EURUSD'
    DEFAULT_VOLUME = 0.01
    DEFAULT_SLIPPAGE = 3
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'MT5_LOGIN': cls.MT5_LOGIN,
            'MT5_PASSWORD': cls.MT5_PASSWORD,
            'MT5_SERVER': cls.MT5_SERVER,
        }
        
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

