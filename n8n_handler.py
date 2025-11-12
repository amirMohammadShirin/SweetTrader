"""
N8N Integration Handler for AI Workflows
"""
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class N8NHandler:
    """Handle N8N webhook interactions for AI analysis"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_analysis_request(self, symbol: str, timeframe: str = 'H1', 
                            market_data: Optional[Dict] = None) -> Optional[Dict]:
        """Send market data to N8N for AI analysis"""
        try:
            payload = {
                'symbol': symbol,
                'timeframe': timeframe,
                'market_data': market_data or {},
                'timestamp': str(datetime.now().isoformat()),
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"N8N request failed with status {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending request to N8N: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in N8N handler: {e}")
            return None
    
    def get_trading_signal(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Get AI trading signal from N8N"""
        try:
            payload = {
                'action': 'get_signal',
                'symbol': symbol,
                'market_data': market_data,
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"N8N signal request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting trading signal: {e}")
            return None
    
    def send_trade_result(self, trade_data: Dict) -> bool:
        """Send trade result back to N8N for learning"""
        try:
            payload = {
                'action': 'trade_result',
                'trade_data': trade_data,
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending trade result to N8N: {e}")
            return False

