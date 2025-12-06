import sys
import os
import time

# Add the parent directory to sys.path so we can import the sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sdk

def risky_operation():
    print("Performing risky operation...")
    time.sleep(1)
    # Check if divisor is zero before performing division
    divisor = 0
    if divisor != 0:
        result = 10 / divisor
    else:
        result = "Cannot divide by zero"
    return result

def main():
    # Initialize the SDK and install the global exception hook
    print("Initializing Log Analysis SDK...")
    sdk.install(service_name="buggy-service")

    print("Running application logic...")
    try:
        risky_operation()
    except Exception:
        # The exception hook will catch this if we let it bubble up,
        # but here we might want to demonstrate manual logging too?
        # Let's just let it crash to test the hook.
        raise

if __name__ == "__main__":
    main()
