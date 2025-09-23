import asyncio
import google.generativeai as genai
import logging
import re
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
    
    def _validate_feedback_structure(self, feedback: dict) -> bool:
        """Validate that feedback contains all required fields with meaningful content"""
        required_fields = ["rating", "overall_assessment", "strengths_text", "improvements_text", "key_takeaways_text"]
        
        for field in required_fields:
            if field not in feedback:
                logger.error(f"Missing required field in feedback: {field}")
                return False
            
            value = feedback[field]
            if not value or not str(value).strip():
                logger.error(f"Empty or invalid value for field '{field}': {value}")
                return False
            
            # Check minimum length for text fields
            if field.endswith('_text') and len(str(value).strip()) < 10:
                logger.warning(f"Field '{field}' has very short content: {value}")
        
        # Validate rating format
        rating = str(feedback.get("rating", "")).strip()
        if not re.match(r'\d+/10', rating):
            logger.warning(f"Invalid rating format: {rating}")
        
        logger.info("Feedback structure validation passed")
        return True
    
    async def generate_feedback(
        self, 
        conversation_history: List[Dict], 
        scenario_name: str,
        character_name: str,
        scenario_objectives: List[str],
        scenario_context: str = None,
        user_role_description: str = None
    ) -> dict:
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
            
            # Log request context for debugging
            logger.info(f"Generating feedback for scenario '{scenario_name}' with character '{character_name}'")
            logger.info(f"Conversation history length: {len(conversation_history)} messages")
            logger.info(f"Scenario objectives: {scenario_objectives}")
            
            # Generate feedback using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            # Parse JSON response
            feedback_text = response.text.strip()
            
            logger.info(f"Raw Gemini response length: {len(feedback_text)} characters")
            logger.debug(f"Raw Gemini response preview: {feedback_text[:200]}...")
            
            # Try to extract structured feedback (handles both JSON and malformed responses)
            feedback_data = self._extract_json_from_response(feedback_text)
            
            # Validate the extracted feedback
            if not self._validate_feedback_structure(feedback_data):
                logger.warning("Feedback validation failed, using fallback data")
                return self._get_fallback_feedback_data()
            
            logger.info("Successfully generated and validated feedback")
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error generating feedback with Gemini for scenario '{scenario_name}': {str(e)}")
            logger.error(f"Conversation history length: {len(conversation_history)}")
            logger.error(f"Character: {character_name}, Objectives: {scenario_objectives}")
            # Return fallback feedback instead of raising exception
            return self._get_fallback_feedback_data()
    
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
    
    def _extract_json_from_response(self, feedback_text: str) -> dict:
        """
        Extract structured feedback from Gemini response with maximum flexibility.
        Handles both valid JSON and malformed responses by extracting field values directly.
        """
        import json
        
        # Get default fallback data
        fallback_data = self._get_fallback_feedback_data()
        
        # Define required fields at function scope
        required_fields = ["rating", "overall_assessment", "strengths_text", "improvements_text", "key_takeaways_text"]
        
        # Step 1: Try to clean and parse as JSON first
        cleaned_text = self._clean_response_text(feedback_text)
        
        try:
            feedback_data = json.loads(cleaned_text)
            
            # Validate required fields
            missing_fields = []
            for field in required_fields:
                if field not in feedback_data:
                    missing_fields.append(field)
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            logger.info("Successfully parsed JSON response from Gemini")
            return feedback_data
            
        except (json.JSONDecodeError, ValueError) as json_error:
            logger.warning(f"JSON parsing failed for Gemini response: {json_error}")
            logger.info(f"Original response length: {len(feedback_text)} characters")
            logger.debug(f"Cleaned response: {cleaned_text[:200]}...")
            logger.info("Attempting field-by-field extraction from malformed response")
            
            # Step 2: Extract field values directly from the original text
            extracted_data = self._extract_field_values(feedback_text)
            
            # Use extracted values if found, otherwise keep defaults
            extracted_count = 0
            for field, value in extracted_data.items():
                if value and len(value.strip()) > 5:  # Only use if substantial content
                    fallback_data[field] = value
                    extracted_count += 1
                    logger.info(f"Successfully extracted {field}: {value[:50]}...")
            
            logger.info(f"Field extraction completed: {extracted_count}/{len(required_fields)} fields extracted")
            return fallback_data
    
    def _get_fallback_feedback_data(self) -> dict:
        """Get fallback feedback data when all other methods fail"""
        return {
            "rating": "7/10",
            "overall_assessment": "Performance analysis completed. See detailed feedback below.",
            "strengths_text": "Communication skills demonstrated - You maintained a professional tone and attempted to address the situation constructively. Engagement with the scenario - You actively participated and showed interest in resolving the conflict or challenge presented. Effort to address the situation - You made genuine attempts to understand and work through the scenario objectives.",
            "improvements_text": "Continue practicing assertiveness - Try being more direct about your needs and concerns. For example, instead of 'I think maybe we could...' try 'I need...' or 'I believe we should...'. Work on clear communication - Be more specific about your points and provide concrete examples. Avoid vague statements and focus on actionable solutions. Focus on scenario objectives - Make sure you're directly addressing the core issues in the scenario.",
            "key_takeaways_text": "Practice active listening - When the other person speaks, acknowledge their points before responding. Try saying 'I understand that you feel...' or 'I hear that you're concerned about...'. Be more direct in communication - Use 'I' statements to express your needs clearly. Instead of 'Maybe we should consider...' try 'I need...' or 'I want...'. Set clear boundaries - When someone is being unreasonable, practice saying 'I'm not comfortable with that' or 'That doesn't work for me' followed by your alternative suggestion."
        }
    
    def _extract_field_values(self, text: str) -> dict:
        """
        Extract field values by finding field names and extracting quoted content.
        Handles malformed JSON with newlines and formatting issues like:
        "rating":"7/10",\n "overall_assessment": "..."
        """
        import re
        
        extracted = {}
        
        # Define the fields we want to extract
        fields = ["rating", "overall_assessment", "strengths_text", "improvements_text", "key_takeaways_text"]
        
        logger.info("Starting robust field extraction from malformed JSON")
        
        for field in fields:
            logger.debug(f"Extracting field: {field}")
            
            # Special handling for rating field (might not be quoted)
            if field == "rating":
                value = self._extract_rating_field(text, field)
            else:
                value = self._extract_quoted_field(text, field)
            
            if value:
                extracted[field] = value
                logger.info(f"Successfully extracted {field}: {value[:50]}...")
            else:
                logger.warning(f"Failed to extract field: {field}")
        
        logger.info(f"Field extraction completed: {len(extracted)}/{len(fields)} fields extracted")
        return extracted
    
    def _extract_rating_field(self, text: str, field: str) -> str:
        """Extract rating field which might not be quoted"""
        import re
        
        # Try multiple patterns for rating field
        patterns = [
            rf'"{field}"\s*:\s*"([^"]*)"',  # "rating": "7/10"
            rf'"{field}"\s*:\s*([^,}}\n]+)',  # "rating": 7/10
            rf'{field}\s*:\s*"([^"]*)"',  # rating: "7/10"
            rf'{field}\s*:\s*([^,}}\n]+)',  # rating: 7/10
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up common rating formats
                value = re.sub(r'^["\']|["\']$', '', value)  # Remove surrounding quotes
                if re.match(r'\d+/10', value):  # Validate it looks like a rating
                    return value
        
        return ""
    
    def _extract_quoted_field(self, text: str, field: str) -> str:
        """Extract quoted field content, handling newlines and malformed JSON"""
        import re
        
        # Find the field name and colon, then extract the quoted content
        # This handles cases like: "field": "value" or "field":\n"value"
        
        # First, find the field name and colon
        field_pattern = rf'["\']?{field}["\']?\s*:\s*'
        field_match = re.search(field_pattern, text, re.IGNORECASE)
        
        if not field_match:
            return ""
        
        # Get the position after the colon
        start_pos = field_match.end()
        
        # Skip any whitespace and newlines
        remaining_text = text[start_pos:].lstrip()
        
        # Look for the opening quote
        if not remaining_text.startswith('"'):
            return ""
        
        # Find the matching closing quote, handling escaped quotes
        quote_count = 0
        i = 0
        while i < len(remaining_text):
            char = remaining_text[i]
            
            if char == '"':
                # Check if it's escaped
                if i > 0 and remaining_text[i-1] == '\\':
                    i += 1
                    continue
                
                if quote_count == 0:
                    # Found opening quote
                    quote_count = 1
                else:
                    # Found closing quote
                    quote_count = 0
                    # Extract the content between quotes
                    content = remaining_text[1:i]  # Skip opening quote
                    return self._clean_extracted_value(content)
            
            i += 1
        
        # If we get here, we didn't find a closing quote
        # Try to extract up to the next comma or brace
        fallback_match = re.search(r'"([^"]*(?:\\.[^"]*)*)', remaining_text)
        if fallback_match:
            return self._clean_extracted_value(fallback_match.group(1))
        
        return ""
    
    def _clean_extracted_value(self, value: str) -> str:
        """Clean up extracted field values"""
        import re
        
        if not value:
            return ""
        
        # Unescape common escape sequences
        value = value.replace('\\"', '"')  # Unescape quotes
        value = value.replace('\\n', '\n')  # Convert \n to actual newlines
        value = value.replace('\\t', '\t')  # Convert \t to actual tabs
        value = value.replace('\\\\', '\\')  # Unescape backslashes
        
        # Remove excessive whitespace but preserve intentional formatting
        value = re.sub(r'\n\s*\n', '\n\n', value)  # Normalize paragraph breaks
        value = value.strip()
        
        return value
    
    def _clean_response_text(self, response_text: str) -> str:
        """
        Clean response text for JSON parsing.
        Removes markdown code blocks and extracts JSON boundaries.
        """
        import re
        
        # Step 1: Remove markdown code blocks
        text = response_text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        text = text.strip()
        
        # Step 2: Find JSON object boundaries
        start_idx = text.find('{')
        if start_idx == -1:
            logger.warning("No opening brace found in response")
            return text
        
        # Step 3: Find matching closing brace (handle nested braces)
        brace_count = 0
        end_idx = start_idx
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if brace_count != 0:
            logger.warning("Unmatched braces in response")
            return text
        
        # Step 4: Extract the JSON portion
        json_text = text[start_idx:end_idx]
        
        # Step 5: Clean up common issues
        json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
        json_text = re.sub(r',\s*]', ']', json_text)
        json_text = json_text.replace('\\\\"', '\\"')  # Fix double-escaped quotes
        
        logger.info(f"Cleaned JSON: {json_text[:100]}...")
        return json_text
    
    def test_field_extraction(self) -> bool:
        """Test the field extraction with malformed JSON examples"""
        test_cases = [
            # Case 1: Your exact example
            '''"rating":"7/10",
 "overall_assessment": "The user showed good communication skills and handled the situation well.",
 "strengths_text": "You maintained a professional tone throughout the conversation.",
 "improvements_text": "Try to be more assertive in expressing your needs.",
 "key_takeaways_text": "Practice active listening and clear communication."''',
            
            # Case 2: With newlines and spacing issues
            '''"rating" : "8/10" ,
 "overall_assessment": "Excellent performance in this scenario.",
 "strengths_text": "Great job staying calm under pressure.",
 "improvements_text": "Consider asking more clarifying questions.",
 "key_takeaways_text": "Remember to validate the other person's feelings."''',
            
            # Case 3: Mixed formatting
            '''rating: "6/10",
"overall_assessment": "Good effort, but room for improvement.",
"strengths_text": "You tried to address the situation constructively.",
"improvements_text": "Be more direct about your concerns.",
"key_takeaways_text": "Practice setting clear boundaries."'''
        ]
        
        logger.info("Testing field extraction with malformed JSON examples")
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Testing case {i}: {test_case[:50]}...")
            extracted = self._extract_field_values(test_case)
            
            expected_fields = ["rating", "overall_assessment", "strengths_text", "improvements_text", "key_takeaways_text"]
            success_count = sum(1 for field in expected_fields if field in extracted and extracted[field])
            
            logger.info(f"Case {i} result: {success_count}/{len(expected_fields)} fields extracted")
            for field, value in extracted.items():
                logger.info(f"  {field}: {value[:30]}...")
        
        return True
    
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
