"""
Signal Generator - Generates reliable trading signals
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Generates trading signals based on technical analysis"""
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        try:
            if df is None or len(df) < 20:
                return {}
            
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
            
            # Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean() if len(df) >= 50 else None
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            latest = df.iloc[-1]
            
            return {
                'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
                'macd': float(latest['macd']) if pd.notna(latest['macd']) else None,
                'macd_signal': float(latest['macd_signal']) if pd.notna(latest['macd_signal']) else None,
                'sma_20': float(latest['sma_20']) if pd.notna(latest['sma_20']) else None,
                'sma_50': float(latest['sma_50']) if pd.notna(latest.get('sma_50')) else None,
                'bb_upper': float(latest['bb_upper']) if pd.notna(latest['bb_upper']) else None,
                'bb_lower': float(latest['bb_lower']) if pd.notna(latest['bb_lower']) else None,
                'current_price': float(latest['close']),
            }
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def generate_signal(self, symbol: str, indicators: Dict, market_data: Dict) -> Optional[Dict]:
        """Generate trading signal based on indicators"""
        try:
            rsi = indicators.get('rsi')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            current_price = indicators.get('current_price')
            sma_20 = indicators.get('sma_20')
            bb_upper = indicators.get('bb_upper')
            bb_lower = indicators.get('bb_lower')
            
            if not all([rsi, macd, macd_signal, current_price, sma_20]):
                return None
            
            buy_signals = 0
            sell_signals = 0
            reasons = []
            
            # RSI Analysis
            if rsi < 30:
                buy_signals += 2
                reasons.append("RSI oversold (<30)")
            elif rsi < 40:
                buy_signals += 1
                reasons.append("RSI near oversold")
            elif rsi > 70:
                sell_signals += 2
                reasons.append("RSI overbought (>70)")
            elif rsi > 60:
                sell_signals += 1
                reasons.append("RSI near overbought")
            
            # MACD Analysis
            if macd > macd_signal:
                buy_signals += 1
                reasons.append("MACD bullish crossover")
            else:
                sell_signals += 1
                reasons.append("MACD bearish crossover")
            
            # Moving Average Analysis
            if current_price > sma_20:
                buy_signals += 1
                reasons.append("Price above SMA 20")
            else:
                sell_signals += 1
                reasons.append("Price below SMA 20")
            
            # Bollinger Bands
            if bb_upper and bb_lower:
                if current_price <= bb_lower:
                    buy_signals += 1
                    reasons.append("Price at lower Bollinger Band")
                elif current_price >= bb_upper:
                    sell_signals += 1
                    reasons.append("Price at upper Bollinger Band")
            
            # Determine signal
            total_signals = buy_signals + sell_signals
            if total_signals == 0:
                return None
            
            if buy_signals > sell_signals and buy_signals >= 3:
                confidence = min(95, (buy_signals / total_signals) * 100)
                return {
                    'symbol': symbol,
                    'action': 'BUY',
                    'confidence': round(confidence, 1),
                    'price': current_price,
                    'reasons': reasons[:3],  # Top 3 reasons
                    'stop_loss': round(current_price * 0.98, 5) if current_price else None,
                    'take_profit': round(current_price * 1.02, 5) if current_price else None,
                }
            elif sell_signals > buy_signals and sell_signals >= 3:
                confidence = min(95, (sell_signals / total_signals) * 100)
                return {
                    'symbol': symbol,
                    'action': 'SELL',
                    'confidence': round(confidence, 1),
                    'price': current_price,
                    'reasons': reasons[:3],  # Top 3 reasons
                    'stop_loss': round(current_price * 1.02, 5) if current_price else None,
                    'take_profit': round(current_price * 0.98, 5) if current_price else None,
                }
            
            return None  # No strong signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def format_signal_message(self, signal: Dict) -> str:
        """Format signal as a message"""
        action_emoji = '🟢' if signal['action'] == 'BUY' else '🔴'
        
        msg = f"{action_emoji} **TRADING SIGNAL** {action_emoji}\n\n"
        msg += f"📊 Symbol: {signal['symbol']}\n"
        msg += f"🎯 Action: {signal['action']}\n"
        msg += f"💰 Price: {signal['price']:.5f}\n"
        msg += f"📈 Confidence: {signal['confidence']}%\n\n"
        
        if signal.get('stop_loss'):
            msg += f"🛑 Stop Loss: {signal['stop_loss']:.5f}\n"
        if signal.get('take_profit'):
            msg += f"🎯 Take Profit: {signal['take_profit']:.5f}\n"
        
        msg += "\n📋 Reasons:\n"
        for reason in signal.get('reasons', []):
            msg += f"• {reason}\n"
        
        msg += "\n⚠️ Always use proper risk management!"
        
        return msg

