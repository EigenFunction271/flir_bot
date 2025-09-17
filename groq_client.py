import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from config import Config

class GroqClient:
    """Client for interacting with Groq GPT OSS API"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = Config.GROQ_BASE_URL
        self.models = Config.GROQ_MODELS
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
    
    async def generate_response(
        self, 
        user_message: str, 
        system_prompt: str, 
        model_type: str = "fast",
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate a response using Groq GPT OSS
        
        Args:
            user_message: The user's input message
            system_prompt: The system prompt for the character
            model_type: Either "fast" (20B) or "quality" (120B)
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if model_type not in self.models:
            raise ValueError(f"Invalid model type: {model_type}. Must be 'fast' or 'quality'")
        
        model = self.models[model_type]
        temperature = temperature or Config.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or Config.MAX_RESPONSE_LENGTH
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Groq API error {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            raise Exception("Groq API request timed out")
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test if the Groq API connection is working"""
        try:
            response = await self.generate_response(
                user_message="Hello, this is a test.",
                system_prompt="You are a helpful assistant. Respond with 'Connection successful!'",
                model_type="fast"
            )
            return "Connection successful!" in response
        except Exception as e:
            print(f"Groq connection test failed: {e}")
            return False
