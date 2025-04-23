import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GroqService:
    # Model categories and their corresponding models
    MODELS = {
        'REASONING': {
            'qwen-qwq': 'Qwen QwQ',
            'deepseek-r1-distill-qwen': 'DeepSeek R1 Distill Qwen',
            'deepseek-r1-distill-llama': 'DeepSeek R1 Distill Llama'
        },
        'TEXT_TO_TEXT': {
            'llama-4': 'Llama 4',
            'llama-3': ['3.3', '3.2', '3.1', '3.0'],
            'qwen-2.5': 'Qwen 2.5',
            'gemma-2': 'Gemma 2'
        },
        'VISION': {
            'llama-4': 'Llama 4',
            'llama-3.2': 'Llama 3.2'
        },
        'MULTILINGUAL': {
            'llama-4': 'Llama 4',
            'llama-3': ['3.3', '3.2', '3.1', '3.0'],
            'mistral-saba': 'Mistral Saba',
            'gemma-2': 'Gemma 2',
            'whisper-large-v3': 'Whisper Large v3'
        },
        'TEXT_TO_SPEECH': {
            'playai-dialog': 'PlayAI Dialog'
        },
        'SPEECH_TO_TEXT': {
            'whisper-large-v3': 'Whisper Large v3',
            'whisper-large-turbo': 'Whisper Large Turbo',
            'whisper-distil': 'Whisper Distil'
        },
        'FUNCTION_CALLING': {
            'llama-4': 'Llama 4',
            'llama-3.3-70b': 'Llama 3.3 70B',
            'qwen-qwq': 'Qwen QwQ'
        },
        'CODING': {
            'qwen-2.5-coder': 'Qwen 2.5 Coder'
        },
        'SAFETY': {
            'llama-guard': 'Llama Guard'
        }
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_appropriate_model(self, task_type):
        """
        Get the most appropriate model for a given task type
        """
        if task_type in self.MODELS:
            # Default to the first model in each category
            models = self.MODELS[task_type]
            return next(iter(models.keys()))
        return 'llama-4'  # Default to Llama 4 if task type not specified

    def complete_prompt(self, prompt: str, task_type: str = None, specific_model: str = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Complete a prompt using the appropriate model
        """
        try:
            # Use specific model if provided, otherwise get appropriate model for task
            model = specific_model if specific_model else self.get_appropriate_model(task_type)
            endpoint = f"{self.base_url}/chat/completions"
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
            
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
        Translate content using multilingual models
        """
        model = self.get_appropriate_model('MULTILINGUAL')
        prompt = f"""
        Translate the following content to {target_language}:
        
        {content}
        """
        
        return self.complete_prompt(prompt, specific_model=model)