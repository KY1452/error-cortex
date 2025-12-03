
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os
import requests
import json
import sys

# Add parent directory to path to import consumer modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from consumer.rag import RAGEngine

app = FastAPI()

# Configure templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
DB_PATH = os.path.join(PROJECT_ROOT, "logs.db")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# Initialize RAG for writing feedback
rag_engine = RAGEngine()


class ChatRequest(BaseModel):
    file_path: str
    line_number: int
    code_snippet: str
    question: str


def get_logs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()
    return logs


def get_file_tree(start_path):
    tree = []
    for item in os.listdir(start_path):
        if item.startswith(".") or item == "__pycache__" or item == "logs.db":
            continue

        path = os.path.join(start_path, item)
        is_dir = os.path.isdir(path)

        node = {
            "name": item,
            "path": path,
            "type": "directory" if is_dir else "file",
            "children": get_file_tree(path) if is_dir else None,
        }
        tree.append(node)

    # Sort directories first, then files
    tree.sort(key=lambda x: (x["type"] == "file", x["name"]))
    return tree


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/logs")
async def api_logs():
    logs = get_logs()
    result = []
    for row in logs:
        log_dict = dict(row)
        # Try to parse the solution as JSON if it looks like it
        try:
            if log_dict["solution"] and log_dict["solution"].strip().startswith("{"):
                log_dict["solution_json"] = json.loads(log_dict["solution"])
            else:
                log_dict["solution_json"] = None
        except json.JSONDecodeError:
            log_dict["solution_json"] = None
        result.append(log_dict)
    return result


@app.get("/api/files")
async def api_files():
    return get_file_tree(PROJECT_ROOT)


@app.get("/api/files/content")
async def api_file_content(path: str):
    # Security check: ensure path is within project root
    if not os.path.abspath(path).startswith(os.path.abspath(PROJECT_ROOT)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(path) or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(path, "r") as f:
        return {"content": f.read()}


@app.post("/api/chat")
async def api_chat(chat_req: ChatRequest):
    prompt = f"""
    Act as a senior developer. I have a question about a specific line of code.
    
    File: {chat_req.file_path}
    Line: {chat_req.line_number}
    
    Code Snippet:
    {chat_req.code_snippet}
    
    Question: {chat_req.question}
    
    Please provide a concise and helpful answer.
    """

    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return {"response": response.json().get("response", "No response")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New endpoint: apply a code fix returned by the AI
@app.post("/feedback/{log_id}")
async def mark_as_fixed(log_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE id = ?", (log_id,))
    log = c.fetchone()
    conn.close()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # Store in RAG
    # We use the stack_trace if available, otherwise fallback to category/context
    stack_trace = log["stack_trace"] if "stack_trace" in log.keys() else log["category"]
    
    rag_engine.add_solution(
        error_msg=log["message"],
        stack_trace=stack_trace,
        solution=log["solution"]
    )
    
    return {"status": "success", "message": "Solution stored in memory."}

