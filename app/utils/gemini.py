from google import generativeai
from dotenv import load_dotenv
import os

load_dotenv()

client = generativeai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = generativeai.GenerativeModel('gemini-2.5-flash')

# ✅ Function to generate content from prompt
def generate_content(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text  # or handle other formats if needed
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")





