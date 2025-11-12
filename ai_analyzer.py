"""
AI-powered Trading Analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-powered market analysis using OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators from price data"""
        try:
            if df is None or len(df) < 20:
                return {}
            
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean() if len(df) >= 50 else None
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Get latest values
            latest = df.iloc[-1]
            
            indicators = {
                'sma_20': float(latest['sma_20']) if pd.notna(latest['sma_20']) else None,
                'sma_50': float(latest['sma_50']) if pd.notna(latest.get('sma_50')) else None,
                'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
                'macd': float(latest['macd']) if pd.notna(latest['macd']) else None,
                'macd_signal': float(latest['macd_signal']) if pd.notna(latest['macd_signal']) else None,
                'bb_upper': float(latest['bb_upper']) if pd.notna(latest['bb_upper']) else None,
                'bb_lower': float(latest['bb_lower']) if pd.notna(latest['bb_lower']) else None,
                'bb_middle': float(latest['bb_middle']) if pd.notna(latest['bb_middle']) else None,
                'current_price': float(latest['close']),
            }
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def generate_ai_analysis(self, symbol: str, indicators: Dict, market_data: Dict) -> Optional[str]:
        """Generate AI-powered trading analysis using OpenAI"""
        if not self.client:
            return None
        
        try:
            prompt = f"""You are an expert forex trader analyzing {symbol}. 

Current Market Data:
- Current Price: {market_data.get('current_price', 'N/A')}
- Bid: {market_data.get('bid', 'N/A')}
- Ask: {market_data.get('ask', 'N/A')}
- Spread: {market_data.get('spread', 'N/A')}

Technical Indicators:
- RSI: {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- MACD Signal: {indicators.get('macd_signal', 'N/A')}
- SMA 20: {indicators.get('sma_20', 'N/A')}
- Bollinger Upper: {indicators.get('bb_upper', 'N/A')}
- Bollinger Lower: {indicators.get('bb_lower', 'N/A')}

Provide a concise trading analysis in Persian (Farsi) with:
1. Market sentiment (Bullish/Bearish/Neutral)
2. Key support and resistance levels
3. Trading recommendation (BUY/SELL/HOLD)
4. Risk assessment
5. Suggested stop loss and take profit levels

Keep the response under 200 words and professional."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert forex trading analyst. Provide analysis in Persian (Farsi)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return None
    
    def analyze_signal(self, indicators: Dict) -> Dict:
        """Generate trading signal based on technical indicators"""
        signal = {
            'action': 'HOLD',
            'confidence': 0,
            'reason': '',
        }
        
        try:
            rsi = indicators.get('rsi')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            current_price = indicators.get('current_price')
            bb_upper = indicators.get('bb_upper')
            bb_lower = indicators.get('bb_lower')
            sma_20 = indicators.get('sma_20')
            
            buy_signals = 0
            sell_signals = 0
            
            # RSI signals
            if rsi:
                if rsi < 30:
                    buy_signals += 2
                elif rsi < 40:
                    buy_signals += 1
                elif rsi > 70:
                    sell_signals += 2
                elif rsi > 60:
                    sell_signals += 1
            
            # MACD signals
            if macd and macd_signal:
                if macd > macd_signal:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # Bollinger Bands
            if current_price and bb_lower and bb_upper:
                if current_price <= bb_lower:
                    buy_signals += 1
                elif current_price >= bb_upper:
                    sell_signals += 1
            
            # SMA trend
            if current_price and sma_20:
                if current_price > sma_20:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # Determine signal
            total_signals = buy_signals + sell_signals
            if total_signals > 0:
                if buy_signals > sell_signals:
                    signal['action'] = 'BUY'
                    signal['confidence'] = min(90, (buy_signals / total_signals) * 100)
                    signal['reason'] = f'{buy_signals} buy signals vs {sell_signals} sell signals'
                elif sell_signals > buy_signals:
                    signal['action'] = 'SELL'
                    signal['confidence'] = min(90, (sell_signals / total_signals) * 100)
                    signal['reason'] = f'{sell_signals} sell signals vs {buy_signals} buy signals'
                else:
                    signal['action'] = 'HOLD'
                    signal['reason'] = 'Mixed signals'
            else:
                signal['reason'] = 'Insufficient data'
            
            return signal
        except Exception as e:
            logger.error(f"Error analyzing signal: {e}")
            return signal

