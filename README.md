# ErrorCortex SDK

A pluggable Python SDK for real-time error tracking and AI-powered analysis.

## Features
- **Real-time Error Capture**: Automatically catches unhandled exceptions.
- **AI Analysis**: Explains errors and suggests fixes using LLMs (Ollama).
- **Memory (RAG)**: Remembers past solutions to provide smarter suggestions over time.
- **Dashboard**: Web interface to view logs, code context, and manage solutions.

## Architecture
- **SDK**: Python package that hooks into `sys.excepthook` to capture errors.
- **RabbitMQ**: Message broker for reliable log transport.
- **Consumer**: Python service that processes logs, queries Llama-3, and stores data.
- **Dashboard**: FastAPI web app for visualizing errors and feedback.
- **ChromaDB**: Vector database for long-term memory of solutions.

## Installation

1.  **Prerequisites**:
    - Docker Desktop (for RabbitMQ)
    - Ollama (for AI models) -> Run `ollama run llama3.2`
    - Python 3.8+

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Quick Start

1.  **Start the System**:
    ```bash
    ./demo.sh
    ```
    This script starts RabbitMQ (Docker), the Consumer, and the Dashboard.

2.  **Run Example Apps**:
    Open a new terminal and run any of the examples:
    ```bash
    python examples/buggy_app.py           # Triggers ZeroDivisionError
    python examples/missing_file_app.py    # Triggers FileNotFoundError
    python examples/index_error_app.py     # Triggers IndexError
    python examples/connection_error_app.py # Triggers ConnectionRefusedError
    ```

3.  **View Dashboard**:
    Open [http://localhost:8000](http://localhost:8000) to see the errors and AI analysis.

## How to Use in Your App

You can integrate this SDK into **any** Python application with just 2 lines of code.

### 1. Import the SDK
```python
import sdk
```

### 2. Install the Hook
Call `sdk.install()` at the start of your application (e.g., in `main()` or `__init__`).

```python
def main():
    # Initialize and start listening for errors
    sdk.install(service_name="my-awesome-app")

    # Your application code...
```

## "Teaching" the AI (Memory)

1.  When you see an error in the dashboard, review the AI's solution.
2.  If it's good, click **"Mark as Fixed (Teach AI)"**.
3.  The system stores this solution in its vector memory.
4.  Next time a similar error occurs, the AI will use this memory to provide a better, context-aware solution (indicated by a **"Knowledge Retrieved"** badge).
