"""
MetaTrader5 Integration Handler - Read-only for market data
"""
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

import pandas as pd
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class MT5Handler:
    """Handle MetaTrader5 operations for market data only"""
    
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MetaTrader5"""
        if not MT5_AVAILABLE:
            logger.warning("MetaTrader5 package not available (typically only on Windows)")
            return False
        
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            if not authorized:
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            self.connected = True
            account_info = mt5.account_info()
            logger.info(f"Connected to MT5. Account: {account_info.login}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MetaTrader5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.connected:
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return {
                'login': account_info.login,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit,
                'currency': account_info.currency,
                'server': account_info.server,
                'leverage': account_info.leverage,
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.connected:
            return None
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None
            
            return {
                'name': symbol_info.name,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'spread': symbol_info.spread,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
            }
        except Exception as e:
            logger.error(f"Error getting symbol info: {e}")
            return None
    
    def get_rates(self, symbol: str, timeframe=None, count: int = 100) -> Optional[pd.DataFrame]:
        """Get historical rates"""
        if not self.connected or not MT5_AVAILABLE:
            return None
        
        if timeframe is None and MT5_AVAILABLE:
            timeframe = mt5.TIMEFRAME_H1
        elif timeframe is None:
            return None
        
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            logger.error(f"Error getting rates: {e}")
            return None
