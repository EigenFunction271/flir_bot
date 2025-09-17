# Flir Voice-Enabled Development Plan
## TTS/STT Integration with ElevenLabs, Groq GPT OSS, and Modular Character Selection

### Executive Summary

This development plan extends the existing Flir social skills training platform to include voice capabilities using ElevenLabs for TTS/STT, Groq's GPT OSS models for language processing, and a modular character selection system. The enhanced platform will provide immersive voice-based social skills training with realistic character interactions.

---

## 1. Technical Architecture Overview

### 1.1 Enhanced System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flir Voice Platform                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   User      │  │   Coach     │  │ Character   │         │
│  │   Bot       │  │   Bot       │  │   Bots      │         │
│  │ (Voice UI)  │  │ (Orchestr.) │  │ (Personas)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ ElevenLabs  │  │    Groq     │  │ Character   │         │
│  │ TTS/STT API │  │ GPT OSS API │  │ Management  │         │
│  │             │  │             │  │   System    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Audio     │  │   Session   │  │   Progress  │         │
│  │ Processing  │  │ Management  │  │  Tracking   │         │
│  │   Engine    │  │   System    │  │   System    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Core Components

1. **Voice Interface Layer**: Handles audio input/output with ElevenLabs
2. **Language Processing Layer**: Groq GPT OSS for character responses
3. **Character Management System**: Modular persona selection and management
4. **Session Orchestration**: Coordinates multi-bot voice interactions
5. **Audio Processing Engine**: Real-time audio handling and optimization

---

## 2. Technology Stack Integration

### 2.1 ElevenLabs Integration

**TTS Capabilities:**
- Real-time text-to-speech conversion
- Voice cloning for character consistency
- Multiple voice options per character
- Streaming audio for low latency
- Voice emotion and tone control

**STT Capabilities:**
- Real-time speech-to-text conversion
- Multi-language support
- Noise reduction and audio enhancement
- Speaker identification (for multi-user scenarios)

**Implementation Requirements:**
```python
# ElevenLabs TTS Configuration
ELEVENLABS_CONFIG = {
    "api_key": os.getenv("ELEVENLABS_API_KEY"),
    "base_url": "https://api.elevenlabs.io/v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    }
}
```

### 2.2 Groq GPT OSS Integration

**Model Selection:**
- **GPT OSS 20B**: For faster response times and lower costs
- **GPT OSS 120B**: For higher quality responses in complex scenarios
- Dynamic model selection based on scenario complexity

**API Configuration:**
```python
# Groq GPT OSS Configuration
GROQ_CONFIG = {
    "api_key": os.getenv("GROQ_API_KEY"),
    "base_url": "https://api.groq.com/openai/v1",
    "models": {
        "fast": "openai/gpt-oss-20b",
        "quality": "openai/gpt-oss-120b"
    },
    "temperature": 0.7,
    "max_tokens": 500
}
```

### 2.3 Character Management System

**Modular Persona Architecture:**
```python
class CharacterPersona:
    def __init__(self, name, voice_id, personality_traits, 
                 communication_style, scenario_affinity):
        self.name = name
        self.voice_id = voice_id  # ElevenLabs voice ID
        self.personality_traits = personality_traits
        self.communication_style = communication_style
        self.scenario_affinity = scenario_affinity
        self.system_prompt = self._generate_system_prompt()
    
    def _generate_system_prompt(self):
        return f"""You are {self.name}, a character in a social skills training scenario. Act and respond in a manner similar to your real-life counterpart {self.reference}, keeping in mind the personality and communication style defined below.
        Personality: {self.personality_traits}
        Communication Style: {self.communication_style}
        Respond naturally and stay in character throughout the interaction."""
```

---

## 3. Pre-defined Character Personas

### 3.1 Workplace Scenario Characters

**1. Marcus - The Demanding Boss**
- **Voice**: Deep, authoritative male voice
- **Personality**: Results-driven, impatient, high expectations
- **Reference**: Elon Musk
- **Communication Style**: Direct, confrontational, deadline-focused
- **Voice ID**: `elevenlabs_voice_001`

**2. Sarah - The Supportive Coworker**
- **Voice**: Warm, empathetic female voice
- **Personality**: Collaborative, understanding, solution-oriented
- **Reference**: 
- **Communication Style**: Diplomatic, encouraging, team-focused
- **Voice ID**: `elevenlabs_voice_002`

### 3.2 Dating Scenario Characters

**3. Alex - The Romantic Interest**
- **Voice**: Charming, confident voice (gender-neutral)
- **Personality**: Interesting, slightly mysterious, good listener
- **Reference**: 
- **Communication Style**: Engaging, curious, emotionally intelligent
- **Voice ID**: `elevenlabs_voice_003`

**4. Jordan - The Supportive Friend**
- **Voice**: Friendly, encouraging voice (gender-neutral)
- **Personality**: Supportive, honest, experienced
- **Reference**: 
- **Communication Style**: Direct but caring, gives good advice
- **Voice ID**: `elevenlabs_voice_004`

### 3.3 Family Scenario Characters

**5. Patricia - The Overbearing Parent**
- **Voice**: Concerned, slightly nagging female voice
- **Personality**: Worried, controlling, well-meaning but intrusive
- **Reference**: 
- **Communication Style**: Guilt-inducing, repetitive, emotional
- **Voice ID**: `elevenlabs_voice_005`

**6. Michael - The Understanding Sibling**
- **Voice**: Calm, rational male voice
- **Personality**: Mediator, understanding, family-focused
- **Reference**:
- **Communication Style**: Logical, supportive, boundary-respecting
- **Voice ID**: `elevenlabs_voice_006`

### 3.4 Coach Bot Character

**7. Kai - The AI Coach**
- **Voice**: Professional, encouraging voice (gender-neutral)
- **Personality**: Patient, knowledgeable, supportive
- **Communication Style**: Clear, constructive, motivating
- **Voice ID**: `elevenlabs_voice_007`

---

## 4. Development Phases

### Phase 1: Core Voice Infrastructure (Weeks 1-2)

**Week 1: Audio Foundation**
- [ ] Set up ElevenLabs API integration
- [ ] Implement basic TTS functionality
- [ ] Implement basic STT functionality
- [ ] Create audio processing pipeline
- [ ] Test audio quality and latency

**Week 2: Groq Integration**
- [ ] Set up Groq GPT OSS API integration
- [ ] Implement model selection logic
- [ ] Create prompt engineering framework
- [ ] Test response quality and speed
- [ ] Implement error handling and fallbacks

### Phase 2: Character System Development (Weeks 3-4)

**Week 3: Character Management**
- [ ] Design character persona data structure
- [ ] Implement character selection mechanism
- [ ] Create voice-to-character mapping system
- [ ] Develop character personality prompts
- [ ] Test character consistency

**Week 4: Multi-Character Coordination**
- [ ] Implement turn-taking system for voice interactions
- [ ] Create conversation flow management
- [ ] Develop character relationship dynamics
- [ ] Test multi-character scenarios
- [ ] Optimize response timing

### Phase 3: Scenario Integration (Weeks 5-6)

**Week 5: Voice Scenario Implementation**
- [ ] Adapt existing scenarios for voice interaction
- [ ] Implement voice-specific coaching features
- [ ] Create audio feedback systems
- [ ] Test scenario flow with voice
- [ ] Optimize user experience

**Week 6: Advanced Features**
- [ ] Implement real-time coaching during voice interactions
- [ ] Create voice emotion detection
- [ ] Develop progress tracking for voice sessions
- [ ] Test advanced features
- [ ] Performance optimization

### Phase 4: Testing and Optimization (Weeks 7-8)

**Week 7: Integration Testing**
- [ ] End-to-end voice scenario testing
- [ ] Multi-user voice interaction testing
- [ ] Performance and latency optimization
- [ ] Error handling and recovery testing
- [ ] User experience refinement

**Week 8: Launch Preparation**
- [ ] Beta testing with voice features
- [ ] Documentation and deployment preparation
- [ ] Monitoring and analytics setup
- [ ] Launch readiness review
- [ ] Go-live preparation

---

## 5. Implementation Details

### 5.1 Voice Processing Pipeline

```python
class VoiceProcessor:
    def __init__(self):
        self.elevenlabs_client = ElevenLabsClient()
        self.groq_client = GroqClient()
        self.character_manager = CharacterManager()
    
    async def process_voice_input(self, audio_data, character_id, scenario_context):
        # STT: Convert audio to text
        user_text = await self.elevenlabs_client.speech_to_text(audio_data)
        
        # Get character persona
        character = self.character_manager.get_character(character_id)
        
        # Process with Groq GPT OSS
        response_text = await self.groq_client.generate_response(
            user_text, character.system_prompt, scenario_context
        )
        
        # TTS: Convert response to speech
        audio_response = await self.elevenlabs_client.text_to_speech(
            response_text, character.voice_id
        )
        
        return audio_response, response_text
```

### 5.2 Character Selection Interface

```python
class CharacterSelector:
    def __init__(self):
        self.available_characters = self._load_character_database()
    
    def get_characters_for_scenario(self, scenario_type):
        return [char for char in self.available_characters 
                if scenario_type in char.scenario_affinity]
    
    def select_character(self, character_id, user_preferences=None):
        character = self.available_characters[character_id]
        if user_preferences:
            character = self._customize_character(character, user_preferences)
        return character
```

### 5.3 Session Management

```python
class VoiceSessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.voice_processor = VoiceProcessor()
    
    async def start_voice_session(self, user_id, scenario_id, character_ids):
        session = VoiceSession(
            user_id=user_id,
            scenario_id=scenario_id,
            characters=[self.character_manager.get_character(cid) 
                       for cid in character_ids],
            voice_processor=self.voice_processor
        )
        self.active_sessions[user_id] = session
        return session
    
    async def process_voice_interaction(self, user_id, audio_data):
        session = self.active_sessions.get(user_id)
        if not session:
            raise SessionNotFoundError()
        
        return await session.process_interaction(audio_data)
```

---

## 6. Technical Requirements

### 6.1 Performance Requirements

- **Voice Latency**: <2 seconds end-to-end response time
- **Audio Quality**: 44.1kHz, 16-bit audio minimum
- **Concurrent Users**: Support 50+ simultaneous voice sessions
- **Uptime**: 99.5% availability for voice services

### 6.2 Security Requirements

- **Audio Encryption**: All voice data encrypted in transit and at rest
- **Privacy Compliance**: GDPR/CCPA compliant voice data handling
- **API Security**: Secure API key management and rotation
- **Content Moderation**: Real-time inappropriate content detection

### 6.3 Scalability Requirements

- **Horizontal Scaling**: Voice processing services can scale independently
- **Load Balancing**: Distribute voice processing across multiple instances
- **Caching**: Cache character responses and voice samples
- **CDN Integration**: Global audio content delivery

---

## 7. Cost Analysis

### 7.1 ElevenLabs Costs
- **TTS**: ~$0.30 per 1K characters
- **STT**: ~$0.20 per minute of audio
- **Voice Cloning**: $5 per voice (one-time)
- **Estimated Monthly**: $200-500 for 1000 active users

### 7.2 Groq Costs
- **GPT OSS 20B**: ~$0.10 per 1K tokens
- **GPT OSS 120B**: ~$0.50 per 1K tokens
- **Estimated Monthly**: $100-300 for 1000 active users

### 7.3 Infrastructure Costs
- **Audio Processing**: $50-100/month
- **Storage**: $20-50/month
- **Bandwidth**: $30-80/month

**Total Estimated Monthly Cost**: $400-930 for 1000 active users

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Voice Quality Issues**
- *Risk*: Poor audio quality affecting user experience
- *Mitigation*: Multiple voice options, audio preprocessing, quality testing

**API Rate Limits**
- *Risk*: ElevenLabs or Groq API limits causing service disruption
- *Mitigation*: Multiple API keys, request queuing, fallback models

**Latency Problems**
- *Risk*: High response times breaking conversation flow
- *Mitigation*: Streaming responses, local caching, optimized prompts

### 8.2 Business Risks

**High API Costs**
- *Risk*: Voice features significantly increase operational costs
- *Mitigation*: Usage monitoring, tiered pricing, cost optimization

**User Adoption**
- *Risk*: Users prefer text over voice interaction
- *Mitigation*: Hybrid text/voice options, gradual voice introduction

---

## 9. Success Metrics

### 9.1 Technical Metrics
- **Voice Response Time**: <2 seconds average
- **Audio Quality Score**: >4.0/5.0 user rating
- **System Uptime**: >99.5%
- **Error Rate**: <1% of voice interactions

### 9.2 User Engagement Metrics
- **Voice Session Duration**: 20+ minutes average
- **Voice Feature Adoption**: 60% of users try voice within first week
- **Voice Preference**: 40% of users prefer voice over text
- **Character Satisfaction**: 4.5+ stars for voice character realism

### 9.3 Learning Effectiveness
- **Voice Confidence Improvement**: 85% of users report increased confidence
- **Voice Scenario Completion**: 75% completion rate for voice scenarios
- **Voice Retry Rate**: 50% of users retry voice scenarios with different approaches

---

## 10. Future Enhancements

### 10.1 Advanced Voice Features
- **Emotion Detection**: Real-time emotion analysis from voice
- **Voice Cloning**: User can create custom character voices
- **Multi-language Support**: Characters speak multiple languages
- **Voice Customization**: Users can adjust character voice parameters

### 10.2 AI Improvements
- **Contextual Memory**: Characters remember voice tone and style preferences
- **Adaptive Responses**: Characters adjust communication style based on user's voice patterns
- **Real-time Coaching**: Voice-based coaching during conversations
- **Progress Analytics**: Voice pattern analysis for skill improvement tracking

---

## 11. Implementation Checklist

### Pre-Development Setup
- [ ] Obtain ElevenLabs API access and keys
- [ ] Obtain Groq API access and keys
- [ ] Set up development environment with audio libraries
- [ ] Create project repository structure
- [ ] Set up CI/CD pipeline for voice features

### Development Milestones
- [ ] Week 2: Basic voice input/output working
- [ ] Week 4: Character voice system implemented
- [ ] Week 6: Voice scenarios fully functional
- [ ] Week 8: Production-ready voice platform

### Launch Preparation
- [ ] Voice feature beta testing completed
- [ ] Performance optimization finished
- [ ] Documentation and user guides created
- [ ] Monitoring and analytics implemented
- [ ] Launch strategy executed

---

*This development plan provides a comprehensive roadmap for integrating voice capabilities into the Flir platform while maintaining the core social skills training mission and ensuring a seamless user experience.*
