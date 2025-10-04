# app/main.py
from fastapi import FastAPI
from .models import OrchestratorRequest
from .agent import app_graph, AgentState

app = FastAPI(
    title="Autonomous AI Tutor Orchestrator",
    description="An intelligent middleware to connect an AI tutor with educational tools."
)

@app.post("/orchestrate")
async def orchestrate(request: OrchestratorRequest):
    """
    This endpoint receives a student's message and orchestrates the tool execution.
    """
    # The input for our LangGraph agent
    initial_state: AgentState = {
        "user_message": request.user_message,
        "user_info": request.user_info.model_dump(),
        "tool_name": "", # This will be set by the router
        "tool_parameters": {},
        "tool_output": ""
    }
    
    # Run the graph
    final_state = app_graph.invoke(initial_state)
    
    return {"response": final_state.get("tool_output", "No tool was executed.")}

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Tutor Orchestrator API"}