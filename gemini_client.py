import asyncio
import google.generativeai as genai
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for Google Gemini Flash 2.0 feedback generation"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        
        # Rate limiting
        self.request_times = []
        self.max_requests_per_minute = 20  # Conservative limit for Gemini
        self.rate_limit_window = 60  # seconds
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("✅ GeminiClient initialized successfully")
    
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
                logger.warning(f"Gemini rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(now)
    
    async def generate_feedback(
        self, 
        conversation_history: List[Dict], 
        scenario_name: str,
        character_name: str,
        scenario_objectives: List[str]
    ) -> str:
        """
        Generate feedback based on conversation history and scenario objectives
        
        Args:
            conversation_history: List of conversation messages
            scenario_name: Name of the scenario
            character_name: Name of the character interacted with
            scenario_objectives: List of learning objectives for the scenario
            
        Returns:
            Generated feedback text
        """
        # Format conversation history
        conversation_text = self._format_conversation_history(conversation_history)
        
        # Create feedback prompt
        prompt = f"""You are an expert social skills coach analyzing a conversation between a user and a set of AI characters in a social skills training scenario.

SCENARIO: {scenario_name}
CHARACTER: {character_name}
CHARACTERS: {', '.join(characters)}
OBJECTIVES: {', '.join(scenario_objectives)}

CONVERSATION HISTORY:
{conversation_text}

Please provide constructive feedback on the user's social skills performance. Focus on:

1. **Communication Strengths**: What did the user do well?
2. **Areas for Improvement**: What could be improved?
3. **Specific Examples**: Reference specific moments from the conversation
4. **Actionable Advice**: Provide concrete tips for future interactions
5. **Objective Achievement**: How well did they work toward the scenario objectives?

Format your feedback as:
- **Rating**: [1-10] - 10 is completely successful or very minor flaws, 1 is completely failed or repeated major flaws
- **Strengths**: [List 2-3 strengths with examples]
- **Areas for Improvement**: [List 2-3 areas with specific suggestions]
- **Key Takeaways**: [2-3 actionable tips for future conversations]
- **Overall Assessment**: [Brief summary of performance]

Keep the feedback constructive, specific, and encouraging. Aim for 300-400 words total."""

        try:
            # Check rate limit before making request
            await self._check_rate_limit()
            
            # Generate feedback using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating feedback with Gemini: {str(e)}")
            raise Exception(f"Error generating feedback with Gemini: {str(e)}")
    
    def _format_conversation_history(self, conversation_history: List[Dict]) -> str:
        """Format conversation history for feedback analysis"""
        formatted = []
        
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            character = msg.get("character", "")
            
            if role == "user":
                formatted.append(f"USER: {content}")
            elif role == "assistant":
                formatted.append(f"{character}: {content}")
        
        return "\n".join(formatted)
    
    async def test_connection(self) -> bool:
        """Test if the Gemini API connection is working"""
        try:
            # Check rate limit before making request
            await self._check_rate_limit()
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                "Hello, this is a test. Respond with 'Connection successful!'"
            )
            return "Connection successful!" in response.text
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
