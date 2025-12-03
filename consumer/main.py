import pika
import sys
import os
import json
import re
import requests
import sqlite3
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
DB_PATH = "logs.db"
print(f"Database Path: {DB_PATH}")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  service TEXT,
                  level TEXT,
                  message TEXT,
                  category TEXT,
                  solution TEXT,
                  code_context TEXT,
                  stack_trace TEXT,
                  is_known_error BOOLEAN DEFAULT 0)"""
    )
    conn.commit()
    conn.close()


def get_code_context(stack_trace):
    try:
        # Regex to find file path and line number in Python stack trace
        # File "/path/to/file.py", line 10, in <module>
        matches = re.findall(r'File "([^"]+)", line (\d+)', stack_trace)
        if matches:
            # Use the last match as it's typically the location of the actual error
            file_path, line_num_str = matches[-1]
            line_num = int(line_num_str)

            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    lines = f.readlines()

                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 10)

                snippet = "".join(
                    [
                        f"{i+1}: {line}"
                        for i, line in enumerate(lines)
                        if start <= i < end
                    ]
                )
                return (
                    f"File: {file_path}\nLine: {line_num}\n\nCode Snippet:\n{snippet}"
                )
    except Exception as e:
        print(f"Error reading code context: {e}")
    return "Code context not available."


from rag import RAGEngine

# Initialize RAG
rag_engine = RAGEngine()

def analyze_with_ai(error_category, log_entry, code_context):
    try:
        # Check for historical context
        similar_solution = rag_engine.find_similar(
            log_entry.get("message"), log_entry.get("stack_trace")
        )
        
        historical_context = ""
        if similar_solution:
            print(f" [RAG] Found similar solution: {similar_solution[:50]}...")
            historical_context = f"\n\nHISTORICAL CONTEXT (We have seen this before!):\nWe previously fixed a similar error with this solution:\n{similar_solution}\n\nPlease use this context to inform your answer."

        prompt = f"""
        Act as a senior DevOps engineer.
        I have an error log from my application.
        
        Category: {error_category}
        Service: {log_entry.get('service')}
        Message: {log_entry.get('message')}
        Stack Trace:
        {log_entry.get('stack_trace')}
        
        Code Context:
        {code_context}
        {historical_context}

        Please provide a concise explanation of what went wrong and which line is likely causing the issue.
        Do not provide a JSON response. Just plain text.
        """

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("response", "No response from AI."), bool(similar_solution)

    except requests.exceptions.ConnectionError:
        return json.dumps(
            {
                "explanation": "AI Analysis Failed: Could not connect to Ollama.",
                "fix": None,
            }
        ), False
    except Exception as e:
        return json.dumps({"explanation": f"AI Analysis Failed: {e}", "fix": None}), False


def categorize_error(message, stack_trace):
    full_text = f"{message} {stack_trace}".lower()

    if "connection refused" in full_text or "econnrefused" in full_text:
        return "Database Connection Error"
    elif "timeout" in full_text:
        return "Network Timeout"
    elif "nullpointer" in full_text or "cannot read property" in full_text:
        return "Null Pointer Exception"
    else:
        return "Unknown Application Error"


def process_log(body):
    try:
        log_entry = json.loads(body)

        # Filter: Only process ERROR logs
        if log_entry.get("level") != "ERROR":
            return

        print(f"\n[!] New Error Detected in {log_entry.get('service')}")

        # Categorize
        category = categorize_error(
            log_entry.get("message"), log_entry.get("stack_trace")
        )
        print(f"Category: {category}")

        # Get Code Context
        code_context = get_code_context(log_entry.get("stack_trace"))
        print(
            f"Code Context Found: {'Yes' if 'Code Snippet' in code_context else 'No'}"
        )

        # AI Analysis
        print("Requesting AI Analysis...")
        solution, similar_solution = analyze_with_ai(category, log_entry, code_context)

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO logs (timestamp, service, level, message, category, solution, code_context, stack_trace, is_known_error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                log_entry.get("timestamp"),
                log_entry.get("service"),
                log_entry.get("level"),
                log_entry.get("message"),
                category,
                solution,
                code_context,
                log_entry.get("stack_trace"),
                1 if similar_solution else 0,
            ),
        )
        conn.commit()
        conn.close()
        print("Log saved to database.")

        print("\n--- AI Solution ---")
        print(solution)
        print("-------------------\n")

    except json.JSONDecodeError:
        print(f" [!] Received non-JSON message: {body}")
    except Exception as e:
        print(f" [!] Error processing log: {e}")


def main():
    init_db()
    try:
        credentials = pika.PlainCredentials("user", "password")
        parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)
        try:
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.ProbableAuthenticationError:
            print("Auth failed, trying guest/guest...")
            credentials = pika.PlainCredentials("guest", "guest")
            parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)
            connection = pika.BlockingConnection(parameters)

        channel = connection.channel()

        channel.queue_declare(queue="log_errors", durable=False)

        def callback(ch, method, properties, body):
            process_log(body.decode())

        channel.basic_consume(
            queue="log_errors", on_message_callback=callback, auto_ack=True
        )

        print(" [*] Assistant is listening for JSON logs. To exit press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError:
        print("Could not connect to RabbitMQ. Is it running?")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    main()
