import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
from config import Config
import requests
import json

class ForexDataFetcher:
    def __init__(self):
        self.current_prices = {}
        self.historical_data = {}
        self.running = False
        self.update_thread = None
        
    def start_real_time_updates(self):
        """Start real-time price updates"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def stop_real_time_updates(self):
        """Stop real-time price updates"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
            
    def _update_loop(self):
        """Main update loop for real-time data"""
        while self.running:
            try:
                self._fetch_current_prices()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(60)  # Wait longer on error
                
    def _convert_pair_to_yfinance(self, pair):
        """Convert currency pair format for yfinance"""
        # Convert EURUSD to EURUSD=X format
        return f"{pair}=X"
    
    def _fetch_current_prices(self):
        """Fetch current prices for all currency pairs"""
        for pair in Config.CURRENCY_PAIRS:
            try:
                yf_symbol = self._convert_pair_to_yfinance(pair)
                ticker = yf.Ticker(yf_symbol)
                
                # Get current price
                info = ticker.info
                current_price = info.get('regularMarketPrice', None)
                
                if current_price is None:
                    # Fallback: get from history
                    hist = ticker.history(period='1d', interval='1m')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                
                if current_price:
                    self.current_prices[pair] = {
                        'price': float(current_price),
                        'timestamp': datetime.now(),
                        'bid': float(current_price) * 0.9999,  # Approximation
                        'ask': float(current_price) * 1.0001   # Approximation
                    }
                    
            except Exception as e:
                print(f"Error fetching price for {pair}: {e}")
                
    def get_current_price(self, pair):
        """Get current price for a currency pair"""
        return self.current_prices.get(pair, {}).get('price', None)
    
    def get_historical_data(self, pair, timeframe='5m', period='1d'):
        """Get historical data for technical analysis"""
        try:
            yf_symbol = self._convert_pair_to_yfinance(pair)
            ticker = yf.Ticker(yf_symbol)
            
            # Map timeframes
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '1d': '1d'
            }
            
            yf_interval = interval_map.get(timeframe, '5m')
            
            # Fetch historical data
            hist = ticker.history(period=period, interval=yf_interval)
            
            if hist.empty:
                return None
                
            # Clean and prepare data
            hist = hist.dropna()
            hist.index = pd.to_datetime(hist.index)
            
            return hist
            
        except Exception as e:
            print(f"Error fetching historical data for {pair}: {e}")
            return None
    
    def get_volatility(self, pair, period=20):
        """Calculate volatility for TP/SL calculation"""
        try:
            hist = self.get_historical_data(pair, timeframe='1h', period='5d')
            if hist is None or len(hist) < period:
                return 0.001  # Default volatility
                
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.rolling(window=period).std().iloc[-1]
            
            return max(volatility, 0.0005)  # Minimum volatility
            
        except Exception as e:
            print(f"Error calculating volatility for {pair}: {e}")
            return 0.001
    
    def get_all_current_prices(self):
        """Get all current prices"""
        return self.current_prices.copy()
    
    def is_market_open(self):
        """Check if Forex market is open (approximate)"""
        now = datetime.now()
        # Forex market is open 24/5, closed weekends
        weekday = now.weekday()
        
        # Market closed from Friday 17:00 EST to Sunday 17:00 EST
        if weekday == 5:  # Saturday
            return False
        elif weekday == 6:  # Sunday
            return now.hour >= 17  # Opens Sunday 17:00 EST
        elif weekday == 4 and now.hour >= 17:  # Friday after 17:00 EST
            return False
        else:
            return True

# Alternative TradingView API implementation (placeholder)
class TradingViewDataFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.tradingview.com"  # Example URL
        
    def get_real_time_price(self, symbol):
        """Get real-time price from TradingView API"""
        # This is a placeholder - actual implementation would depend on TradingView API
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/quote",
                params={'symbol': symbol},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('price', None)
            else:
                return None
                
        except Exception as e:
            print(f"TradingView API error: {e}")
            return None

# Data fetcher factory
def create_data_fetcher(source='yfinance'):
    """Create appropriate data fetcher based on source"""
    if source == 'yfinance':
        return ForexDataFetcher()
    elif source == 'tradingview':
        return TradingViewDataFetcher()
    else:
        return ForexDataFetcher()  # Default to yfinance