# app/models.py
from pydantic import BaseModel, Field
from typing import List, Literal

# Common User Info object used by all tools [cite: 585]
class UserInfo(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the student")
    name: str = Field(..., description="Student's full name")
    grade_level: str = Field(..., description="Student's current grade level")
    learning_style_summary: str = Field(..., description="Summary of student's preferred learning style")
    emotional_state_summary: str = Field(..., description="Current emotional state of the student")
    mastery_level_summary: str = Field(..., description="Current mastery level description")

# Input schema for the Flashcard Generator Tool [cite: 307]
class FlashcardGeneratorInput(BaseModel):
    user_info: UserInfo
    topic: str
    count: int = Field(..., ge=1, le=20) # ge=greater than or equal to, le=less than or equal to
    difficulty: Literal["easy", "medium", "hard"]
    subject: str
    include_examples: bool = True

# Main request body for your orchestrator endpoint
class OrchestratorRequest(BaseModel):
    user_message: str
    user_info: UserInfo
    chat_history: list = [] # Simplified for now