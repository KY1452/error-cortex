import sys
import os
import time

# Add parent directory to path to import sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sdk

def main():
    print("Initializing Log Analysis SDK...")
    sdk.install("config-service")
    
    print("Running application logic...")
    time.sleep(1)
    
    read_config()

def read_config():
    print("Attempting to read configuration...")
    # This will raise FileNotFoundError
    with open("non_existent_config.json", "r") as f:
        return f.read()

if __name__ == "__main__":
    main()
