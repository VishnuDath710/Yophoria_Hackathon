import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .schemas import UserInfo
from .agent import app_graph
from .tools import AVAILABLE_TOOLS

# --- App Setup ---
app = FastAPI(title="AI Tutor Orchestrator")

# Mount static files (for JS)
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Setup templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_path)

# Path to the chat history file
CHAT_HISTORY_FILE = Path(__file__).parent.parent / "chat_history.json"

# --- Helper Functions ---
def read_chat_history():
    if not CHAT_HISTORY_FILE.exists():
        return []
    with open(CHAT_HISTORY_FILE, "r") as f:
        return json.load(f)

def write_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# --- FastAPI Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serves the main chat HTML page."""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/add-tool", response_class=HTMLResponse)
async def get_add_tool_page(request: Request):
    """Serves the page for adding new tools."""
    return templates.TemplateResponse("add_tool.html", {"request": request})

@app.get("/history", response_class=JSONResponse)
async def get_history():
    """Endpoint to fetch the current chat history."""
    return JSONResponse(content=read_chat_history())

@app.post("/clear-chat", response_class=JSONResponse)
async def clear_chat():
    """Endpoint to clear the chat history."""
    write_chat_history([])
    return JSONResponse(content={"message": "Chat history cleared"})

@app.post("/chat", response_class=JSONResponse)
async def chat_endpoint(userInput: str = Form(...)):
    """
    Main endpoint to process user messages.
    It runs the LangGraph agent to get classified tools and extracted parameters.
    """
    history = read_chat_history()
    history.append({"role": "user", "content": userInput})

    # For this prototype, we use a default user object.
    # In a real app, this would come from a database.
    user_info = UserInfo().dict()

    # Run the LangGraph agent
    agent_input = {
        "userInput": userInput,
        "chatHistory": history,
        "userInfo": user_info
    }
    agent_result = app_graph.invoke(agent_input)

    # Prepare response for the frontend
    response_data = {
        "classifiedTools": agent_result.get("classifiedTools", []),
        "extractedParameters": agent_result.get("extractedParameters", {})
    }
    
    # Add a placeholder assistant message to history
    history.append({
        "role": "assistant",
        "content": f"I have identified {len(response_data['classifiedTools'])} relevant tool(s) for your request."
    })
    write_chat_history(history)

    return JSONResponse(content=response_data)

@app.post("/call-tool/{tool_name}", response_class=JSONResponse)
async def call_tool_endpoint(tool_name: str, request: Request):
    """
    Endpoint to simulate calling a selected tool with its extracted parameters.
    """
    if tool_name not in AVAILABLE_TOOLS:
        return JSONResponse(status_code=404, content={"error": "Tool not found"})

    try:
        # Get the parameters sent from the frontend
        params_dict = await request.json()
        
        # Get tool function and schema
        tool_info = AVAILABLE_TOOLS[tool_name]
        tool_function = tool_info["function"]
        pydantic_schema = tool_info["schema"]
        
        # Validate the parameters against the Pydantic model
        validated_params = pydantic_schema(**params_dict)

        # Execute the tool
        result = tool_function(validated_params)
        return JSONResponse(content=json.loads(result))

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": "Invalid parameters", "details": str(e)})
