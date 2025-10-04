# app/tools.py
from .models import FlashcardGeneratorInput
import json

def flashcard_generator_tool(input_data: FlashcardGeneratorInput) -> str:
    """Mock function for the Flashcard Generator Tool."""
    print(f"--- Calling Flashcard Generator Tool with topic: {input_data.topic} ---")
    
    # Simulate adapting to the user's state [cite: 96]
    adaptation_details = f"Flashcards adapted for a {input_data.user_info.emotional_state_summary.lower()} student at mastery level {input_data.user_info.mastery_level_summary.split(':')[0]}."

    # Mock success response [cite: 395]
    mock_response = {
        "flashcards": [
            {
                "title": f"Key Term in {input_data.topic}",
                "question": "What is the primary function of chlorophyll?",
                "answer": "To absorb light energy for photosynthesis.",
                "example": "Found in the chloroplasts of plant cells."
            } for _ in range(input_data.count)
        ],
        "topic": input_data.topic,
        "adaptation_details": adaptation_details,
        "difficulty": input_data.difficulty
    }
    
    return json.dumps(mock_response, indent=2)

def note_maker_tool(input_data: dict) -> str:
    """Placeholder mock function for the Note Maker Tool."""
    print(f"--- Calling Note Maker Tool with topic: {input_data.get('topic')} ---")
    return json.dumps({"status": "success", "notes": "Your notes on the topic are here."})

# A dictionary to easily find tools by name
available_tools = {
    "flashcard_generator": flashcard_generator_tool,
    "note_maker": note_maker_tool,
}