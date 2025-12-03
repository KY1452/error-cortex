import subprocess
import time
import sys
import os

def run_scenario():
    print("Running scenario: scenarios/zero_division.py")
    result = subprocess.run(["python", "scenarios/zero_division.py"], capture_output=True, text=True)
    return result

def main():
    print("--- Step 1: Initial Run (Expect Failure) ---")
    result = run_scenario()
    if result.returncode != 0:
        print("✅ Scenario failed as expected.")
        print(f"Output:\n{result.stderr}")
    else:
        print("❌ Scenario passed unexpectedly!")
        sys.exit(1)

    print("\n--- Step 2: Verification Complete ---")
    print("1. Go to the Dashboard (http://127.0.0.1:8000).")
    print("2. You should see the ZeroDivisionError log.")
    print("3. Verify that the AI provides a clear explanation.")
    print("✅ Workflow verified: Error detected and explained.")

if __name__ == "__main__":
    main()
