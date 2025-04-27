import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any
from requests.exceptions import RequestException, Timeout
import base64

# Load environment variables from .env file
load_dotenv()

class GroqService:
    # Model categories and their corresponding models
    MODELS = {
        'REASONING': {
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
            'qwen-qwq': 'Qwen QwQ',
            'deepseek-r1-distill-qwen': 'DeepSeek R1 Distill Qwen',
            'deepseek-r1-distill-llama': 'DeepSeek R1 Distill Llama'
        },
        'TEXT_TO_TEXT': {
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
            'llama-4': 'Llama 4',
            'llama-3': ['3.3', '3.2', '3.1', '3.0'],
            'qwen-2.5': 'Qwen 2.5',
            'gemma-2': 'Gemma 2'
        },
        'VISION': {
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
            'llama-4': 'Llama 4',
            'llama-3.2': 'Llama 3.2'
        },
        'MULTILINGUAL': {
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
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
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
            'llama-4': 'Llama 4',
            'llama-3.3-70b': 'Llama 3.3 70B',
            'qwen-qwq': 'Qwen QwQ'
        },
        'CODING': {
            'llama-3.3-70b-versatile': 'Llama 3.3 70B Versatile',
            'qwen-2.5-coder': 'Qwen 2.5 Coder'
        },
        'SAFETY': {
            'llama-guard': 'Llama Guard'
        }
    }

    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        # Configure session with retries and backoff
        retry_strategy = requests.adapters.Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[408, 429, 500, 502, 503, 504]  # status codes to retry on
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _make_request(self, endpoint: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Make request to Groq API with proper error handling"""
        try:
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except Timeout as exc:
            print("Request to Groq API timed out")
            raise RuntimeError("Request timed out. Please try again.") from exc
        except RequestException as e:
            print(f"Error calling Groq API: {str(e)}")
            if isinstance(e, requests.exceptions.ConnectionError):
                raise RuntimeError("Network connection error. Please check your internet connection.") from e
            elif isinstance(e, requests.exceptions.HTTPError):
                if e.response.status_code == 429:
                    raise RuntimeError("Rate limit exceeded. Please try again later.") from e
                elif e.response.status_code >= 500:
                    raise RuntimeError("Groq API service error. Please try again later.") from e
            raise RuntimeError(f"API request failed: {str(e)}") from e

    def get_appropriate_model(self, task_type: str = None) -> str:
        """Get the most appropriate model for a given task"""
        if not task_type or task_type not in self.MODELS:
            return "llama-3.3-70b-versatile"  # Default model
        
        # Return the first available model for the task type
        for model_id in self.MODELS[task_type]:
            return model_id
        
        return "llama-3.3-70b-versatile"  # Fallback to default

    def complete_prompt(self, prompt: str, task_type: str = None, specific_model: str = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """Complete a prompt using the appropriate model"""
        try:
            model = specific_model if specific_model else self.get_appropriate_model(task_type)
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful educational AI assistant. When analyzing content, provide detailed, insightful responses that help users understand the material better. Break down complex topics, offer examples, and suggest related concepts to explore."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            print(f"Calling Groq API with model: {model}")
            # Use a longer timeout for content analysis
            return self._make_request("chat/completions", payload, timeout=60)
            
        except Exception as e:
            print(f"Error in complete_prompt: {str(e)}")
            raise RuntimeError(f"Failed to process request: {str(e)}") from e

    def process_math_problem(self, problem_text: str, subject: str = "mathematics") -> Dict[str, Any]:
        """Process a math problem with step-by-step analysis"""
        prompt = f"""Analyze this {subject} problem step by step:
        {problem_text}
        
        Please provide:
        1. Step-by-step solution
        2. Key concepts involved
        3. Similar practice problems
        4. Learning resources
        """
        return self.complete_prompt(prompt, task_type='REASONING')
    
    def translate_content(self, content: str, target_language: str) -> Dict[str, Any]:
        """Translate content to target language"""
        prompt = f"""Translate the following content to {target_language}:
        {content}
        
        Please ensure:
        1. Natural and fluent translation
        2. Preserve technical terms accurately
        3. Maintain the original meaning
        """
        return self.complete_prompt(prompt, task_type='MULTILINGUAL')

    def analyze_file_content(self, content: str, file_type: str, context: str = None) -> Dict[str, Any]:
        """Analyze file content with enhanced educational focus"""
        try:
            system_prompt = """You are an expert educational AI assistant specializing in analyzing content and providing 
            insightful explanations. Focus on making complex topics accessible while maintaining academic rigor. 
            Break down concepts clearly and suggest practical applications and learning opportunities."""

            user_prompt = f"""Please analyze this {file_type} content carefully and provide:

1. Summary: A clear overview of the main content
2. Key Concepts: Important ideas and principles identified
3. Educational Value:
   - Learning objectives that can be derived
   - Skills or knowledge this content helps develop
   - How this connects to broader educational topics
4. Analysis: 
   - Critical insights and patterns
   - Relationships between concepts
   - Potential implications or applications
5. Learning Suggestions:
   - Study questions to deepen understanding
   - Related topics to explore
   - Practical exercises or activities
6. Additional Resources:
   - Suggested supplementary materials
   - Related fields of study
   - Tools or methods for further learning

Content to analyze:
{content}"""

            if context:
                user_prompt += f"\n\nAdditional context from the user: {context}\nPlease incorporate this context into your analysis."

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            
            payload = {
                "model": self.get_appropriate_model('REASONING'),
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            # Use a longer timeout for file analysis
            return self._make_request("chat/completions", payload, timeout=120)
            
        except Exception as e:
            print(f"Error in analyze_file_content: {str(e)}")
            raise RuntimeError(f"Failed to analyze content: {str(e)}") from e

    def analyze_image(self, image_data, query: str = "What's in this image?", is_url: bool = False) -> Dict[str, Any]:
        """Analyze an image using Groq's vision model"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data if is_url else f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # Updated model name
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }
            
            return self._make_request("chat/completions", payload, timeout=60)
            
        except Exception as e:
            print(f"Error in analyze_image: {str(e)}")
            raise RuntimeError(f"Failed to analyze image: {str(e)}") from e

    def analyze_local_image(self, image_path: str, query: str = "What's in this image?") -> Dict[str, Any]:
        """Analyze a local image file"""
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            return self.analyze_image(base64_image, query, is_url=False)
        except Exception as e:
            print(f"Error reading local image: {str(e)}")
            raise RuntimeError(f"Failed to process local image: {str(e)}") from e