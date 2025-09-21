import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with Groq GPT OSS API"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = Config.GROQ_BASE_URL
        self.models = Config.GROQ_MODELS
        self.session = None
        
        # Rate limiting
        self.request_times = []
        self.max_requests_per_minute = 30  # Conservative limit
        self.rate_limit_window = 60  # seconds
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        logger.info("✅ GroqClient initialized successfully")
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        
        # Remove old request times outside the window
        self.request_times = [
            req_time for req_time in self.request_times 
            if (now - req_time).total_seconds() < self.rate_limit_window
        ]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.max_requests_per_minute:
            # Calculate wait time
            oldest_request = min(self.request_times)
            wait_time = self.rate_limit_window - (now - oldest_request).total_seconds()
            
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(now)
    
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
        
        # Check rate limit before making request
        await self._check_rate_limit()
        
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
    
    def _get_character_relevant_history(self, conversation_history: List[Dict], current_character_name: str) -> List[Dict]:
        """Filter conversation history to give character-specific context and self-awareness"""
        relevant_messages = []
        
        for msg in conversation_history:
            if msg["role"] == "user":
                # User messages are relevant to all characters
                relevant_messages.append(msg)
            elif msg["role"] == "assistant":
                character_name = msg.get("character", "Unknown")
                content = msg.get("content", "")
                
                if character_name == current_character_name:
                    # This character's own previous response
                    relevant_messages.append({
                        "role": "assistant",
                        "content": f"You said: {content}"
                    })
                else:
                    # Another character's response
                    relevant_messages.append({
                        "role": "assistant",
                        "content": f"{character_name} said: {content}"
                    })
        
        return relevant_messages

    async def generate_response_with_history(
        self, 
        user_message: str, 
        system_prompt: str, 
        conversation_history: List[Dict],
        model_type: str = "fast",
        temperature: float = None,
        max_tokens: int = None,
        current_character_name: str = None
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
        
        # Check rate limit before making request
        await self._check_rate_limit()
        
        model = self.models[model_type]
        temperature = temperature or Config.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or Config.MAX_RESPONSE_LENGTH
        
        # Build messages array with system prompt and conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Filter conversation history for character-specific context and self-awareness
        if current_character_name:
            character_relevant_history = self._get_character_relevant_history(conversation_history, current_character_name)
            logger.info(f"🎭 MEMORY: Filtered history for {current_character_name}: {len(character_relevant_history)} messages")
        else:
            # Fallback to generic history if no character name provided
            character_relevant_history = conversation_history
            logger.info("🎭 MEMORY: Using generic conversation history (no character specified)")
        
        # Add conversation history (limit to last 10 messages to avoid token limits)
        recent_history = character_relevant_history[-10:] if len(character_relevant_history) > 10 else character_relevant_history
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
