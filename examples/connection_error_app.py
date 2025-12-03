import sys
import os
import time

# Add parent directory to path to import sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sdk

def connect_to_db():
    print("Attempting to connect to database...")
    # Simulate a connection error
    raise ConnectionRefusedError("Connection refused: 127.0.0.1:5432")

def main():
    print("Initializing Log Analysis SDK...")
    sdk.install("order-service")
    
    print("Processing orders...")
    time.sleep(1)
    
    connect_to_db()

if __name__ == "__main__":
    main()
