from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
from datetime import datetime
from main_trading_system import create_trading_system, get_trading_system
from config import Config
import threading
import time

# Create Flask app
app = Flask(__name__)
app.secret_key = 'forex_trading_system_secret_key_change_in_production'

# Global trading system instance
trading_system = create_trading_system()

@app.route('/')
def index():
    """Main dashboard"""
    try:
        system_status = trading_system.get_system_status() if trading_system else {}
        current_prices = system_status.get('current_prices', {})
        
        return render_template('dashboard.html', 
                             system_status=system_status,
                             current_prices=current_prices,
                             currency_pairs=Config.CURRENCY_PAIRS)
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", 'error')
        return render_template('dashboard.html', system_status={}, current_prices={})

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        if trading_system:
            status = trading_system.get_system_status()
            return jsonify({'success': True, 'data': status})
        else:
            return jsonify({'success': False, 'error': 'Trading system not initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/prices')
def api_prices():
    """API endpoint for current prices"""
    try:
        if trading_system and trading_system.signal_generator:
            prices = trading_system.signal_generator.data_fetcher.get_all_current_prices()
            return jsonify({'success': True, 'data': prices})
        else:
            return jsonify({'success': False, 'error': 'Data fetcher not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/signals')
def api_signals():
    """API endpoint for signals"""
    try:
        if trading_system:
            active_signals = trading_system.signal_generator.get_active_signals()
            signal_history = trading_system.signal_generator.get_signal_history(20)
            
            return jsonify({
                'success': True, 
                'data': {
                    'active': active_signals,
                    'history': signal_history
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Trading system not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/config')
def config_page():
    """Configuration page"""
    return render_template('config.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint for configuration"""
    if request.method == 'GET':
        try:
            config_data = {
                'telegram_bot_token': Config.TELEGRAM_BOT_TOKEN,
                'telegram_chat_id': Config.TELEGRAM_CHAT_ID,
                'currency_pairs': Config.CURRENCY_PAIRS,
                'scan_interval': Config.SCAN_INTERVAL,
                'min_confidence': Config.MIN_CONFIDENCE,
                'min_tp_sl_points': Config.MIN_TP_SL_POINTS,
                'max_tp_sl_points': Config.MAX_TP_SL_POINTS
            }
            return jsonify({'success': True, 'data': config_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update Telegram configuration
            if 'telegram_bot_token' in data and 'telegram_chat_id' in data:
                success, message = trading_system.configure_telegram(
                    data['telegram_bot_token'], 
                    data['telegram_chat_id']
                )
                
                if not success:
                    return jsonify({'success': False, 'error': message})
            
            # Update other configuration parameters
            if 'min_confidence' in data:
                Config.MIN_CONFIDENCE = float(data['min_confidence'])
            
            if 'scan_interval' in data:
                Config.SCAN_INTERVAL = int(data['scan_interval'])
            
            if 'min_tp_sl_points' in data:
                Config.MIN_TP_SL_POINTS = int(data['min_tp_sl_points'])
            
            if 'max_tp_sl_points' in data:
                Config.MAX_TP_SL_POINTS = int(data['max_tp_sl_points'])
            
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/start', methods=['POST'])
def api_start_system():
    """Start the trading system"""
    try:
        if not trading_system.running:
            trading_system.start()
            return jsonify({'success': True, 'message': 'Trading system started successfully'})
        else:
            return jsonify({'success': False, 'error': 'Trading system is already running'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/stop', methods=['POST'])
def api_stop_system():
    """Stop the trading system"""
    try:
        if trading_system.running:
            trading_system.stop()
            return jsonify({'success': True, 'message': 'Trading system stopped successfully'})
        else:
            return jsonify({'success': False, 'error': 'Trading system is not running'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scan/force', methods=['POST'])
def api_force_scan():
    """Force an immediate scan"""
    try:
        if trading_system.running:
            # Run scan in background to avoid blocking
            def background_scan():
                trading_system.force_scan()
            
            thread = threading.Thread(target=background_scan)
            thread.daemon = True
            thread.start()
            
            return jsonify({'success': True, 'message': 'Force scan initiated'})
        else:
            return jsonify({'success': False, 'error': 'Trading system is not running'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test/alerts', methods=['POST'])
def api_test_alerts():
    """Test alert system"""
    try:
        results = trading_system.test_alerts()
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test/telegram', methods=['POST'])
def api_test_telegram():
    """Test Telegram connection"""
    try:
        success, message = trading_system.alert_system.test_telegram_connection()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test/sound', methods=['POST'])
def api_test_sound():
    """Test sound alert"""
    try:
        success = trading_system.alert_system.test_sound_alert()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pair/analyze/<pair>')
def api_analyze_pair(pair):
    """Analyze a specific currency pair"""
    try:
        if pair not in Config.CURRENCY_PAIRS:
            return jsonify({'success': False, 'error': 'Invalid currency pair'})
        
        signal = trading_system.get_pair_analysis(pair)
        
        if signal:
            return jsonify({'success': True, 'data': signal.to_dict()})
        else:
            return jsonify({'success': True, 'data': None, 'message': 'No signal generated for this pair'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/signals')
def api_export_signals():
    """Export signal history"""
    try:
        filename = trading_system.export_signal_history()
        if filename:
            return jsonify({'success': True, 'filename': filename})
        else:
            return jsonify({'success': False, 'error': 'Failed to export signals'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/signals')
def signals_page():
    """Signals monitoring page"""
    try:
        active_signals = trading_system.signal_generator.get_active_signals() if trading_system else []
        signal_history = trading_system.signal_generator.get_signal_history(50) if trading_system else []
        
        return render_template('signals.html', 
                             active_signals=active_signals,
                             signal_history=signal_history)
    except Exception as e:
        flash(f"Error loading signals: {str(e)}", 'error')
        return render_template('signals.html', active_signals=[], signal_history=[])

@app.route('/alerts')
def alerts_page():
    """Alerts configuration page"""
    try:
        alert_status = trading_system.alert_system.get_status() if trading_system else {}
        return render_template('alerts.html', alert_status=alert_status)
    except Exception as e:
        flash(f"Error loading alerts page: {str(e)}", 'error')
        return render_template('alerts.html', alert_status={})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

# Template functions
@app.template_filter('datetime')
def datetime_filter(timestamp):
    """Format datetime for templates"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return str(timestamp)

@app.template_filter('currency')
def currency_filter(value):
    """Format currency values"""
    try:
        return f"{float(value):.5f}"
    except:
        return str(value)

@app.template_filter('percentage')
def percentage_filter(value):
    """Format percentage values"""
    try:
        return f"{float(value)*100:.1f}%"
    except:
        return str(value)

if __name__ == '__main__':
    # Development server
    print("Starting Forex Trading System Web Interface...")
    print("Access the dashboard at: http://localhost:5000")
    
    # Start with debug mode for development
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)