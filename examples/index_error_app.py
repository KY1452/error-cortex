import sys
import os
import time

# Add parent directory to path to import sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sdk

def process_data(data):
    print(f"Processing data: {data}")
    # This will raise IndexError
    return data[5]

def main():
    print("Initializing Log Analysis SDK...")
    sdk.install("data-processor")
    
    print("Running data processing pipeline...")
    time.sleep(1)
    
    my_list = [1, 2, 3]
    print(f"Current list: {my_list}")
    print("Attempting to access index 5...")
    
    process_data(my_list)

if __name__ == "__main__":
    main()
