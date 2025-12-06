import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sdk.client import LogAnalysisClient

def trigger_syntax_error():
    print("Initializing SDK...")
    client = LogAnalysisClient("syntax-test-service")
    
    print("Sending 'FORCE_SYNTAX_ERROR' log...")
    try:
        # We simulate an error that asks for the syntax error test
        raise ValueError("FORCE_SYNTAX_ERROR: This should trigger the guardrail.")
    except Exception as e:
        client.send_error(e, exc_info=sys.exc_info())
        print("Log sent!")
        print("Check the Dashboard. You should see a '⚠️ Syntax Warning'.")

    time.sleep(1)
    client.close()

if __name__ == "__main__":
    trigger_syntax_error()
