# Forex Trading Signal System

🚀 **Automated Forex trading signal system** that analyzes real-time charts and generates high-confidence trading signals with integrated Telegram alerts and sound notifications.

## ✨ Key Features

### 🟩 Trading Analysis
- **Real-time Data**: Live Forex price feeds with tick-by-tick updates
- **Multi-timeframe Analysis**: Primary M5 + confirmation M15 timeframes
- **Technical Indicators**: RSI, MACD, Moving Average, Bollinger Bands, Stochastic
- **High-confidence Signals**: Only sends signals above 75% confidence threshold
- **6 Major Pairs**: EUR/USD, EUR/JPY, EUR/GBP, AUD/JPY, GBP/JPY, GBP/USD

### 🟦 Intelligent Signal Generation
- **Dynamic TP/SL**: Calculated based on market volatility (50-100 points)
- **Smart Entry Conditions**: Multiple indicator confirmation required
- **Trend Confluence**: M5 and M15 timeframe agreement
- **Risk Management**: Automatic stop-loss and take-profit levels

### 🟥 Alert System
- **Telegram Integration**: Instant signal delivery to your phone/desktop
- **Sound Alerts**: Audio notifications with custom alert tones
- **Advanced Timing**: 10-second advance warning before entry points
- **Rich Formatting**: Professional signal format with all trading details

### 📊 Professional Web Interface
- **Real-time Dashboard**: Live price monitoring and system status
- **Signal Management**: Track active signals and historical performance
- **Configuration Panel**: Easy setup for Telegram bot and trading parameters
- **System Controls**: Start/stop system and force manual scans

## 🛠️ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Telegram Bot
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create new bot: `/newbot`
3. Copy the Bot Token
4. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)

### 3. Start the System
```bash
# Option 1: Web Interface (Recommended)
python web_interface.py

# Option 2: Command Line
python main_trading_system.py start
```

### 4. Access Web Dashboard
Open your browser and go to: **http://localhost:5000**

## 📱 Telegram Signal Format

```yaml
📡 Forex Signal  
Pair: GBP/JPY  
Signal: ✅ BUY  
Entry: 203.500  
TP: 204.000  
SL: 203.000  
Confidence: 85%
⏰ Time: 16:05 (GMT+7)
Reason: MACD bullish crossover, RSI recovery
```

## ⚙️ Configuration Options

### Trading Parameters
- **Minimum Confidence**: 50% - 100% (default: 75%)
- **Scan Interval**: 15-30 minutes (default: 15 minutes)
- **TP/SL Range**: 50-100 points (dynamic based on volatility)

### Alert Settings
- **Advance Warning**: 0-60 seconds before entry (default: 10 seconds)
- **Sound Alerts**: Custom alert tones with volume control
- **Telegram Notifications**: Rich formatting with emojis

### Currency Pairs
Currently monitoring 6 major Forex pairs:
- **EUR/USD** - Euro vs US Dollar
- **EUR/JPY** - Euro vs Japanese Yen  
- **EUR/GBP** - Euro vs British Pound
- **AUD/JPY** - Australian Dollar vs Japanese Yen
- **GBP/JPY** - British Pound vs Japanese Yen
- **GBP/USD** - British Pound vs US Dollar

## 🔧 Technical Architecture

### Core Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Fetcher  │───▶│ Technical Analyzer│───▶│ Signal Generator│
│   (yFinance)    │    │ (RSI,MACD,BB,etc)│    │  (Entry Logic)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              │
│   Web Interface │◄───│  Alert System    │◄─────────────┘
│  (Dashboard)    │    │(Telegram + Sound)│
└─────────────────┘    └──────────────────┘
```

### Technical Indicators Used
- **RSI (14)**: Momentum oscillator for overbought/oversold conditions
- **MACD (12,26,9)**: Trend following momentum indicator
- **SMA (20)**: Simple moving average for trend direction
- **Bollinger Bands (20,2)**: Volatility and mean reversion indicator  
- **Stochastic (14,3)**: Momentum oscillator for entry timing

## 📊 Signal Generation Logic

### Entry Conditions (All Must Be Met)
1. **Trend Confirmation**: M15 timeframe shows clear trend direction
2. **M5 Signal**: Primary timeframe confirms entry opportunity
3. **RSI Confirmation**: Not in extreme overbought/oversold territory
4. **MACD Momentum**: Histogram shows increasing momentum
5. **Stochastic Entry**: K line above D line (for buy signals)
6. **Bollinger Position**: Price in favorable position relative to bands

### Risk Management
- **Dynamic TP/SL**: Based on current market volatility
- **Point Calculation**: 
  - JPY pairs: 1 point = 0.01
  - Other pairs: 1 point = 0.0001
- **No Duplicate Signals**: Prevents multiple signals for same pair within 1 hour

## 🎯 Usage Examples

### Command Line Operations
```bash
# Start the trading system
python main_trading_system.py start

# Force an immediate scan
python main_trading_system.py scan

# Test alert systems
python main_trading_system.py test

# Check system status
python main_trading_system.py status
```

### Web Interface Features
- **Dashboard**: Real-time price monitoring and system overview
- **Signals Page**: Detailed signal history and active trades
- **Configuration**: Easy setup for all system parameters
- **Alerts Page**: Test and configure notification systems

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **Internet Connection** (for real-time data)
- **Audio Output** (for sound alerts)

### Python Dependencies
```
flask==3.0.0
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
python-telegram-bot==21.0.1
pydub==0.25.1
simpleaudio==1.0.4
ta==0.11.0
yfinance==0.2.28
schedule==1.2.0
```

## 🚨 Important Notes

### Market Hours
- **Forex Market**: Open 24/5 (Monday 17:00 EST to Friday 17:00 EST)
- **Weekend Closure**: System automatically detects and pauses during weekends
- **Holiday Awareness**: May experience reduced volatility during major holidays

### Data Sources
- **Primary**: yFinance API (free, reliable)
- **Alternative**: TradingView API support (placeholder implementation)
- **Update Frequency**: 30-second price updates, 15-minute analysis cycles

### Risk Disclaimer
⚠️ **This is an educational/analysis tool only. All trading involves risk. Past performance does not guarantee future results. Always verify signals with your own analysis before trading.**

## 🔄 Maintenance & Updates

### Log Monitoring
- System generates detailed logs for all operations
- Error handling with automatic recovery mechanisms
- Performance metrics tracking

### Data Backup
- Signal history automatically saved
- Configuration export/import functionality
- System state preservation across restarts

## 📞 Support & Troubleshooting

### Common Issues
1. **Telegram Not Working**: Verify bot token and chat ID
2. **No Sound**: Check audio drivers and simpleaudio installation
3. **No Price Data**: Verify internet connection and yFinance access
4. **High CPU Usage**: Adjust scan interval in configuration

### Debug Mode
```bash
# Run with debug output
python web_interface.py --debug

# View detailed logs
tail -f system.log
```

## 🎉 Getting Started Checklist

- [ ] Install Python 3.8+ and dependencies
- [ ] Create Telegram bot with @BotFather  
- [ ] Get your Telegram chat ID
- [ ] Run `python web_interface.py`
- [ ] Open http://localhost:5000
- [ ] Configure Telegram settings
- [ ] Test alerts system
- [ ] Start the trading system
- [ ] Monitor first signals

---

**🎯 Ready to start receiving professional Forex signals? Follow the setup guide above and you'll be up and running in minutes!**

## 📄 License

This project is provided for educational purposes. Please ensure compliance with your local financial regulations before use.

---
*Built with ❤️ for the Forex trading community*