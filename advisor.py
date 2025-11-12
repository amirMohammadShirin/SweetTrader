"""
Trading Advisor - Provides technical, planning, and financial advice
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class TradingAdvisor:
    """Provides comprehensive trading advice"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
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
    
    def get_technical_advice(self, symbol: str, indicators: Dict, market_data: Dict) -> str:
        """Get technical trading advice"""
        advice = f"📊 Technical Analysis for {symbol}\n\n"
        
        rsi = indicators.get('rsi')
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        current_price = indicators.get('current_price')
        sma_20 = indicators.get('sma_20')
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        
        # RSI Analysis
        if rsi:
            advice += f"📈 RSI: {rsi:.2f}\n"
            if rsi > 70:
                advice += "⚠️ Overbought - Consider selling or waiting for pullback\n"
            elif rsi < 30:
                advice += "✅ Oversold - Potential buying opportunity\n"
            elif 30 <= rsi <= 70:
                advice += "➡️ Neutral zone - Wait for clearer signals\n"
        
        # MACD Analysis
        if macd and macd_signal:
            advice += f"\n📊 MACD: {macd:.5f}\n"
            if macd > macd_signal:
                advice += "🟢 Bullish momentum - Uptrend likely\n"
            else:
                advice += "🔴 Bearish momentum - Downtrend likely\n"
        
        # Moving Average Analysis
        if sma_20 and current_price:
            advice += f"\n📉 SMA 20: {sma_20:.5f}\n"
            if current_price > sma_20:
                advice += "✅ Price above SMA 20 - Bullish trend\n"
            else:
                advice += "⚠️ Price below SMA 20 - Bearish trend\n"
        
        # Bollinger Bands
        if bb_upper and bb_lower and current_price:
            advice += f"\n📊 Bollinger Bands:\n"
            advice += f"Upper: {bb_upper:.5f}\n"
            advice += f"Lower: {bb_lower:.5f}\n"
            if current_price >= bb_upper:
                advice += "⚠️ Price at upper band - Possible reversal down\n"
            elif current_price <= bb_lower:
                advice += "✅ Price at lower band - Possible reversal up\n"
            else:
                advice += "➡️ Price in middle range - Normal volatility\n"
        
        return advice
    
    def get_planning_advice(self, account_info: Dict) -> str:
        """Get trading planning advice"""
        advice = "📋 Trading Plan Advice\n\n"
        
        balance = account_info.get('balance', 0)
        equity = account_info.get('equity', 0)
        margin = account_info.get('margin', 0)
        free_margin = account_info.get('free_margin', 0)
        margin_level = account_info.get('margin_level', 0)
        leverage = account_info.get('leverage', 0)
        profit = account_info.get('profit', 0)
        
        # Risk Management
        advice += "💰 Risk Management:\n"
        advice += f"• Never risk more than 1-2% per trade\n"
        advice += f"• Current balance: {balance:.2f}\n"
        advice += f"• Maximum risk per trade: {balance * 0.02:.2f}\n\n"
        
        # Margin Advice
        if margin_level:
            advice += f"📊 Margin Level: {margin_level:.2f}%\n"
            if margin_level < 100:
                advice += "🚨 CRITICAL: Margin level below 100% - Close positions immediately!\n"
            elif margin_level < 150:
                advice += "⚠️ WARNING: Low margin level - Consider reducing positions\n"
            elif margin_level < 200:
                advice += "⚠️ CAUTION: Monitor margin closely\n"
            else:
                advice += "✅ Healthy margin level\n"
        
        # Leverage Advice
        if leverage:
            advice += f"\n⚖️ Leverage: {leverage}:1\n"
            if leverage > 100:
                advice += "⚠️ High leverage - Use with extreme caution\n"
            elif leverage > 50:
                advice += "⚠️ Moderate leverage - Manage risk carefully\n"
            else:
                advice += "✅ Reasonable leverage level\n"
        
        # Position Sizing
        advice += "\n📏 Position Sizing:\n"
        advice += f"• Free margin: {free_margin:.2f}\n"
        if free_margin > 0:
            advice += f"• Suggested max position size: {free_margin * 0.1:.2f}\n"
        advice += "• Use stop losses on all trades\n"
        advice += "• Never risk more than you can afford to lose\n"
        
        return advice
    
    def get_financial_advice(self, account_info: Dict) -> str:
        """Get financial management advice"""
        advice = "💵 Financial Management Advice\n\n"
        
        balance = account_info.get('balance', 0)
        equity = account_info.get('equity', 0)
        profit = account_info.get('profit', 0)
        margin = account_info.get('margin', 0)
        
        # Account Health
        advice += "🏥 Account Health:\n"
        if equity < balance:
            drawdown = ((balance - equity) / balance) * 100
            advice += f"• Current drawdown: {drawdown:.2f}%\n"
            if drawdown > 20:
                advice += "🚨 High drawdown - Consider reducing risk\n"
            elif drawdown > 10:
                advice += "⚠️ Moderate drawdown - Review your strategy\n"
        
        # Profit/Loss
        if profit != 0:
            advice += f"\n📊 Current P/L: {profit:.2f}\n"
            if profit > 0:
                advice += "✅ In profit - Consider taking some profits\n"
            else:
                advice += "⚠️ In loss - Review your positions\n"
        
        # Capital Management
        advice += "\n💼 Capital Management:\n"
        advice += "• Never trade with money you need for living expenses\n"
        advice += "• Keep 3-6 months of expenses in savings\n"
        advice += "• Only trade with disposable income\n"
        advice += "• Diversify your investments\n"
        advice += "• Set aside profits regularly\n"
        
        # Trading Psychology
        advice += "\n🧠 Trading Psychology:\n"
        advice += "• Stick to your trading plan\n"
        advice += "• Don't let emotions drive decisions\n"
        advice += "• Take breaks after losses\n"
        advice += "• Keep a trading journal\n"
        advice += "• Learn from mistakes\n"
        
        return advice
    
    def get_ai_advice(self, symbol: str, indicators: Dict, market_data: Dict, account_info: Dict) -> Optional[str]:
        """Get AI-powered comprehensive advice"""
        if not self.client:
            return None
        
        try:
            prompt = f"""You are an expert forex trading advisor. Provide comprehensive trading advice for {symbol}.

Current Market Data:
- Price: {market_data.get('current_price', 'N/A')}
- Bid: {market_data.get('bid', 'N/A')}
- Ask: {market_data.get('ask', 'N/A')}
- Spread: {market_data.get('spread', 'N/A')}

Technical Indicators:
- RSI: {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- SMA 20: {indicators.get('sma_20', 'N/A')}

Account Status:
- Balance: {account_info.get('balance', 'N/A')}
- Equity: {account_info.get('equity', 'N/A')}
- Margin Level: {account_info.get('margin_level', 'N/A')}%

Provide:
1. Technical analysis and trading signal
2. Risk management recommendations
3. Position sizing advice
4. Entry/exit suggestions
5. Stop loss and take profit levels

Keep response concise, professional, and actionable (under 300 words)."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert forex trading advisor. Provide clear, actionable trading advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting AI advice: {e}")
            return None

