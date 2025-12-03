#!/bin/bash

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $CONSUMER_PID 2>/dev/null
    kill $DASHBOARD_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT

# Check if Docker is running
echo "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running."
    echo "Please start Docker Desktop and run this script again."
    exit 1
fi

echo "Installing dependencies..."
python -m pip install -r requirements.txt





echo "Starting RabbitMQ..."
docker-compose up -d

echo "Waiting for RabbitMQ to initialize (10s)..."
sleep 10

echo "Starting Consumer (Assistant)..."
# Using 'python' as it seems to be the one with dependencies installed
python consumer/main.py &
CONSUMER_PID=$!
echo "Consumer PID: $CONSUMER_PID"

echo "Starting Dashboard..."
uvicorn dashboard.app:app --port 8000 &
DASHBOARD_PID=$!
echo "Dashboard PID: $DASHBOARD_PID"

echo "Waiting for services to settle (5s)..."
sleep 5

echo "---------------------------------------------------"
echo "Running Buggy App (Example)..."
echo "---------------------------------------------------"
python examples/buggy_app.py
echo "---------------------------------------------------"

echo "Demo Complete!"
echo "1. Open the Dashboard: http://localhost:8000"
echo "2. You should see the 'ZeroDivisionError' log."
echo ""
echo "Press Ctrl+C to stop the Consumer and Dashboard."

# Wait forever (until Ctrl+C)
wait
