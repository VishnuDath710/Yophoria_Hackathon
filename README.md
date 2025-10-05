Autonomous AI Tutor Orchestrator
This project is an intelligent middleware orchestrator built with FastAPI and LangGraph. It serves as a "brain" between a conversational AI tutor and various educational tools, designed to understand user requests, classify them into the correct tools, extract necessary parameters, and simulate API calls to those tools.

Core Features
Web Interface: A clean, responsive chat interface built with Bootstrap.

Chat History: Conversation is stored in a static chat_history.json file.

AI-Powered Tool Classification: Uses a LangGraph agent with the Gemini API to identify the most relevant tool(s) for a user's prompt.

AI-Powered Parameter Extraction: Intelligently extracts parameters for each tool based on its specific schema, the user's prompt, and the conversation history.

Mock Tool Execution: Simulates API calls to the tools and displays the raw JSON response.

Schema Validation: Uses Pydantic to define and validate the input for each tool.

Technology Stack
Backend: Python, FastAPI

Frontend: HTML, Bootstrap, JavaScript

Agent Framework: LangGraph, LangChain

LLM: Google Gemini Pro

Validation: Pydantic

Project Structure
autonomous_tutor_orchestrator/
├── app/                  # Core application logic
├── static/               # For CSS/JS files
├── templates/            # HTML templates
├── .env                  # For API keys
├── chat_history.json     # Stores conversation
├── requirements.txt      # Python dependencies
└── README.md

Setup and Installation
Clone the repository:

git clone <your-repo-url>
cd autonomous_tutor_orchestrator

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the required dependencies:

pip install -r requirements.txt

Set up your API Key:

Rename the .env.example file to .env (if you have one) or create a new .env file.

Add your Google Gemini API key to the .env file:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

Running the Application
Start the FastAPI server from the root directory using Uvicorn:

uvicorn app.main:app --reload
