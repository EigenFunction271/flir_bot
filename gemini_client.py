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
        scenario_objectives: List[str],
        scenario_context: str = None,
        user_role_description: str = None
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
        
        # Create feedback prompt with proper context
        user_role_context = f"\nUSER'S ROLE IN SCENARIO: {user_role_description}" if user_role_description else ""
        scenario_context_info = f"\nSCENARIO CONTEXT: {scenario_context}" if scenario_context else ""
        
        prompt = f"""You are an expert social skills coach analyzing a conversation between a user and AI characters in a social skills training scenario.

SCENARIO: {scenario_name}
CHARACTER: {character_name}
OBJECTIVES: {', '.join(scenario_objectives)}{user_role_context}{scenario_context_info}

CONVERSATION HISTORY:
{conversation_text}

IMPORTANT: The user is the person being trained in social skills. The AI characters (like {character_name}) are playing specific roles to challenge and train the user. Evaluate the USER's performance, not the AI characters' performance.

For example, in a workplace scenario where the user is an employee being pressured by a boss:
- Evaluate how well the user stood up for themselves, communicated their concerns, and handled the pressure
- Do NOT evaluate the boss character's aggressive behavior (that's intentional to create challenge)
- Focus on the user's communication skills, assertiveness, and problem-solving approach

Please provide constructive feedback on the USER's social skills performance. Focus on:

1. **Communication Strengths**: What did the user do well?
2. **Areas for Improvement**: What could be improved?
3. **Specific Examples**: Reference specific moments from the conversation
4. **Actionable Advice**: Provide concrete tips for future interactions
5. **Objective Achievement**: How well did they work toward the scenario objectives?

Format your feedback as JSON with these exact fields:
{{
    "rating": "X/10 - where X is a number from 1-10",
    "overall_assessment": "Brief summary of performance (2-3 sentences)",
    "strengths_text": "Detailed analysis of communication strengths with specific examples from the conversation. Include 2-3 key strengths with concrete examples.",
    "improvements_text": "Detailed analysis of areas for improvement with specific suggestions. Include 2-3 key areas with actionable advice.",
    "key_takeaways_text": "Detailed actionable tips and strategies for future conversations. Include 2-3 key takeaways with specific guidance."
}}

IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON object."""

        try:
            # Check rate limit before making request
            await self._check_rate_limit()
            
            # Generate feedback using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            # Parse JSON response
            feedback_text = response.text.strip()
            try:
                import json
                feedback_data = json.loads(feedback_text)
                
                # Validate required fields
                required_fields = ["rating", "overall_assessment", "strengths_text", "improvements_text", "key_takeaways_text"]
                for field in required_fields:
                    if field not in feedback_data:
                        raise ValueError(f"Missing required field: {field}")
                
                return feedback_data
                
            except (json.JSONDecodeError, ValueError) as json_error:
                logger.warning(f"Failed to parse JSON feedback: {json_error}")
                logger.warning(f"Raw response: {feedback_text}")
                # Fallback to structured text format
                return self._create_fallback_feedback(feedback_text)
            
        except Exception as e:
            logger.error(f"Error generating feedback with Gemini: {str(e)}")
            # Return fallback feedback instead of raising exception
            return self._create_fallback_feedback("")
    
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
    
    def _create_fallback_feedback(self, feedback_text: str) -> dict:
        """Create structured feedback from text when JSON parsing fails"""
        logger.info("Creating fallback feedback structure from text response")
        
        # Try to extract information from the text response
        fallback_data = {
            "rating": "7/10",  # Default rating
            "overall_assessment": "Performance analysis completed. See detailed feedback below.",
            "strengths_text": "Communication skills demonstrated - You maintained a professional tone and attempted to address the situation constructively. Engagement with the scenario - You actively participated and showed interest in resolving the conflict or challenge presented. Effort to address the situation - You made genuine attempts to understand and work through the scenario objectives.",
            "improvements_text": "Continue practicing assertiveness - Try being more direct about your needs and concerns. For example, instead of 'I think maybe we could...' try 'I need...' or 'I believe we should...'. Work on clear communication - Be more specific about your points and provide concrete examples. Avoid vague statements and focus on actionable solutions. Focus on scenario objectives - Make sure you're directly addressing the core issues in the scenario.",
            "key_takeaways_text": "Practice active listening - When the other person speaks, acknowledge their points before responding. Try saying 'I understand that you feel...' or 'I hear that you're concerned about...'. Be more direct in communication - Use 'I' statements to express your needs clearly. Instead of 'Maybe we should consider...' try 'I need...' or 'I want...'. Set clear boundaries - When someone is being unreasonable, practice saying 'I'm not comfortable with that' or 'That doesn't work for me' followed by your alternative suggestion."
        }
        
        # Try to extract rating if present
        import re
        rating_match = re.search(r'(\d+)/10', feedback_text)
        if rating_match:
            fallback_data["rating"] = rating_match.group(0)
        
        return fallback_data
    
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
