#!/usr/bin/env python3
"""
Forex Trading Signal System - Startup Script

This script provides an easy way to start the Forex trading system
in different modes with proper error handling and user guidance.
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

def print_banner():
    """Print system banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                 🚀 FOREX TRADING SIGNAL SYSTEM 🚀             ║
║                                                               ║
║         Automated Forex Analysis with Real-time Alerts       ║
║              Telegram Integration • Sound Alerts             ║
║                    Professional Web Interface                 ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'requests', 'pandas', 'numpy', 'python-telegram-bot',
        'pydub', 'simpleaudio', 'ta', 'yfinance', 'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("📋 Requires Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def start_web_interface():
    """Start the web interface"""
    print("\n🌐 Starting Web Interface...")
    print("📍 Access dashboard at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "web_interface.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except FileNotFoundError:
        print("❌ web_interface.py not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

def start_command_line():
    """Start the command line version"""
    print("\n💻 Starting Command Line Interface...")
    print("⏹️  Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "main_trading_system.py", "start"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Trading system stopped by user")
    except FileNotFoundError:
        print("❌ main_trading_system.py not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting trading system: {e}")
        sys.exit(1)

def quick_test():
    """Run quick system test"""
    print("\n🧪 Running Quick System Test...")
    
    try:
        result = subprocess.run([sys.executable, "main_trading_system.py", "test"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ System test completed successfully")
            print(result.stdout)
        else:
            print("❌ System test failed")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
    except FileNotFoundError:
        print("❌ main_trading_system.py not found")
    except Exception as e:
        print(f"❌ Error running test: {e}")

def show_setup_guide():
    """Show setup guide for first-time users"""
    guide = """
📋 FIRST-TIME SETUP GUIDE

1. 🤖 Create Telegram Bot:
   • Message @BotFather on Telegram
   • Send: /newbot
   • Follow instructions and save your Bot Token
   
2. 📱 Get Your Chat ID:
   • Message @userinfobot on Telegram
   • Note down your Chat ID number
   
3. 🌐 Configure System:
   • Start web interface: python start_system.py --web
   • Go to Configuration page
   • Enter Bot Token and Chat ID
   • Test your alerts
   
4. 🚀 Start Trading:
   • Return to Dashboard
   • Click "Start System"
   • Monitor real-time signals

💡 Need help? Check README.md for detailed instructions.
    """
    print(guide)

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def show_status():
    """Show system status"""
    print("\n📊 System Status Check...")
    
    try:
        result = subprocess.run([sys.executable, "main_trading_system.py", "status"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Unable to get system status")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Status check timed out")
    except FileNotFoundError:
        print("❌ main_trading_system.py not found")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Forex Trading Signal System Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_system.py --web          # Start web interface (recommended)
  python start_system.py --cli          # Start command line interface
  python start_system.py --test         # Run system test
  python start_system.py --setup        # Show setup guide
  python start_system.py --install      # Install dependencies
  python start_system.py --status       # Check system status
        """
    )
    
    parser.add_argument('--web', action='store_true', 
                       help='Start web interface (recommended)')
    parser.add_argument('--cli', action='store_true', 
                       help='Start command line interface')
    parser.add_argument('--test', action='store_true', 
                       help='Run quick system test')
    parser.add_argument('--setup', action='store_true', 
                       help='Show first-time setup guide')
    parser.add_argument('--install', action='store_true', 
                       help='Install missing dependencies')
    parser.add_argument('--status', action='store_true', 
                       help='Check system status')
    parser.add_argument('--skip-checks', action='store_true', 
                       help='Skip dependency and version checks')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Show setup guide if requested
    if args.setup:
        show_setup_guide()
        return
    
    # Install dependencies if requested
    if args.install:
        if install_dependencies():
            print("\n✅ Ready to start! Run: python start_system.py --web")
        return
    
    # Skip checks if requested
    if not args.skip_checks:
        # Check Python version
        if not check_python_version():
            return
        
        # Check dependencies
        if not check_dependencies():
            print("\n💡 Run with --install to install missing dependencies")
            return
    
    # Handle different modes
    if args.test:
        quick_test()
    elif args.status:
        show_status()
    elif args.cli:
        start_command_line()
    elif args.web:
        start_web_interface()
    else:
        # Default behavior - interactive menu
        print("\n🎯 Choose your preferred way to start:")
        print("1. 🌐 Web Interface (Recommended)")
        print("2. 💻 Command Line Interface")
        print("3. 🧪 Run System Test")
        print("4. 📊 Check System Status")
        print("5. 📋 Show Setup Guide")
        print("6. 📦 Install Dependencies")
        print("0. ❌ Exit")
        
        while True:
            try:
                choice = input("\n👉 Enter your choice (1-6, 0 to exit): ").strip()
                
                if choice == '1':
                    start_web_interface()
                    break
                elif choice == '2':
                    start_command_line()
                    break
                elif choice == '3':
                    quick_test()
                    break
                elif choice == '4':
                    show_status()
                    break
                elif choice == '5':
                    show_setup_guide()
                    break
                elif choice == '6':
                    if install_dependencies():
                        print("\n✅ Ready to start! Choose option 1 for web interface.")
                    break
                elif choice == '0':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-6 or 0.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()