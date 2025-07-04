import threading
import time
import schedule
from datetime import datetime, timedelta
from config import Config
from signal_generator import SignalGenerator
from alert_system import AlertSystem, AdvancedAlertScheduler
import json

class ForexTradingSystem:
    def __init__(self):
        self.signal_generator = SignalGenerator()
        self.alert_system = AlertSystem()
        self.advanced_scheduler = AdvancedAlertScheduler(self.alert_system)
        
        self.running = False
        self.main_thread = None
        self.system_status = {
            'started_at': None,
            'last_scan': None,
            'total_signals_generated': 0,
            'active_signals_count': 0,
            'system_health': 'unknown'
        }
        
    def start(self):
        """Start the complete trading system"""
        print("Starting Forex Trading System...")
        
        try:
            # Start all components
            self.signal_generator.start()
            self.alert_system.start()
            self.advanced_scheduler.start()
            
            # Set up the scanning schedule
            self._setup_schedule()
            
            # Start main loop
            self.running = True
            self.main_thread = threading.Thread(target=self._main_loop)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            self.system_status['started_at'] = datetime.now()
            self.system_status['system_health'] = 'running'
            
            print("✅ Forex Trading System started successfully!")
            
            # Send startup notification
            self.alert_system.send_status_alert(
                f"🚀 Forex Trading System Started\n"
                f"Monitoring {len(Config.CURRENCY_PAIRS)} currency pairs\n"
                f"Scan interval: {Config.SCAN_INTERVAL // 60} minutes\n"
                f"Started at: {datetime.now().strftime('%H:%M:%S GMT+7')}"
            )
            
        except Exception as e:
            print(f"❌ Error starting system: {e}")
            self.system_status['system_health'] = 'error'
            raise
    
    def stop(self):
        """Stop the trading system"""
        print("Stopping Forex Trading System...")
        
        try:
            self.running = False
            
            # Stop all components
            self.signal_generator.stop()
            self.alert_system.stop()
            self.advanced_scheduler.stop()
            
            # Wait for main thread to finish
            if self.main_thread:
                self.main_thread.join(timeout=5)
            
            self.system_status['system_health'] = 'stopped'
            
            print("✅ Forex Trading System stopped successfully!")
            
        except Exception as e:
            print(f"❌ Error stopping system: {e}")
            self.system_status['system_health'] = 'error'
    
    def _setup_schedule(self):
        """Setup the scanning schedule"""
        # Schedule regular scans every 15-30 minutes
        scan_interval_minutes = Config.SCAN_INTERVAL // 60
        
        # Clear any existing schedule
        schedule.clear()
        
        # Schedule scans
        schedule.every(scan_interval_minutes).minutes.do(self._scheduled_scan)
        
        # Schedule signal status updates every minute
        schedule.every(1).minutes.do(self._update_signal_status)
        
        # Schedule system health check every 5 minutes
        schedule.every(5).minutes.do(self._health_check)
        
        print(f"📅 Scheduled scans every {scan_interval_minutes} minutes")
    
    def _main_loop(self):
        """Main system loop"""
        print("🔄 Main trading loop started")
        
        # Perform initial scan after startup
        time.sleep(30)  # Wait for system to stabilize
        self._scheduled_scan()
        
        while self.running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _scheduled_scan(self):
        """Perform scheduled scan for signals"""
        try:
            print(f"\n🔍 Starting scheduled scan at {datetime.now().strftime('%H:%M:%S')}")
            
            # Scan for new signals
            new_signals = self.signal_generator.scan_all_pairs()
            
            # Process new signals
            for signal in new_signals:
                # Send immediate alert or schedule advanced alert
                if Config.ALERT_ADVANCE_TIME > 0:
                    # Schedule alert for later (advanced timing)
                    self.advanced_scheduler.schedule_signal_alert(
                        signal, Config.ALERT_ADVANCE_TIME
                    )
                else:
                    # Send immediate alert
                    self.alert_system.send_signal_alert(signal)
            
            # Update system status
            self.system_status['last_scan'] = datetime.now()
            self.system_status['total_signals_generated'] += len(new_signals)
            self.system_status['active_signals_count'] = len(self.signal_generator.active_signals)
            
            print(f"✅ Scan completed. Generated {len(new_signals)} new signals")
            
        except Exception as e:
            print(f"❌ Error in scheduled scan: {e}")
            self.system_status['system_health'] = 'warning'
    
    def _update_signal_status(self):
        """Update status of active signals"""
        try:
            self.signal_generator.update_signal_status()
            self.system_status['active_signals_count'] = len(self.signal_generator.active_signals)
            
        except Exception as e:
            print(f"Error updating signal status: {e}")
    
    def _health_check(self):
        """Perform system health check"""
        try:
            issues = []
            
            # Check data fetcher
            if not self.signal_generator.data_fetcher.running:
                issues.append("Data fetcher not running")
            
            # Check alert system
            if not self.alert_system.running:
                issues.append("Alert system not running")
            
            # Check Telegram connection
            if not self.alert_system.telegram_bot.connected:
                issues.append("Telegram bot not connected")
            
            # Check recent data
            current_prices = self.signal_generator.data_fetcher.get_all_current_prices()
            if not current_prices:
                issues.append("No current price data available")
            
            # Update health status
            if issues:
                self.system_status['system_health'] = 'warning'
                print(f"⚠️ System health issues: {', '.join(issues)}")
            else:
                self.system_status['system_health'] = 'healthy'
                
        except Exception as e:
            print(f"Error in health check: {e}")
            self.system_status['system_health'] = 'error'
    
    def force_scan(self):
        """Force an immediate scan"""
        print("🔍 Force scanning all pairs...")
        return self._scheduled_scan()
    
    def get_system_status(self):
        """Get comprehensive system status"""
        status = self.system_status.copy()
        
        # Add component statuses
        status.update({
            'signal_generator_running': self.signal_generator.data_fetcher.running,
            'alert_system_status': self.alert_system.get_status(),
            'current_prices': self.signal_generator.data_fetcher.get_all_current_prices(),
            'active_signals': self.signal_generator.get_active_signals(),
            'recent_signals': self.signal_generator.get_signal_history(10),
            'scheduled_alerts': self.advanced_scheduler.get_scheduled_alerts()
        })
        
        return status
    
    def configure_telegram(self, bot_token, chat_id):
        """Configure Telegram bot settings"""
        try:
            success, message = self.alert_system.update_telegram_config(bot_token, chat_id)
            
            if success:
                # Send test message to confirm
                self.alert_system.send_test_alert("Telegram configuration successful!")
                
            return success, message
            
        except Exception as e:
            return False, f"Configuration error: {str(e)}"
    
    def test_alerts(self):
        """Test both sound and Telegram alerts"""
        try:
            # Test sound
            sound_success = self.alert_system.test_sound_alert()
            
            # Test Telegram
            telegram_success, telegram_message = self.alert_system.test_telegram_connection()
            
            if telegram_success:
                self.alert_system.send_test_alert("Test alert - all systems working!")
            
            return {
                'sound_test': sound_success,
                'telegram_test': telegram_success,
                'telegram_message': telegram_message
            }
            
        except Exception as e:
            return {
                'sound_test': False,
                'telegram_test': False,
                'telegram_message': f"Test error: {str(e)}"
            }
    
    def get_pair_analysis(self, pair):
        """Get detailed analysis for a specific pair"""
        try:
            return self.signal_generator.analyze_pair(pair)
        except Exception as e:
            print(f"Error analyzing pair {pair}: {e}")
            return None
    
    def export_signal_history(self, filename=None):
        """Export signal history to JSON file"""
        if filename is None:
            filename = f"signal_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            history = self.signal_generator.get_signal_history()
            
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            
            print(f"Signal history exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"Error exporting signal history: {e}")
            return None

# Global instance
trading_system = None

def create_trading_system():
    """Create and return the global trading system instance"""
    global trading_system
    if trading_system is None:
        trading_system = ForexTradingSystem()
    return trading_system

def get_trading_system():
    """Get the global trading system instance"""
    global trading_system
    return trading_system

if __name__ == "__main__":
    # Command line interface for testing
    import sys
    
    system = create_trading_system()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            try:
                system.start()
                print("System started. Press Ctrl+C to stop.")
                
                while True:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\nStopping system...")
                system.stop()
                
        elif command == "scan":
            system.start()
            time.sleep(5)  # Let system initialize
            signals = system.force_scan()
            print(f"Generated {len(signals) if signals else 0} signals")
            system.stop()
            
        elif command == "test":
            system.start()
            time.sleep(2)
            results = system.test_alerts()
            print(f"Test results: {results}")
            system.stop()
            
        elif command == "status":
            system.start()
            time.sleep(2)
            status = system.get_system_status()
            print(f"System status: {json.dumps(status, indent=2, default=str)}")
            system.stop()
            
        else:
            print("Usage: python main_trading_system.py [start|scan|test|status]")
    else:
        print("Usage: python main_trading_system.py [start|scan|test|status]")