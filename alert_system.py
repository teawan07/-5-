import asyncio
import threading
import time
import os
from datetime import datetime
import requests
import json
from config import Config

# Sound libraries
try:
    import simpleaudio as sa
    SOUND_AVAILABLE = True
except ImportError:
    print("simpleaudio not available. Sound alerts disabled.")
    SOUND_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.generators import Sine
    AUDIO_GENERATION_AVAILABLE = True
except ImportError:
    AUDIO_GENERATION_AVAILABLE = False

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or Config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.connected = False
        
    def test_connection(self):
        """Test Telegram bot connection"""
        try:
            if not self.bot_token:
                return False, "Bot token not provided"
                
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    self.connected = True
                    return True, f"Connected to bot: {data['result']['first_name']}"
                else:
                    return False, data.get('description', 'Unknown error')
            else:
                return False, f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def send_message(self, message):
        """Send message to Telegram"""
        try:
            if not self.bot_token or not self.chat_id:
                print("Telegram bot token or chat ID not configured")
                return False
                
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return True
                else:
                    print(f"Telegram API error: {data.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Telegram connection error: {e}")
            return False
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def update_config(self, bot_token, chat_id):
        """Update bot configuration"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        Config.update_telegram_config(bot_token, chat_id)
        self.connected = False

class SoundAlert:
    def __init__(self):
        self.enabled = SOUND_AVAILABLE
        self.sound_file = None
        self._generate_alert_sound()
        
    def _generate_alert_sound(self):
        """Generate a default alert sound if none exists"""
        if not AUDIO_GENERATION_AVAILABLE:
            return
            
        try:
            # Create a simple alert tone (800Hz for 0.5 seconds)
            tone = Sine(800).to_audio_segment(duration=500)
            
            # Add a short pause and repeat
            silence = AudioSegment.silent(duration=100)
            alert_sound = tone + silence + tone
            
            # Export as WAV
            sound_path = "alert.wav"
            alert_sound.export(sound_path, format="wav")
            self.sound_file = sound_path
            print(f"Generated alert sound: {sound_path}")
            
        except Exception as e:
            print(f"Error generating alert sound: {e}")
    
    def play_alert(self):
        """Play alert sound"""
        if not self.enabled:
            print("Sound alerts disabled (simpleaudio not available)")
            return False
            
        try:
            if self.sound_file and os.path.exists(self.sound_file):
                wave_obj = sa.WaveObject.from_wave_file(self.sound_file)
                play_obj = wave_obj.play()
                return True
            else:
                print("Alert sound file not found")
                return False
                
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False
    
    def test_sound(self):
        """Test sound alert"""
        return self.play_alert()

class AlertSystem:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.sound_alert = SoundAlert()
        self.alert_queue = []
        self.running = False
        self.alert_thread = None
        
    def start(self):
        """Start the alert system"""
        self.running = True
        self.alert_thread = threading.Thread(target=self._alert_loop)
        self.alert_thread.daemon = True
        self.alert_thread.start()
        print("Alert system started")
        
    def stop(self):
        """Stop the alert system"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join()
        print("Alert system stopped")
        
    def _alert_loop(self):
        """Main alert processing loop"""
        while self.running:
            try:
                if self.alert_queue:
                    alert = self.alert_queue.pop(0)
                    self._process_alert(alert)
                else:
                    time.sleep(1)
            except Exception as e:
                print(f"Error in alert loop: {e}")
                time.sleep(5)
                
    def _process_alert(self, alert):
        """Process a single alert"""
        try:
            alert_type = alert.get('type')
            
            if alert_type == 'signal':
                self._handle_signal_alert(alert)
            elif alert_type == 'test':
                self._handle_test_alert(alert)
            elif alert_type == 'status':
                self._handle_status_alert(alert)
                
        except Exception as e:
            print(f"Error processing alert: {e}")
    
    def _handle_signal_alert(self, alert):
        """Handle trading signal alert"""
        signal = alert.get('signal')
        if not signal:
            return
            
        # Play sound alert first
        print("Playing sound alert...")
        self.sound_alert.play_alert()
        
        # Send Telegram message
        message = signal.format_telegram_message()
        print(f"Sending Telegram alert for {signal.pair} {signal.signal_type}")
        
        success = self.telegram_bot.send_message(message)
        if success:
            print("Telegram alert sent successfully")
        else:
            print("Failed to send Telegram alert")
    
    def _handle_test_alert(self, alert):
        """Handle test alert"""
        message = alert.get('message', 'Test alert from Forex Trading System')
        
        # Play sound
        self.sound_alert.play_alert()
        
        # Send Telegram
        self.telegram_bot.send_message(f"🔔 Test Alert\n{message}")
    
    def _handle_status_alert(self, alert):
        """Handle status alert"""
        message = alert.get('message', 'System status update')
        
        # Only send Telegram (no sound for status)
        self.telegram_bot.send_message(f"ℹ️ Status Update\n{message}")
    
    def send_signal_alert(self, signal):
        """Queue a signal alert"""
        alert = {
            'type': 'signal',
            'signal': signal,
            'timestamp': datetime.now()
        }
        self.alert_queue.append(alert)
        print(f"Queued signal alert for {signal.pair}")
    
    def send_test_alert(self, message="Test from Forex Trading System"):
        """Send a test alert"""
        alert = {
            'type': 'test',
            'message': message,
            'timestamp': datetime.now()
        }
        self.alert_queue.append(alert)
        print("Queued test alert")
    
    def send_status_alert(self, message):
        """Send a status alert"""
        alert = {
            'type': 'status',
            'message': message,
            'timestamp': datetime.now()
        }
        self.alert_queue.append(alert)
    
    def update_telegram_config(self, bot_token, chat_id):
        """Update Telegram configuration"""
        self.telegram_bot.update_config(bot_token, chat_id)
        return self.telegram_bot.test_connection()
    
    def test_telegram_connection(self):
        """Test Telegram connection"""
        return self.telegram_bot.test_connection()
    
    def test_sound_alert(self):
        """Test sound alert"""
        return self.sound_alert.test_sound()
    
    def get_status(self):
        """Get alert system status"""
        telegram_status = "Connected" if self.telegram_bot.connected else "Disconnected"
        sound_status = "Enabled" if self.sound_alert.enabled else "Disabled"
        
        return {
            'running': self.running,
            'telegram_status': telegram_status,
            'sound_status': sound_status,
            'queue_size': len(self.alert_queue),
            'bot_token_configured': bool(self.telegram_bot.bot_token),
            'chat_id_configured': bool(self.telegram_bot.chat_id)
        }

# Advanced alert scheduling for "10 seconds before entry"
class AdvancedAlertScheduler:
    def __init__(self, alert_system):
        self.alert_system = alert_system
        self.scheduled_alerts = []
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the advanced scheduler"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
    def stop(self):
        """Stop the advanced scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
            
    def _scheduler_loop(self):
        """Scheduler loop for advanced alerts"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for alerts to trigger
                for alert in self.scheduled_alerts[:]:
                    if current_time >= alert['trigger_time']:
                        self.alert_system.send_signal_alert(alert['signal'])
                        self.scheduled_alerts.remove(alert)
                        
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                time.sleep(5)
    
    def schedule_signal_alert(self, signal, advance_seconds=10):
        """Schedule a signal alert with advance warning"""
        from datetime import timedelta
        
        trigger_time = datetime.now() + timedelta(seconds=advance_seconds)
        
        scheduled_alert = {
            'signal': signal,
            'trigger_time': trigger_time,
            'scheduled_at': datetime.now()
        }
        
        self.scheduled_alerts.append(scheduled_alert)
        print(f"Scheduled alert for {signal.pair} at {trigger_time.strftime('%H:%M:%S')}")
    
    def get_scheduled_alerts(self):
        """Get list of scheduled alerts"""
        return [{
            'pair': alert['signal'].pair,
            'signal_type': alert['signal'].signal_type,
            'trigger_time': alert['trigger_time'].isoformat(),
            'scheduled_at': alert['scheduled_at'].isoformat()
        } for alert in self.scheduled_alerts]