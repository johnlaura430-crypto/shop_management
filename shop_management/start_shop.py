import webbrowser
import threading
import time
import os
import sys

def open_browser():
    time.sleep(3)
    webbrowser.open('http://localhost:5000')

def main():
    print("🛍️  Starting Shop Management System...")
    print("Please wait for the browser to open automatically...")
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        from app import app
        threading.Timer(2, open_browser).start()
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error starting the system: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()