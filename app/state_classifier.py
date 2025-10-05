import os
import json
from pathlib import Path
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- State Definitions ---

class UserState(BaseModel):
    """A model to represent the classified state of the user."""
    teaching_style: Literal[
        "Direct", "Socratic", "Visual", "Flipped Classroom"
    ] = Field(description="Infer the best teaching style for the next turn based on the conversation.")
    
    emotional_state: Literal[
        "Focused", "Anxious", "Confused", "Tired"
    ] = Field(description="Infer the user's current emotional state from their language.")
    
    mastery_level: Literal[
        "Levels 1-3: Foundation building",
        "Levels 4-6: Developing competence",
        "Levels 7-9: Advanced application",
        "Level 10: Full mastery"
    ] = Field(description="Infer the user's mastery level of the topic discussed.")

# --- Database Interaction ---

USER_STATE_FILE = Path(__file__).parent / "db" / "user_state.json"

def get_current_state() -> dict:
    """Reads the current user state from the JSON file."""
    if not USER_STATE_FILE.exists():
        # Return a default state if the file doesn't exist
        return {
            "teaching_style": "Direct",
            "emotional_state": "Focused",
            "mastery_level": "Levels 4-6: Developing competence"
        }
    with open(USER_STATE_FILE, "r") as f:
        return json.load(f)

def save_current_state(state: dict):
    """Saves the user state to the JSON file."""
    with open(USER_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# --- State Classification Logic ---

def update_user_state(chat_history: list) -> dict:
    """
    Analyzes chat history to classify and update the user's state.
    This runs in the background after every message.
    """
    print("--- A. CLASSIFYING USER STATE ---")
    
    # Don't run on an empty history
    if not chat_history:
        return get_current_state()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.5, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    structured_llm = llm.with_structured_output(UserState)
    
    current_state = get_current_state()
    
    prompt = f"""
    Based on the following conversation history and the user's most recent messages, classify their current state.
    The user's previous state was: {current_state}

    Conversation History:
    {json.dumps(chat_history, indent=2)}
    """
    
    try:
        updated_state = structured_llm.invoke(prompt)
        new_state_dict = updated_state.dict()
        save_current_state(new_state_dict)
        print(f"    - User state updated: {new_state_dict}")
        return new_state_dict
    except Exception as e:
        print(f"    - Error updating user state: {e}. Using previous state.")
        return current_state