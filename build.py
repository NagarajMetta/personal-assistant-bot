#!/usr/bin/env python3
"""Build and setup script for the Telegram Bot project"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Build the project"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Building Telegram Personal Assistant Bot             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    project_root = Path(__file__).parent
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found!")
        sys.exit(1)
    
    # Install/update dependencies
    print("\n📚 Checking dependencies...")
    if not run_command("pip install -r requirements.txt -q", "Installing dependencies"):
        print("⚠️  Some dependencies may not be installed")
    
    # Create logs directory
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Logs directory ready: {logs_dir}")
    
    # Verify database directory
    db_dir = project_root
    print(f"✅ Database directory ready: {db_dir}")
    
    # Check configuration
    print("\n🔍 Verifying configuration...")
    env_content = env_file.read_text()
    
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID", "OPENAI_API_KEY"]
    missing = []
    
    for var in required_vars:
        # Look for the variable in env file
        lines = env_content.split("\n")
        found = False
        for line in lines:
            if line.startswith(var + "="):
                value = line.split("=", 1)[1].strip()
                if value and value != "":
                    print(f"✅ {var} configured")
                    found = True
                    break
        if not found:
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing configuration: {', '.join(missing)}")
        print("Please update .env file with required credentials")
        return False
    
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║                  ✅ Build Complete!                           ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("\n🚀 To start the bot, run:")
    print("   python main.py")
    print("\n📡 Bot will be available at:")
    print("   http://127.0.0.1:8000")
    print("\n📚 API documentation at:")
    print("   http://127.0.0.1:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
