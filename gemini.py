import google.generativeai as genai
import os

class GeminiAPI:
    def __init__(self):
        # Configure with your actual API key
        self.api_key = os.getenv('GEMINI_API_KEY', "AIzaSyC3jNkMe6_5vKW_laWoMgryufd-YNauvtE")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request."