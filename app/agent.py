# app/agent.py
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from .tools import available_tools

# This will be the state of our graph, tracking the conversation
class AgentState(TypedDict):
    user_message: str
    user_info: dict
    tool_name: str
    tool_parameters: dict
    tool_output: str

# This is a placeholder for your router.
# In a real system, an LLM would make this decision.
def tool_router(state: AgentState) -> Literal["flashcard_generator", "note_maker", END]:
    """Simple router to decide which tool to use based on keywords."""
    message = state['user_message'].lower()
    if "flashcard" in message or "quiz me" in message:
        return "flashcard_generator"
    if "note" in message or "summarize" in message:
        return "note_maker"
    return END

# This is a placeholder for parameter extraction.
# This is the most important part you'll build out with an LLM. [cite: 708]
def parameter_extractor(state: AgentState) -> AgentState:
    """
    Placeholder for the intelligent parameter extraction engine.
    For now, it uses simple logic.
    """
    print("--- Extracting Parameters ---")
    message = state['user_message']
    
    # TODO: Replace this with an LLM call using LangChain's tool/function calling
    # to extract parameters from `message` based on the tool's schema.
    # For now, we'll hardcode some values for the demo.
    
    if state["tool_name"] == "flashcard_generator":
        params = {
            "user_info": state["user_info"],
            "topic": "Photosynthesis", # Inferred from message
            "count": 5, # Inferred from message
            "difficulty": "easy", # Inferred from emotional state "confused"
            "subject": "Biology" # Inferred from topic
        }
        state["tool_parameters"] = params
        
    # Add logic for other tools here
    else:
        state["tool_parameters"] = {}

    return state

def tool_executor(state: AgentState) -> AgentState:
    """Executes the chosen tool with the extracted parameters."""
    print(f"--- Executing Tool: {state['tool_name']} ---")
    tool_function = available_tools.get(state["tool_name"])
    
    if tool_function:
        # Here you would use Pydantic models to validate before calling
        # For this example, the tool function itself takes the dict
        # In a robust solution, you'd parse `state["tool_parameters"]` into the correct Pydantic model.
        output = tool_function(state["tool_parameters"])
        state["tool_output"] = output
    else:
        state["tool_output"] = '{"error": "Tool not found"}'
        
    return state


# Define the graph workflow
workflow = StateGraph(AgentState)

workflow.add_node("parameter_extractor", parameter_extractor)
workflow.add_node("tool_executor", tool_executor)

# The entry point is the router
workflow.set_conditional_entry_point(
    tool_router,
    {
        "flashcard_generator": "parameter_extractor",
        "note_maker": "parameter_extractor", # Add other tools here
        END: END
    }
)

# After extracting parameters, we always execute the tool
workflow.add_edge("parameter_extractor", "tool_executor")
workflow.add_edge("tool_executor", END)

# Compile the graph into a runnable app
app_graph = workflow.compile()