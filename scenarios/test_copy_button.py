import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sdk.client import LogAnalysisClient

def trigger_copy_test():
    print("Initializing SDK...")
    client = LogAnalysisClient("copy-test-service")
    
    print("Sending 'FORCE_VALID_CODE' log...")
    try:
        raise ValueError("FORCE_VALID_CODE: This should show a clean code block with a Copy button.")
    except Exception as e:
        client.send_error(e, exc_info=sys.exc_info())
        print("Log sent!")
        print("Check the Dashboard. You should see a code block with a 'Copy' button.")

    time.sleep(1)
    client.close()

if __name__ == "__main__":
    trigger_copy_test()
