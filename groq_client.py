import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with Groq GPT OSS API"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = Config.GROQ_BASE_URL
        self.models = Config.GROQ_MODELS
        self.session = None
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        logger.info("✅ GroqClient initialized successfully")
    
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
            # Use session reuse for better performance
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
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
                    logger.error(f"Groq API error {response.status}: {error_text}")
                    raise Exception(f"Groq API error {response.status}: {error_text}")
                    
        except asyncio.TimeoutError:
            logger.error("Groq API request timed out")
            raise Exception("Groq API request timed out")
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise Exception(f"Error calling Groq API: {str(e)}")
    
    async def generate_response_with_history(
        self, 
        user_message: str, 
        system_prompt: str, 
        conversation_history: List[Dict],
        model_type: str = "fast",
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate a response using Groq GPT OSS with conversation history
        
        Args:
            user_message: The user's current input message
            system_prompt: The system prompt for the character
            conversation_history: List of previous conversation messages
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
        
        # Build messages array with system prompt and conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limit to last 10 messages to avoid token limits)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Use session reuse for better performance
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
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
                    logger.error(f"Groq API error {response.status}: {error_text}")
                    raise Exception(f"Groq API error {response.status}: {error_text}")
                    
        except asyncio.TimeoutError:
            logger.error("Groq API request timed out")
            raise Exception("Groq API request timed out")
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
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
            logger.error(f"Groq connection test failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("✅ GroqClient session closed")
