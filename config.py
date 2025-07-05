import os
from datetime import datetime
import pytz

class Config:
    # Currency pairs to monitor
    CURRENCY_PAIRS = [
        'EURUSD', 'EURJPY', 'EURGBP', 
        'AUDJPY', 'GBPJPY', 'GBPUSD'
    ]
    
    # Timeframes
    PRIMARY_TIMEFRAME = '5m'  # M5
    CONFIRMATION_TIMEFRAME = '15m'  # M15
    
    # Technical Analysis Parameters
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    MA_PERIOD = 20
    
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    STOCH_K = 14
    STOCH_D = 3
    
    # TP/SL Settings
    MIN_TP_SL_POINTS = 50
    MAX_TP_SL_POINTS = 100
    
    # Alert Settings
    SCAN_INTERVAL = 15 * 60  # 15 minutes in seconds
    ALERT_ADVANCE_TIME = 10  # 10 seconds before entry
    
    # Telegram Settings (will be set via web interface)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Timezone
    TIMEZONE = 'Asia/Bangkok'  # GMT+7
    
    # Sound Settings
    SOUND_FILE = 'alert.wav'
    
    # Data Source
    DATA_SOURCE = 'yfinance'  # Can be switched to TradingView API
    
    # Signal Confidence Threshold
    MIN_CONFIDENCE = 0.75  # Only high-confidence signals
    
    @classmethod
    def update_telegram_config(cls, bot_token, chat_id):
        cls.TELEGRAM_BOT_TOKEN = bot_token
        cls.TELEGRAM_CHAT_ID = chat_id
        
    @classmethod
    def get_current_time(cls):
        tz = pytz.timezone(cls.TIMEZONE)
        return datetime.now(tz)