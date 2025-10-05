from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- Common Models ---

class UserInfo(BaseModel):
    """Consistent User Info object for all tools."""
    user_id: str = "student123"
    name: str = "Alex"
    grade_level: str = "10"
    learning_style_summary: str = "Prefers visual aids and examples"
    emotional_state_summary: str = "Curious and engaged"
    mastery_level_summary: str = "Level 5: Developing competence"

class ChatMessage(BaseModel):
    """Represents a single message in the chat history."""
    role: Literal["user", "assistant"]
    content: str

# --- Tool Specific Input Schemas ---

class NoteMakerToolInput(BaseModel):
    user_info: UserInfo = Field(default_factory=UserInfo)
    chat_history: List[ChatMessage]
    topic: str = Field(..., description="The main topic for note generation, e.g., 'Water Cycle'")
    subject: str = Field(..., description="Academic subject area, e.g., 'Environmental Science'")
    note_taking_style: Literal["outline", "bullet_points", "narrative", "structured"]
    include_examples: bool = True
    include_analogies: bool = False

class FlashcardGeneratorToolInput(BaseModel):
    user_info: UserInfo = Field(default_factory=UserInfo)
    topic: str = Field(..., description="The topic for flashcard generation, e.g., 'Photosynthesis'")
    count: int = Field(..., ge=1, le=20, description="Number of flashcards to generate")
    difficulty: Literal["easy", "medium", "hard"]
    subject: str = Field(..., description="Academic subject area, e.g., 'Biology'")
    include_examples: bool = True

class ConceptExplainerToolInput(BaseModel):
    user_info: UserInfo = Field(default_factory=UserInfo)
    chat_history: List[ChatMessage]
    concept_to_explain: str = Field(..., description="The specific concept to explain, e.g., 'mitosis'")
    current_topic: str = Field(..., description="Broader topic context, e.g., 'Cell Biology'")
    desired_depth: Literal["basic", "intermediate", "advanced", "comprehensive"]

class QuizGeneratorToolInput(BaseModel):
    """Schema for a hypothetical Quiz Generator Tool."""
    user_info: UserInfo = Field(default_factory=UserInfo)
    topic: str = Field(..., description="The main topic for the quiz")
    subject: str = Field(..., description="The academic subject of the quiz")
    question_count: int = Field(10, ge=5, le=25)
    difficulty: Literal["beginner", "intermediate", "expert"] = "intermediate"
    question_types: List[Literal["multiple_choice", "true_false", "short_answer"]] = ["multiple_choice"]
