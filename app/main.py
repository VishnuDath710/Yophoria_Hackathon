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
from app.state_classifier import update_user_state 
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



@app.get("/history", response_class=JSONResponse)
async def get_history():
    """Endpoint to fetch the current chat history."""
    return JSONResponse(content=read_chat_history())

@app.post("/clear-chat", response_class=JSONResponse)
async def clear_chat():
    """Endpoint to clear the chat history."""
    write_chat_history([])
    return JSONResponse(content={"message": "Chat history cleared"})

# --- Endpoints ---
@app.post("/chat", response_class=JSONResponse)
async def chat_endpoint(userInput: str = Form(...)):
    history = read_chat_history()
    history.append({"role": "user", "content": userInput})
    write_chat_history(history)

    user_state = update_user_state(history)
    user_info_data = UserInfo(user_id="student123", name="Alex", **user_state).dict()

    agent_input = { "userInput": userInput, "chatHistory": history, "userInfo": user_info_data }
    agent_result = app_graph.invoke(agent_input)

    response_data = {}
    assistant_message = ""

    if agent_result.get("completeTools"):
        complete_tools = agent_result["completeTools"]
        tool_names = list(complete_tools.keys())
        
        # FIX: The assistant message now correctly lists the tool names.
        # It also cleans them up for better readability (e.g., "NoteMakerTool" -> "Note Maker").
        display_names = [name.replace('Tool', '') for name in tool_names]
        assistant_message = f"I've identified these tools for you: {', '.join(display_names)}."
        
        response_data = {"classifiedTools": tool_names, "extractedParameters": complete_tools}
    elif agent_result.get("clarificationQuestion"):
        assistant_message = agent_result["clarificationQuestion"]
        response_data = {"clarification_question": assistant_message}
    else:
        assistant_message = "I'm not sure how to help with that. Could you try rephrasing your request?"
        response_data = {"clarification_question": assistant_message}

    history.append({"role": "assistant", "content": assistant_message})
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
