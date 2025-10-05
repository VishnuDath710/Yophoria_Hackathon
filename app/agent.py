import os
from typing import TypedDict, List, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field # <-- FIX: Changed from langchain_core.pydantic_v1
from langgraph.graph import StateGraph, END
from .tools import AVAILABLE_TOOLS

# Load API key from .env file
from dotenv import load_dotenv
load_dotenv()

# --- Agent State ---
class AgentState(TypedDict):
    userInput: str
    chatHistory: list
    userInfo: dict
    classifiedTools: List[str]
    extractedParameters: dict

# --- LangGraph Nodes ---

# 1. Tool Classifier Node
class ToolClassifier(BaseModel):
    """Select the most relevant tool(s) based on the user's request."""
    tool_names: List[Literal["NoteMakerTool", "FlashcardGeneratorTool", "ConceptExplainerTool", "QuizGeneratorTool"]] = Field(
        description="The names of the tools that are most relevant to the user's prompt."
    )

def classify_tools(state: AgentState):
    """
    First node in the graph: Classifies the user's request into one or more tools.
    """
    print("--- 1. CLASSIFYING TOOLS ---")
    
    # FIX: Explicitly pass the API key from the environment variable
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    structured_llm_classifier = llm.with_structured_output(ToolClassifier)
    
    system_prompt = """You are an expert at classifying a user's request into a set of available tools.
    Based on the user's prompt and chat history, identify the most relevant tool(s) from the provided list."""
    
    prompt = f"""
    Available Tools: {', '.join(AVAILABLE_TOOLS.keys())}
    Chat History: {state['chatHistory']}
    User's Latest Prompt: {state['userInput']}
    """
    
    tool_choice_result = structured_llm_classifier.invoke([SystemMessage(content=system_prompt), prompt])
    
    print(f"    - Tools Classified: {tool_choice_result.tool_names}")
    state['classifiedTools'] = tool_choice_result.tool_names
    return state

# 2. Parameter Extractor Node
def extract_parameters(state: AgentState):
    """
    Second node: Extracts parameters for the classified tools using the tool's Pydantic schema.
    """
    print("--- 2. EXTRACTING PARAMETERS ---")
    
    # FIX: Explicitly pass the API key here as well
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    all_extracted_params = {}

    for tool_name in state['classifiedTools']:
        tool_schema = AVAILABLE_TOOLS[tool_name]["schema"]
        structured_llm_extractor = llm.with_structured_output(tool_schema)
        
        system_prompt = f"""You are an expert at extracting information. Your task is to extract parameters for the `{tool_name}` tool based on its schema.
        You must analyze the user's prompt and the chat history to find the required information.
        If a value is not found, use a sensible default that aligns with the schema's description.
        The user's personal information is provided."""

        prompt = f"""
        User Info: {state['userInfo']}
        Chat History: {state['chatHistory']}
        User's Latest Prompt: {state['userInput']}
        """
        
        extracted_data = structured_llm_extractor.invoke([SystemMessage(content=system_prompt), prompt])
        all_extracted_params[tool_name] = extracted_data.dict()
        print(f"    - Parameters for {tool_name}: {all_extracted_params[tool_name]}")

    state['extractedParameters'] = all_extracted_params
    return state

# --- Build the Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("classify_tools", classify_tools)
workflow.add_node("extract_parameters", extract_parameters)

workflow.set_entry_point("classify_tools")
workflow.add_edge("classify_tools", "extract_parameters")
workflow.add_edge("extract_parameters", END)

app_graph = workflow.compile()