import time
import sys
import os
import statistics

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from sdk.client import LogAnalysisClient

def benchmark():
    print("Initializing SDK Client...")
    try:
        client = LogAnalysisClient("benchmark-service")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        print("Make sure ./demo.sh is running!")
        return

    latencies = []
    iterations = 100

    print(f"Running {iterations} iterations...")
    
    # Warmup
    client.send_error("Warmup error")

    for i in range(iterations):
        start_time = time.perf_counter()
        client.send_error(f"Benchmark error {i}")
        end_time = time.perf_counter()
        
        # Convert to milliseconds
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    p95_latency = sorted(latencies)[int(0.95 * len(latencies))]

    print("\n--- SDK Overhead Results ---")
    print(f"Average Latency: {avg_latency:.4f} ms")
    print(f"Min Latency:     {min_latency:.4f} ms")
    print(f"Max Latency:     {max_latency:.4f} ms")
    print(f"95th Percentile: {p95_latency:.4f} ms")
    print("----------------------------")

    client.close()

if __name__ == "__main__":
    benchmark()
