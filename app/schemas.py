from pydantic import BaseModel, Field
from typing import List, Literal

# --- Common Models ---

class UserInfo(BaseModel):
    """
    Represents the student's dynamic profile.
    This data is now classified and updated after every message.
    """
    user_id: str = "student123"
    name: str = "Alex"
    teaching_style: str
    emotional_state: str
    mastery_level: str

class ChatMessage(BaseModel):
    """Represents a single message in the chat history."""
    role: Literal["user", "assistant"]
    content: str

# --- Tool Specific Input Schemas ---
# (The rest of the file remains the same)

class NoteMakerToolInput(BaseModel):
    user_info: UserInfo
    chat_history: List[ChatMessage]
    topic: str
    subject: str
    note_taking_style: Literal["outline", "bullet_points", "narrative", "structured"]
    
class FlashcardGeneratorToolInput(BaseModel):
    user_info: UserInfo
    topic: str
    count: int = Field(..., ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"]
    subject: str

class ConceptExplainerToolInput(BaseModel):
    user_info: UserInfo
    chat_history: List[ChatMessage]
    concept_to_explain: str
    current_topic: str
    desired_depth: Literal["basic", "intermediate", "advanced", "comprehensive"]

class QuizGeneratorToolInput(BaseModel):
    user_info: UserInfo
    topic: str
    subject: str
    question_count: int = Field(10, ge=5, le=25)
    difficulty: Literal["beginner", "intermediate", "expert"]
    question_types: List[Literal["multiple_choice", "true_false", "short_answer"]]