import os
from typing import TypedDict, List, Literal, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
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
    extractedParameters: Dict[str, Any]
    completeTools: Dict[str, Any]
    incompleteTools: Dict[str, List[str]]
    clarificationQuestion: str

# --- LangGraph Nodes ---

# 1. Tool Classifier Node
class ToolClassifier(BaseModel):
    tool_names: List[Literal["NoteMakerTool", "FlashcardGeneratorTool", "ConceptExplainerTool", "QuizGeneratorTool"]] = Field(
        description="The names of the tools that are most relevant to the user's prompt."
    )

def classify_tools(state: AgentState):
    """Classifies the user's request into one or more tools using the specified prompt."""
    print("--- 1. CLASSIFYING TOOLS ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))
    structured_llm_classifier = llm.with_structured_output(ToolClassifier)
    
    # Using the exact prompt structure you requested
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
    """Extracts adaptive parameters for the tools based on the dynamic user state."""
    print("--- 2. EXTRACTING PARAMETERS ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))
    all_extracted_params = {}
    system_prompt = """You are an expert at extracting parameters based on a tool's schema, adapting your response to the user's state.
    CRITICAL: Use the provided 'User Info' to adapt your response (e.g., 'Confused' -> 'easy' difficulty). If a parameter is not mentioned, do not invent it."""
    for tool_name in state['classifiedTools']:
        tool_schema = AVAILABLE_TOOLS[tool_name]["schema"]
        structured_llm_extractor = llm.with_structured_output(tool_schema)
        prompt = f"User Info: {state['userInfo']}\nChat History: {state['chatHistory']}\nUser's Latest Prompt: {state['userInput']}"
        extracted_data = structured_llm_extractor.invoke([SystemMessage(content=system_prompt), prompt])
        all_extracted_params[tool_name] = extracted_data.dict()
        print(f"    - Parameters for {tool_name}: {extracted_data.dict()}")
    state['extractedParameters'] = all_extracted_params
    return state

# 3. Validation Node
def validate_parameters(state: AgentState):
    """Checks if all required parameters have been extracted for each tool."""
    print("--- 3. VALIDATING PARAMETERS ---")
    complete_tools = {}
    incomplete_tools = {}
    for tool_name, params in state['extractedParameters'].items():
        schema_model = AVAILABLE_TOOLS[tool_name]["schema"]
        required_fields = [field for field, model_field in schema_model.model_fields.items() if model_field.is_required()]
        missing_fields = [field for field in required_fields if params.get(field) is None or str(params.get(field)).strip() == ""]
        if not missing_fields:
            complete_tools[tool_name] = params
            print(f"    - {tool_name}: VALID")
        else:
            incomplete_tools[tool_name] = missing_fields
            print(f"    - {tool_name}: INVALID, Missing: {missing_fields}")
    state['completeTools'] = complete_tools
    state['incompleteTools'] = incomplete_tools
    return state

# 4. "Ask User" Node
def request_missing_info(state: AgentState):
    """Generates a friendly question to ask the user for missing information."""
    print("--- 4. GENERATING CLARIFICATION QUESTION ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=os.getenv("GEMINI_API_KEY"))
    missing_info_str = "\n".join([f"- For the {tool.replace('Tool', '')}, I'm missing: {', '.join(fields)}." for tool, fields in state['incompleteTools'].items()])
    prompt = f"You are a helpful AI assistant. Ask the user for the missing information in a single, friendly question. Be concise.\nInformation you are missing:\n{missing_info_str}"
    response = llm.invoke(prompt)
    state['clarificationQuestion'] = response.content
    print(f"    - Generated Question: {response.content}")
    return state

# 5. Conditional Router
def decide_next_step(state: AgentState) -> Literal["request_info", "end_with_tools", "end_with_clarification"]:
    """Decides the next step based on parameter validation."""
    print("--- 5. DECIDING NEXT STEP ---")
    if state.get('completeTools'):
        print("    - Decision: End with tools.")
        return "end_with_tools"
    elif state.get('incompleteTools'):
        print("    - Decision: Request more info.")
        return "request_info"
    print("    - Decision: End with clarification (no tools found).")
    return "end_with_clarification"

# --- Build the Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("classify_tools", classify_tools)
workflow.add_node("extract_parameters", extract_parameters)
workflow.add_node("validate_parameters", validate_parameters)
workflow.add_node("request_missing_info", request_missing_info)
workflow.set_entry_point("classify_tools")
workflow.add_edge("classify_tools", "extract_parameters")
workflow.add_edge("extract_parameters", "validate_parameters")
workflow.add_conditional_edges("validate_parameters", decide_next_step, {
    "request_info": "request_missing_info",
    "end_with_tools": END,
    "end_with_clarification": END
})
workflow.add_edge("request_missing_info", END)
app_graph = workflow.compile()

