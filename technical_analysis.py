import pandas as pd
import numpy as np
import ta
from config import Config

class TechnicalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_rsi(self, data, period=None):
        """Calculate RSI (Relative Strength Index)"""
        if period is None:
            period = Config.RSI_PERIOD
            
        if len(data) < period:
            return None
            
        rsi = ta.momentum.RSIIndicator(data['Close'], window=period).rsi()
        return rsi
    
    def calculate_macd(self, data, fast=None, slow=None, signal=None):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if fast is None:
            fast = Config.MACD_FAST
        if slow is None:
            slow = Config.MACD_SLOW
        if signal is None:
            signal = Config.MACD_SIGNAL
            
        if len(data) < slow:
            return None, None, None
            
        macd_indicator = ta.trend.MACD(data['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
        
        macd = macd_indicator.macd()
        macd_signal = macd_indicator.macd_signal()
        macd_histogram = macd_indicator.macd_diff()
        
        return macd, macd_signal, macd_histogram
    
    def calculate_moving_average(self, data, period=None):
        """Calculate Simple Moving Average"""
        if period is None:
            period = Config.MA_PERIOD
            
        if len(data) < period:
            return None
            
        ma = ta.trend.SMAIndicator(data['Close'], window=period).sma_indicator()
        return ma
    
    def calculate_bollinger_bands(self, data, period=None, std_dev=None):
        """Calculate Bollinger Bands"""
        if period is None:
            period = Config.BOLLINGER_PERIOD
        if std_dev is None:
            std_dev = Config.BOLLINGER_STD
            
        if len(data) < period:
            return None, None, None
            
        bb_indicator = ta.volatility.BollingerBands(data['Close'], window=period, window_dev=std_dev)
        
        bb_upper = bb_indicator.bollinger_hband()
        bb_middle = bb_indicator.bollinger_mavg()
        bb_lower = bb_indicator.bollinger_lband()
        
        return bb_upper, bb_middle, bb_lower
    
    def calculate_stochastic(self, data, k_period=None, d_period=None):
        """Calculate Stochastic Oscillator"""
        if k_period is None:
            k_period = Config.STOCH_K
        if d_period is None:
            d_period = Config.STOCH_D
            
        if len(data) < k_period:
            return None, None
            
        stoch_indicator = ta.momentum.StochasticOscillator(
            data['High'], data['Low'], data['Close'], 
            window=k_period, smooth_window=d_period
        )
        
        stoch_k = stoch_indicator.stoch()
        stoch_d = stoch_indicator.stoch_signal()
        
        return stoch_k, stoch_d
    
    def get_all_indicators(self, data):
        """Calculate all technical indicators for the given data"""
        if data is None or len(data) < 50:  # Need sufficient data
            return None
            
        indicators = {}
        
        # RSI
        rsi = self.calculate_rsi(data)
        if rsi is not None:
            indicators['rsi'] = rsi.iloc[-1] if not rsi.empty else None
            indicators['rsi_series'] = rsi
        
        # MACD
        macd, macd_signal, macd_hist = self.calculate_macd(data)
        if macd is not None:
            indicators['macd'] = macd.iloc[-1] if not macd.empty else None
            indicators['macd_signal'] = macd_signal.iloc[-1] if not macd_signal.empty else None
            indicators['macd_histogram'] = macd_hist.iloc[-1] if not macd_hist.empty else None
            indicators['macd_series'] = macd
            indicators['macd_signal_series'] = macd_signal
            indicators['macd_histogram_series'] = macd_hist
        
        # Moving Average
        ma = self.calculate_moving_average(data)
        if ma is not None:
            indicators['ma'] = ma.iloc[-1] if not ma.empty else None
            indicators['ma_series'] = ma
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(data)
        if bb_upper is not None:
            indicators['bb_upper'] = bb_upper.iloc[-1] if not bb_upper.empty else None
            indicators['bb_middle'] = bb_middle.iloc[-1] if not bb_middle.empty else None
            indicators['bb_lower'] = bb_lower.iloc[-1] if not bb_lower.empty else None
            indicators['bb_upper_series'] = bb_upper
            indicators['bb_middle_series'] = bb_middle
            indicators['bb_lower_series'] = bb_lower
        
        # Stochastic
        stoch_k, stoch_d = self.calculate_stochastic(data)
        if stoch_k is not None:
            indicators['stoch_k'] = stoch_k.iloc[-1] if not stoch_k.empty else None
            indicators['stoch_d'] = stoch_d.iloc[-1] if not stoch_d.empty else None
            indicators['stoch_k_series'] = stoch_k
            indicators['stoch_d_series'] = stoch_d
        
        # Current price
        indicators['current_price'] = data['Close'].iloc[-1]
        indicators['high'] = data['High'].iloc[-1]
        indicators['low'] = data['Low'].iloc[-1]
        indicators['volume'] = data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
        
        return indicators
    
    def get_trend_direction(self, data_m5, data_m15):
        """Determine overall trend direction using both timeframes"""
        indicators_m5 = self.get_all_indicators(data_m5)
        indicators_m15 = self.get_all_indicators(data_m15)
        
        if not indicators_m5 or not indicators_m15:
            return None
            
        # Trend signals
        trend_signals = []
        
        # MA trend (M15 for confirmation)
        if indicators_m15.get('ma') and indicators_m15.get('current_price'):
            if indicators_m15['current_price'] > indicators_m15['ma']:
                trend_signals.append('bullish')
            else:
                trend_signals.append('bearish')
        
        # MACD trend (M5)
        if (indicators_m5.get('macd') is not None and 
            indicators_m5.get('macd_signal') is not None):
            if indicators_m5['macd'] > indicators_m5['macd_signal']:
                trend_signals.append('bullish')
            else:
                trend_signals.append('bearish')
        
        # Bollinger Bands position (M5)
        if (indicators_m5.get('current_price') and 
            indicators_m5.get('bb_upper') and 
            indicators_m5.get('bb_lower')):
            bb_position = (indicators_m5['current_price'] - indicators_m5['bb_lower']) / (indicators_m5['bb_upper'] - indicators_m5['bb_lower'])
            if bb_position > 0.7:
                trend_signals.append('bullish')
            elif bb_position < 0.3:
                trend_signals.append('bearish')
        
        # Count signals
        bullish_count = trend_signals.count('bullish')
        bearish_count = trend_signals.count('bearish')
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'neutral'
    
    def calculate_signal_strength(self, indicators_m5, indicators_m15, trend):
        """Calculate signal strength/confidence"""
        if not indicators_m5 or not indicators_m15:
            return 0.0
            
        strength_factors = []
        
        # RSI confirmation
        if indicators_m5.get('rsi') is not None:
            rsi = indicators_m5['rsi']
            if trend == 'bullish' and rsi < 70:  # Not overbought
                strength_factors.append(0.2)
            elif trend == 'bearish' and rsi > 30:  # Not oversold
                strength_factors.append(0.2)
        
        # MACD momentum
        if (indicators_m5.get('macd_histogram') is not None and 
            len(indicators_m5.get('macd_histogram_series', [])) > 1):
            current_hist = indicators_m5['macd_histogram']
            prev_hist = indicators_m5['macd_histogram_series'].iloc[-2]
            
            if trend == 'bullish' and current_hist > prev_hist > 0:
                strength_factors.append(0.25)
            elif trend == 'bearish' and current_hist < prev_hist < 0:
                strength_factors.append(0.25)
        
        # Stochastic confirmation
        if (indicators_m5.get('stoch_k') is not None and 
            indicators_m5.get('stoch_d') is not None):
            stoch_k = indicators_m5['stoch_k']
            stoch_d = indicators_m5['stoch_d']
            
            if trend == 'bullish' and stoch_k > stoch_d and stoch_k < 80:
                strength_factors.append(0.2)
            elif trend == 'bearish' and stoch_k < stoch_d and stoch_k > 20:
                strength_factors.append(0.2)
        
        # Timeframe confluence
        m5_trend = 'bullish' if indicators_m5.get('current_price', 0) > indicators_m5.get('ma', 0) else 'bearish'
        m15_trend = 'bullish' if indicators_m15.get('current_price', 0) > indicators_m15.get('ma', 0) else 'bearish'
        
        if m5_trend == m15_trend == trend:
            strength_factors.append(0.35)
        
        return min(sum(strength_factors), 1.0)  # Cap at 1.0