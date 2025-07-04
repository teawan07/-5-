import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import Config
from technical_analysis import TechnicalAnalyzer
from data_fetcher import create_data_fetcher

class TradingSignal:
    def __init__(self, pair, signal_type, entry_price, tp_price, sl_price, confidence, timestamp, reason):
        self.pair = pair
        self.signal_type = signal_type  # 'BUY' or 'SELL'
        self.entry_price = entry_price
        self.tp_price = tp_price
        self.sl_price = sl_price
        self.confidence = confidence
        self.timestamp = timestamp
        self.reason = reason
        self.status = 'active'  # active, hit_tp, hit_sl, expired
        
    def to_dict(self):
        return {
            'pair': self.pair,
            'signal_type': self.signal_type,
            'entry_price': self.entry_price,
            'tp_price': self.tp_price,
            'sl_price': self.sl_price,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'status': self.status
        }
    
    def format_telegram_message(self):
        """Format signal for Telegram message"""
        signal_emoji = "✅" if self.signal_type == "BUY" else "🔴"
        time_str = self.timestamp.strftime("%H:%M (GMT+7)")
        
        message = f"""📡 Forex Signal
Pair: {self.pair}
Signal: {signal_emoji} {self.signal_type}
Entry: {self.entry_price:.5f}
TP: {self.tp_price:.5f}
SL: {self.sl_price:.5f}
Confidence: {self.confidence:.0%}
⏰ Time: {time_str}
Reason: {self.reason}"""
        
        return message

class SignalGenerator:
    def __init__(self):
        self.data_fetcher = create_data_fetcher(Config.DATA_SOURCE)
        self.technical_analyzer = TechnicalAnalyzer()
        self.active_signals = []
        self.signal_history = []
        
    def start(self):
        """Start the data fetcher"""
        self.data_fetcher.start_real_time_updates()
        
    def stop(self):
        """Stop the data fetcher"""
        self.data_fetcher.stop_real_time_updates()
        
    def calculate_tp_sl_levels(self, pair, entry_price, signal_type, volatility):
        """Calculate Take Profit and Stop Loss levels"""
        # Get volatility-based points
        base_points = volatility * 10000  # Convert to points (for 4-digit pairs)
        
        # Ensure minimum and maximum points
        points = max(Config.MIN_TP_SL_POINTS, min(base_points, Config.MAX_TP_SL_POINTS))
        
        # Convert points to price difference
        if 'JPY' in pair:
            # JPY pairs are 3-digit (e.g., USD/JPY = 150.25)
            point_value = 0.01
        else:
            # Other pairs are 5-digit (e.g., EUR/USD = 1.08500)
            point_value = 0.0001
            
        price_diff = points * point_value
        
        if signal_type == 'BUY':
            tp_price = entry_price + price_diff
            sl_price = entry_price - price_diff * 0.8  # Slightly tighter SL
        else:  # SELL
            tp_price = entry_price - price_diff
            sl_price = entry_price + price_diff * 0.8
            
        return tp_price, sl_price
    
    def analyze_pair(self, pair):
        """Analyze a single currency pair for trading signals"""
        try:
            # Get historical data for both timeframes
            data_m5 = self.data_fetcher.get_historical_data(pair, timeframe='5m', period='2d')
            data_m15 = self.data_fetcher.get_historical_data(pair, timeframe='15m', period='5d')
            
            if data_m5 is None or data_m15 is None:
                return None
                
            if len(data_m5) < 50 or len(data_m15) < 50:
                return None
                
            # Calculate technical indicators
            indicators_m5 = self.technical_analyzer.get_all_indicators(data_m5)
            indicators_m15 = self.technical_analyzer.get_all_indicators(data_m15)
            
            if not indicators_m5 or not indicators_m15:
                return None
                
            # Get trend direction
            trend = self.technical_analyzer.get_trend_direction(data_m5, data_m15)
            if trend is None or trend == 'neutral':
                return None
                
            # Calculate signal strength
            confidence = self.technical_analyzer.calculate_signal_strength(
                indicators_m5, indicators_m15, trend
            )
            
            # Check if confidence meets minimum threshold
            if confidence < Config.MIN_CONFIDENCE:
                return None
                
            # Generate signal based on specific entry conditions
            signal = self._check_entry_conditions(
                pair, indicators_m5, indicators_m15, trend, confidence
            )
            
            return signal
            
        except Exception as e:
            print(f"Error analyzing pair {pair}: {e}")
            return None
    
    def _check_entry_conditions(self, pair, indicators_m5, indicators_m15, trend, confidence):
        """Check specific entry conditions for generating signals"""
        current_price = indicators_m5.get('current_price')
        if not current_price:
            return None
            
        entry_conditions = []
        reasons = []
        
        # RSI Entry Conditions
        rsi = indicators_m5.get('rsi')
        if rsi is not None:
            if trend == 'bullish' and 30 < rsi < 60:  # RSI recovering from oversold
                entry_conditions.append(True)
                reasons.append("RSI bullish divergence")
            elif trend == 'bearish' and 40 < rsi < 70:  # RSI falling from overbought
                entry_conditions.append(True)
                reasons.append("RSI bearish divergence")
            else:
                entry_conditions.append(False)
        
        # MACD Entry Conditions
        macd = indicators_m5.get('macd')
        macd_signal = indicators_m5.get('macd_signal')
        macd_hist = indicators_m5.get('macd_histogram')
        
        if macd is not None and macd_signal is not None and macd_hist is not None:
            if trend == 'bullish' and macd > macd_signal and macd_hist > 0:
                entry_conditions.append(True)
                reasons.append("MACD bullish crossover")
            elif trend == 'bearish' and macd < macd_signal and macd_hist < 0:
                entry_conditions.append(True)
                reasons.append("MACD bearish crossover")
            else:
                entry_conditions.append(False)
        
        # Bollinger Bands Entry Conditions
        bb_upper = indicators_m5.get('bb_upper')
        bb_lower = indicators_m5.get('bb_lower')
        bb_middle = indicators_m5.get('bb_middle')
        
        if bb_upper and bb_lower and bb_middle:
            if trend == 'bullish' and current_price > bb_middle and current_price < bb_upper:
                entry_conditions.append(True)
                reasons.append("Price above BB middle")
            elif trend == 'bearish' and current_price < bb_middle and current_price > bb_lower:
                entry_conditions.append(True)
                reasons.append("Price below BB middle")
            else:
                entry_conditions.append(False)
        
        # Stochastic Entry Conditions
        stoch_k = indicators_m5.get('stoch_k')
        stoch_d = indicators_m5.get('stoch_d')
        
        if stoch_k is not None and stoch_d is not None:
            if trend == 'bullish' and stoch_k > stoch_d and stoch_k < 80:
                entry_conditions.append(True)
                reasons.append("Stoch bullish momentum")
            elif trend == 'bearish' and stoch_k < stoch_d and stoch_k > 20:
                entry_conditions.append(True)
                reasons.append("Stoch bearish momentum")
            else:
                entry_conditions.append(False)
        
        # Check if majority of conditions are met
        valid_conditions = sum(entry_conditions)
        total_conditions = len(entry_conditions)
        
        if valid_conditions < total_conditions * 0.7:  # At least 70% of conditions
            return None
            
        # Check for recent signals to avoid duplicates
        if self._has_recent_signal(pair, hours=1):
            return None
            
        # Generate signal
        signal_type = 'BUY' if trend == 'bullish' else 'SELL'
        
        # Calculate TP/SL levels
        volatility = self.data_fetcher.get_volatility(pair)
        tp_price, sl_price = self.calculate_tp_sl_levels(
            pair, current_price, signal_type, volatility
        )
        
        # Create signal
        signal = TradingSignal(
            pair=pair,
            signal_type=signal_type,
            entry_price=current_price,
            tp_price=tp_price,
            sl_price=sl_price,
            confidence=confidence,
            timestamp=Config.get_current_time(),
            reason=", ".join(reasons[:3])  # Limit reasons
        )
        
        return signal
    
    def _has_recent_signal(self, pair, hours=1):
        """Check if there's a recent signal for the same pair"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for signal in self.active_signals:
            if signal.pair == pair and signal.timestamp > cutoff_time:
                return True
                
        return False
    
    def scan_all_pairs(self):
        """Scan all configured currency pairs for signals"""
        new_signals = []
        
        if not self.data_fetcher.is_market_open():
            print("Market is closed. Skipping scan.")
            return new_signals
            
        print(f"Scanning {len(Config.CURRENCY_PAIRS)} currency pairs...")
        
        for pair in Config.CURRENCY_PAIRS:
            try:
                signal = self.analyze_pair(pair)
                if signal:
                    new_signals.append(signal)
                    self.active_signals.append(signal)
                    self.signal_history.append(signal)
                    print(f"Generated signal: {pair} {signal.signal_type} @ {signal.entry_price:.5f}")
                    
            except Exception as e:
                print(f"Error scanning pair {pair}: {e}")
                
        print(f"Scan complete. Generated {len(new_signals)} new signals.")
        return new_signals
    
    def update_signal_status(self):
        """Update status of active signals based on current prices"""
        current_prices = self.data_fetcher.get_all_current_prices()
        
        for signal in self.active_signals[:]:  # Copy list to modify during iteration
            if signal.status != 'active':
                continue
                
            current_price_data = current_prices.get(signal.pair)
            if not current_price_data:
                continue
                
            current_price = current_price_data.get('price')
            if not current_price:
                continue
                
            # Check TP/SL hits
            if signal.signal_type == 'BUY':
                if current_price >= signal.tp_price:
                    signal.status = 'hit_tp'
                    print(f"Signal {signal.pair} {signal.signal_type} hit TP!")
                elif current_price <= signal.sl_price:
                    signal.status = 'hit_sl'
                    print(f"Signal {signal.pair} {signal.signal_type} hit SL!")
            else:  # SELL
                if current_price <= signal.tp_price:
                    signal.status = 'hit_tp'
                    print(f"Signal {signal.pair} {signal.signal_type} hit TP!")
                elif current_price >= signal.sl_price:
                    signal.status = 'hit_sl'
                    print(f"Signal {signal.pair} {signal.signal_type} hit SL!")
                    
            # Remove from active signals if completed
            if signal.status in ['hit_tp', 'hit_sl']:
                self.active_signals.remove(signal)
    
    def get_active_signals(self):
        """Get all active signals"""
        return [signal.to_dict() for signal in self.active_signals]
    
    def get_signal_history(self, limit=50):
        """Get signal history"""
        return [signal.to_dict() for signal in self.signal_history[-limit:]]