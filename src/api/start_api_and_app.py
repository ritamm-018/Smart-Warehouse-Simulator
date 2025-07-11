import subprocess
import sys
import time
import os
from threading import Thread

def run_api():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    try:
        subprocess.run([sys.executable, "api_backend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API backend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 API backend stopped")

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for API to start
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8504"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit frontend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Streamlit frontend stopped")

def main():
    """Start both API and Streamlit"""
    print("🏭 Smart Warehouse Simulator - Starting Services")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists("api_backend.py"):
        print("❌ api_backend.py not found!")
        return
    
    if not os.path.exists("app.py"):
        print("❌ app.py not found!")
        return
    
    # Start API in a separate thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Start Streamlit in main thread
    run_streamlit()

if __name__ == "__main__":
    main() 