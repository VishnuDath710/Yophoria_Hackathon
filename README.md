# Autonomous AI Tutor Orchestrator

[cite_start]This project is an intelligent middleware orchestrator built for the **Yophoria Innovation Challenge**[cite: 3]. [cite_start]It acts as a "brain" between a conversational AI tutor and various educational tools (like flashcard generators, note makers, etc.)[cite: 14].

The system is designed to understand a student's request from a natural language conversation, determine the appropriate educational tool, intelligently extract the required parameters, and execute the tool.

## Core Functionality

* [cite_start]**Context Analysis:** Parses conversation history to identify educational intent[cite: 47].
* [cite_start]**Intelligent Parameter Extraction:** Extracts entities like topics, subjects, and difficulty levels from the conversation to fill tool requirements[cite: 49].
* [cite_start]**Tool Orchestration:** Manages API calls to multiple educational tools, handles validation, and processes responses[cite: 54, 55].
* [cite_start]**Scalable Architecture:** Designed to be extensible for integrating 80+ tools[cite: 24].

## Technology Stack

* [cite_start]**Backend:** Python 3.10+ with FastAPI [cite: 39]
* [cite_start]**Agent Framework:** LangGraph and LangChain [cite: 40]
* **Validation:** Pydantic

## Project Structure
autonomous_tutor_orchestrator/
├── app/
│   ├── init.py
│   ├── main.py
│   ├── models.py
│   ├── agent.py
│   └── tools.py
├── requirements.txt
└── README.md

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd autonomous_tutor_orchestrator
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1.  Start the FastAPI server using Uvicorn:
    ```sh
    uvicorn app.main:app --reload
    ```
2.  The application will be running at `http://127.0.0.1:8000`.

## How to Use

Once the server is running, you can access the interactive API documentation (Swagger UI) by navigating to:

**`http://127.0.0.1:8000/docs`**

You can test the `/orchestrate` endpoint directly from the documentation.

### Example Request Body

Here is an example JSON payload to send to the `/orchestrate` endpoint:

```json
{
  "user_message": "I'm confused, can you make some flashcards for me about photosynthesis?",
  "user_info": {
    "user_id": "student123",
    "name": "Alex",
    "grade_level": "10",
    "learning_style_summary": "Prefers visual aids and examples",
    "emotional_state_summary": "Confused but motivated",
    "mastery_level_summary": "Level 3: Building foundation"
  },
  "chat_history": []
}