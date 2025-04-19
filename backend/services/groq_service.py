import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GroqService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def complete_prompt(self, prompt: str, model: str = "llama3-70b-8192", max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Send a prompt to Groq for completion
        """
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling Groq API: {e}")
            return {"error": str(e)}
    
    def process_math_problem(self, problem_text: str, subject: str = "mathematics") -> Dict[str, Any]:
        """
        Process a math or subject-specific problem and return explanation
        """
        prompt = f"""
        Subject: {subject}
        Problem: {problem_text}
        
        Please:
        1. Solve this problem step-by-step
        2. Explain the key concepts involved
        3. Provide a final answer
        4. Suggest similar practice problems
        """
        
        return self.complete_prompt(prompt)
    
    def translate_content(self, content: str, target_language: str) -> Dict[str, Any]:
        """
        Translate content to the specified language
        """
        prompt = f"""
        Translate the following content to {target_language}:
        
        {content}
        """
        
        return self.complete_prompt(prompt)