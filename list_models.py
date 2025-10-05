import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment file
load_dotenv()

# Configure the API key
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error configuring API key: {e}")
    exit()

print("Available models that support 'generateContent':")
print("-" * 45)

# List all models and filter for the ones you can use for chat/text
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)