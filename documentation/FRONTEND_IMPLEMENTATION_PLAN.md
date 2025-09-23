# Flir Frontend Implementation Plan

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Architecture & Backend API](#phase-1-architecture--backend-api)
3. [Phase 2: Frontend Development](#phase-2-frontend-development)
4. [Phase 3: Real-time Communication](#phase-3-real-time-communication)
5. [Phase 4: Enhanced User Experience](#phase-4-enhanced-user-experience)
6. [Phase 5: Mobile Optimization](#phase-5-mobile-optimization)
7. [Technical Implementation Details](#technical-implementation-details)
8. [Deployment Strategy](#deployment-strategy)
9. [Benefits & Timeline](#benefits--timeline)

## Overview

This document outlines a comprehensive plan for adding a web frontend to complement the existing Discord bot functionality. The implementation will create a modern, responsive web application that provides the same social skills training capabilities through a more accessible and feature-rich interface.

### Goals
- **Maintain Discord bot functionality** while adding web interface
- **Create reusable backend API** for both Discord and web clients
- **Build modern, responsive frontend** with real-time capabilities
- **Enable user progress tracking** and analytics
- **Provide mobile-optimized experience** with PWA capabilities

### Key Benefits
- **Broader user reach** beyond Discord users
- **Better visual design** and user experience
- **Enhanced analytics** and progress tracking
- **Professional appearance** for enterprise clients
- **Mobile accessibility** for on-the-go practice

## Phase 1: Architecture & Backend API (2-3 weeks)

### 1.1 Backend API Development

Create a REST API layer to decouple the Discord bot from core logic:

```
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── scenarios.py     # Scenario management endpoints
│   │   ├── characters.py    # Character information endpoints
│   │   ├── sessions.py      # Session management endpoints
│   │   ├── conversations.py # Conversation handling endpoints
│   │   ├── feedback.py      # Feedback generation endpoints
│   │   └── users.py         # User management endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── session.py       # Pydantic models for API
│   │   ├── scenario.py      # Scenario response models
│   │   ├── character.py     # Character response models
│   │   ├── feedback.py      # Feedback response models
│   │   └── user.py          # User profile models
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication middleware
│   │   ├── cors.py          # CORS configuration
│   │   └── rate_limit.py    # Rate limiting
│   └── websocket/
│       ├── __init__.py
│       ├── connection_manager.py  # WebSocket connection management
│       ├── message_handler.py     # Message routing
│       └── session_websocket.py   # Session-specific WebSocket handling
```

### 1.2 API Endpoints

#### Scenario Endpoints
```python
# Scenarios
GET /api/scenarios                    # List all scenarios
GET /api/scenarios/{id}              # Get scenario details
GET /api/scenarios/type/{type}       # Filter by type (workplace, dating, family)
GET /api/scenarios/difficulty/{level} # Filter by difficulty
```

#### Character Endpoints
```python
# Characters
GET /api/characters                  # List all characters
GET /api/characters/{id}            # Get character details
GET /api/characters/scenario/{scenario_id} # Get characters for scenario
```

#### Session Endpoints
```python
# Sessions
POST /api/sessions                   # Start new session
GET /api/sessions/{user_id}         # Get user's active session
PUT /api/sessions/{session_id}      # Update session
DELETE /api/sessions/{session_id}   # End session
GET /api/sessions/{session_id}/status # Get session status
```

#### Conversation Endpoints
```python
# Conversations
POST /api/conversations/message      # Send message to characters
GET /api/conversations/{session_id} # Get conversation history
POST /api/conversations/switch-character # Switch current character
```

#### Feedback Endpoints
```python
# Feedback
POST /api/feedback/generate         # Generate feedback for session
GET /api/feedback/{session_id}     # Get feedback for session
GET /api/feedback/user/{user_id}   # Get user's feedback history
```

#### User Endpoints
```python
# Users
POST /api/users/register            # Register new user
POST /api/users/login              # User login
GET /api/users/{user_id}/profile   # Get user profile
PUT /api/users/{user_id}/profile   # Update user profile
GET /api/users/{user_id}/progress  # Get user progress
```

### 1.3 Refactor Existing Code

Extract core logic from `discord_bot.py` into reusable services:

```
├── services/
│   ├── __init__.py
│   ├── conversation_service.py     # Core conversation logic
│   ├── session_service.py          # Session management
│   ├── character_service.py        # Character interactions
│   ├── feedback_service.py         # Feedback generation
│   ├── scenario_service.py         # Scenario management
│   └── user_service.py             # User management
```

**Benefits:**
- **Code reusability** between Discord bot and web API
- **Separation of concerns** for better maintainability
- **Easier testing** with isolated service layers
- **Consistent behavior** across platforms

### 1.4 Database Integration

Add database layer for persistent user data:

```
├── database/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User profiles and preferences
│   │   ├── session.py           # Session persistence
│   │   ├── progress.py          # User progress tracking
│   │   ├── feedback.py          # Feedback history
│   │   └── conversation.py      # Conversation history
│   ├── migrations/              # Database migrations
│   ├── connection.py            # Database connection
│   └── repositories/            # Data access layer
│       ├── __init__.py
│       ├── user_repository.py
│       ├── session_repository.py
│       └── progress_repository.py
```

## Phase 2: Frontend Development (3-4 weeks)

### 2.1 Technology Stack

**Recommended Frontend Stack:**
```typescript
// Core Technologies
- React 18 + TypeScript
- Next.js 14 (for SSR/SSG capabilities)
- Tailwind CSS (for styling)
- Zustand (for state management)
- React Query (for API data fetching)
- Framer Motion (for animations)
- React Hook Form (for form handling)
- Socket.io-client (for WebSocket communication)
```

### 2.2 Frontend Architecture

```
├── src/
│   ├── components/
│   │   ├── ui/                    # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Card.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── chat/                  # Chat interface components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── CharacterAvatar.tsx
│   │   │   ├── TypingIndicator.tsx
│   │   │   └── MessageInput.tsx
│   │   ├── scenarios/             # Scenario selection components
│   │   │   ├── ScenarioCard.tsx
│   │   │   ├── ScenarioGrid.tsx
│   │   │   ├── ScenarioFilter.tsx
│   │   │   └── ScenarioDetails.tsx
│   │   ├── characters/            # Character display components
│   │   │   ├── CharacterCard.tsx
│   │   │   ├── CharacterSelector.tsx
│   │   │   ├── CharacterProfile.tsx
│   │   │   └── CharacterAvatar.tsx
│   │   ├── feedback/              # Feedback display components
│   │   │   ├── FeedbackDisplay.tsx
│   │   │   ├── RatingDisplay.tsx
│   │   │   ├── StrengthsList.tsx
│   │   │   ├── ImprovementsList.tsx
│   │   │   └── TakeawaysList.tsx
│   │   ├── progress/              # Progress tracking components
│   │   │   ├── ProgressDashboard.tsx
│   │   │   ├── SkillChart.tsx
│   │   │   ├── ScenarioHistory.tsx
│   │   │   └── AchievementBadge.tsx
│   │   └── layout/                # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── Footer.tsx
│   │       └── Navigation.tsx
│   ├── pages/
│   │   ├── index.tsx              # Landing page
│   │   ├── scenarios/             # Scenario selection
│   │   │   ├── index.tsx
│   │   │   └── [id].tsx
│   │   ├── chat/                  # Chat interface
│   │   │   └── [sessionId].tsx
│   │   ├── feedback/              # Feedback display
│   │   │   └── [sessionId].tsx
│   │   ├── progress/              # Progress tracking
│   │   │   ├── index.tsx
│   │   │   └── [userId].tsx
│   │   ├── profile/               # User profile
│   │   │   └── [userId].tsx
│   │   └── auth/                  # Authentication
│   │       ├── login.tsx
│   │       └── register.tsx
│   ├── hooks/
│   │   ├── useSession.ts          # Session management
│   │   ├── useConversation.ts     # Chat functionality
│   │   ├── useFeedback.ts         # Feedback handling
│   │   ├── useWebSocket.ts        # WebSocket connection
│   │   ├── useAuth.ts             # Authentication
│   │   └── useProgress.ts         # Progress tracking
│   ├── stores/
│   │   ├── sessionStore.ts        # Session state
│   │   ├── chatStore.ts           # Chat state
│   │   ├── userStore.ts           # User preferences
│   │   ├── progressStore.ts       # Progress tracking
│   │   └── uiStore.ts             # UI state
│   ├── types/
│   │   ├── api.ts                 # API response types
│   │   ├── session.ts             # Session types
│   │   ├── character.ts           # Character types
│   │   ├── scenario.ts            # Scenario types
│   │   ├── feedback.ts            # Feedback types
│   │   └── user.ts                # User types
│   ├── utils/
│   │   ├── api.ts                 # API client
│   │   ├── websocket.ts           # WebSocket client
│   │   ├── auth.ts                # Authentication utilities
│   │   └── validation.ts          # Form validation
│   └── styles/
│       ├── globals.css            # Global styles
│       └── components.css         # Component-specific styles
```

### 2.3 Key Frontend Components

#### Scenario Selection Interface
```typescript
interface ScenarioCardProps {
  scenario: Scenario;
  onSelect: (scenarioId: string) => void;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  characters: Character[];
  completed?: boolean;
  userRating?: number;
}

const ScenarioCard: React.FC<ScenarioCardProps> = ({
  scenario,
  onSelect,
  difficulty,
  characters,
  completed = false,
  userRating
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-900">
          {scenario.name}
        </h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
          difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {difficulty}
        </span>
      </div>
      
      <p className="text-gray-600 mb-4">{scenario.description}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          {characters.map(character => (
            <CharacterAvatar key={character.id} character={character} size="sm" />
          ))}
        </div>
        
        <Button 
          onClick={() => onSelect(scenario.id)}
          variant={completed ? "secondary" : "primary"}
        >
          {completed ? "Retry" : "Start"}
        </Button>
      </div>
    </div>
  );
};
```

#### Chat Interface
```typescript
interface ChatInterfaceProps {
  sessionId: string;
  characters: Character[];
  onMessage: (message: string) => void;
  conversationHistory: Message[];
  currentCharacter?: Character;
  isTyping: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  characters,
  onMessage,
  conversationHistory,
  currentCharacter,
  isTyping
}) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationHistory]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {characters.map(character => (
              <CharacterAvatar 
                key={character.id} 
                character={character} 
                isActive={currentCharacter?.id === character.id}
              />
            ))}
          </div>
          <SessionStatus sessionId={sessionId} />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversationHistory.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
        
        {isTyping && <TypingIndicator characters={characters} />}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isTyping}
          />
          <Button type="submit" disabled={!message.trim() || isTyping}>
            Send
          </Button>
        </form>
      </div>
    </div>
  );
};
```

#### Feedback Display
```typescript
interface FeedbackDisplayProps {
  feedback: Feedback;
  scenario: Scenario;
  conversationHistory: Message[];
  onRetry?: () => void;
  onNext?: () => void;
}

const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({
  feedback,
  scenario,
  conversationHistory,
  onRetry,
  onNext
}) => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Session Complete!
        </h1>
        <p className="text-gray-600">
          Great job completing the <strong>{scenario.name}</strong> scenario
        </p>
      </div>

      {/* Rating */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center mb-4">
          <RatingDisplay rating={feedback.rating} />
        </div>
        <p className="text-center text-gray-700">
          {feedback.overall_assessment}
        </p>
      </div>

      {/* Strengths */}
      <div className="bg-green-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-green-800 mb-3">
          ✅ Communication Strengths
        </h3>
        <StrengthsList strengths={feedback.strengths_text} />
      </div>

      {/* Improvements */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-yellow-800 mb-3">
          🔧 Areas for Improvement
        </h3>
        <ImprovementsList improvements={feedback.improvements_text} />
      </div>

      {/* Takeaways */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-blue-800 mb-3">
          💡 Key Takeaways
        </h3>
        <TakeawaysList takeaways={feedback.key_takeaways_text} />
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        {onRetry && (
          <Button variant="secondary" onClick={onRetry}>
            Try Again
          </Button>
        )}
        {onNext && (
          <Button variant="primary" onClick={onNext}>
            Next Scenario
          </Button>
        )}
      </div>
    </div>
  );
};
```

## Phase 3: Real-time Communication (1-2 weeks)

### 3.1 WebSocket Integration

Add real-time capabilities for live conversations:

```python
# WebSocket endpoints
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        # Add connection to session
        await connection_manager.connect(websocket, session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message and generate character responses
            responses = await process_message(session_id, data)
            
            # Send responses to client
            for response in responses:
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, session_id)
```

### 3.2 WebSocket Events

```typescript
// Client-side WebSocket events
interface WebSocketEvents {
  'session_started': { 
    sessionId: string; 
    characters: Character[];
    scenario: Scenario;
  };
  'character_response': { 
    character: Character; 
    message: string;
    turnCount: number;
  };
  'character_typing': {
    character: Character;
    isTyping: boolean;
  };
  'session_ended': { 
    sessionId: string; 
    feedback: Feedback;
  };
  'error': { 
    message: string; 
    code: string;
  };
  'session_status': {
    sessionId: string;
    status: 'active' | 'ended' | 'error';
    turnCount: number;
    maxTurns: number;
  };
}
```

### 3.3 Real-time Features

- **Live character responses** as they're generated
- **Typing indicators** for character responses
- **Session status updates** in real-time
- **Automatic feedback generation** when sessions end
- **Connection status** and reconnection handling

## Phase 4: Enhanced User Experience (2-3 weeks)

### 4.1 User Authentication & Profiles

```typescript
// User profile system
interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  preferences: {
    preferredScenarios: string[];
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
    notificationSettings: {
      email: boolean;
      push: boolean;
      feedback: boolean;
    };
    privacySettings: {
      shareProgress: boolean;
      anonymousMode: boolean;
    };
  };
  progress: {
    completedScenarios: string[];
    skillImprovements: SkillMetric[];
    totalSessions: number;
    averageRating: number;
    streakDays: number;
  };
  achievements: Achievement[];
}
```

### 4.2 Progress Tracking Dashboard

```typescript
// Progress visualization components
interface ProgressDashboardProps {
  userProgress: UserProgress;
  skillMetrics: SkillMetric[];
  completedScenarios: CompletedScenario[];
  achievements: Achievement[];
}

const ProgressDashboard: React.FC<ProgressDashboardProps> = ({
  userProgress,
  skillMetrics,
  completedScenarios,
  achievements
}) => {
  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Sessions Completed" 
          value={userProgress.totalSessions}
          icon="📊"
        />
        <StatCard 
          title="Average Rating" 
          value={userProgress.averageRating.toFixed(1)}
          icon="⭐"
        />
        <StatCard 
          title="Current Streak" 
          value={`${userProgress.streakDays} days`}
          icon="🔥"
        />
        <StatCard 
          title="Achievements" 
          value={achievements.length}
          icon="🏆"
        />
      </div>

      {/* Skill Progress Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Skill Development</h3>
        <SkillChart metrics={skillMetrics} />
      </div>

      {/* Recent Scenarios */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Recent Sessions</h3>
        <ScenarioHistory scenarios={completedScenarios} />
      </div>

      {/* Achievements */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Achievements</h3>
        <AchievementGrid achievements={achievements} />
      </div>
    </div>
  );
};
```

### 4.3 Advanced Features

- **Scenario recommendations** based on user progress
- **Skill assessment** and improvement tracking
- **Achievement system** with badges and milestones
- **Social features** (sharing achievements, leaderboards)
- **Custom scenario creation** (future enhancement)
- **Export progress** data for external analysis

## Phase 5: Mobile Optimization (1-2 weeks)

### 5.1 Responsive Design

- **Mobile-first approach** with Tailwind CSS
- **Touch-optimized** chat interface
- **Swipe gestures** for character switching
- **Responsive grid layouts** for all screen sizes
- **Optimized typography** for mobile reading

### 5.2 Progressive Web App (PWA)

```typescript
// PWA configuration
const pwaConfig = {
  manifest: {
    name: 'Flir - Social Skills Training',
    short_name: 'Flir',
    description: 'Practice difficult conversations with AI characters',
    theme_color: '#3B82F6',
    background_color: '#FFFFFF',
    display: 'standalone',
    orientation: 'portrait',
    start_url: '/',
    scope: '/',
    icons: [
      {
        src: '/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'any maskable'
      },
      {
        src: '/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any maskable'
      }
    ],
    categories: ['education', 'productivity', 'social'],
    screenshots: [
      {
        src: '/screenshot-mobile.png',
        sizes: '390x844',
        type: 'image/png',
        form_factor: 'narrow'
      }
    ]
  },
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\./,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 100,
            maxAgeSeconds: 60 * 60 * 24 // 24 hours
          }
        }
      }
    ]
  }
};
```

### 5.3 Mobile-Specific Features

- **Offline support** for completed scenarios
- **Push notifications** for session reminders
- **Voice input** integration (future enhancement)
- **Haptic feedback** for interactions
- **Gesture navigation** for better UX

## Technical Implementation Details

### Backend API Structure

```python
# FastAPI application setup
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

app = FastAPI(
    title="Flir API",
    description="Social Skills Training Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://flir-app.vercel.app",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Authentication
security = HTTPBearer()

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    token: str = Query(...)
):
    # Verify authentication
    user = await verify_token(token)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await websocket.accept()
    try:
        # Add connection to session
        await connection_manager.connect(websocket, session_id, user.id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message and generate character responses
            responses = await conversation_service.process_message(
                session_id, 
                data, 
                user.id
            )
            
            # Send responses to client
            for response in responses:
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend State Management

```typescript
// Zustand store for session management
interface SessionStore {
  currentSession: Session | null;
  conversationHistory: Message[];
  characters: Character[];
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  
  // Actions
  startSession: (scenarioId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  switchCharacter: (characterId: string) => Promise<void>;
  endSession: () => Promise<void>;
  clearError: () => void;
}

const useSessionStore = create<SessionStore>((set, get) => ({
  currentSession: null,
  conversationHistory: [],
  characters: [],
  isLoading: false,
  isTyping: false,
  error: null,

  startSession: async (scenarioId: string) => {
    set({ isLoading: true, error: null });
    try {
      const session = await api.sessions.create(scenarioId);
      set({ 
        currentSession: session,
        characters: session.characters,
        conversationHistory: [],
        isLoading: false 
      });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  sendMessage: async (message: string) => {
    const { currentSession } = get();
    if (!currentSession) return;

    // Add user message to history
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
      character: null
    };

    set(state => ({
      conversationHistory: [...state.conversationHistory, userMessage],
      isTyping: true
    }));

    try {
      const responses = await api.conversations.sendMessage(
        currentSession.id, 
        message
      );

      // Add character responses to history
      set(state => ({
        conversationHistory: [...state.conversationHistory, ...responses],
        isTyping: false
      }));

      // Check if session should end
      if (currentSession.turnCount >= currentSession.maxTurns) {
        await get().endSession();
      }
    } catch (error) {
      set({ error: error.message, isTyping: false });
    }
  },

  endSession: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    try {
      const feedback = await api.feedback.generate(currentSession.id);
      // Handle feedback display
      set({ 
        currentSession: null,
        conversationHistory: [],
        characters: []
      });
    } catch (error) {
      set({ error: error.message });
    }
  },

  clearError: () => set({ error: null })
}));
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scenario_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    turn_count INTEGER DEFAULT 0,
    max_turns INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    character_id VARCHAR(255),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    rating VARCHAR(10) NOT NULL,
    overall_assessment TEXT NOT NULL,
    strengths_text TEXT NOT NULL,
    improvements_text TEXT NOT NULL,
    key_takeaways_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scenario_id VARCHAR(255) NOT NULL,
    completed_at TIMESTAMP DEFAULT NOW(),
    rating VARCHAR(10),
    skill_improvements JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_feedback_session_id ON feedback(session_id);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
```

## Deployment Strategy

### Docker Configuration

```yaml
# docker-compose.yml for full stack deployment
version: '3.8'

services:
  # Database
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: flir
      POSTGRES_USER: flir_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U flir_user -d flir"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  api:
    build: 
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://flir_user:${DB_PASSWORD}@db:5432/flir
      - REDIS_URL=redis://redis:6379
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./api:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXT_PUBLIC_WS_URL=ws://api:8000
    depends_on:
      - api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # Discord Bot (existing)
  discord-bot:
    build:
      context: .
      dockerfile: Dockerfile.discord
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - API_URL=http://api:8000
    depends_on:
      - api
    volumes:
      - ./discord_bot.py:/app/discord_bot.py
      - ./characters.py:/app/characters.py
      - ./scenarios.py:/app/scenarios.py
      - ./services:/app/services

volumes:
  postgres_data:
  redis_data:
```

### Environment Configuration

```env
# Backend environment variables
DATABASE_URL=postgresql://flir_user:password@localhost:5432/flir
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_jwt_secret_key
CORS_ORIGINS=http://localhost:3000,https://flir-app.vercel.app

# Discord Bot environment variables
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_discord_server_id
API_URL=http://localhost:8000

# Frontend environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=Flir
NEXT_PUBLIC_APP_DESCRIPTION=Social Skills Training Platform
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      - name: Run tests
        run: pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Build and deploy API
      - name: Deploy API to Render
        uses: render-actions/deploy@v1
        with:
          service-id: ${{ secrets.RENDER_API_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
      
      # Build and deploy Frontend
      - name: Deploy Frontend to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

## Benefits & Timeline

### Benefits of Frontend Implementation

#### User Experience Improvements
- **Better visual design** with custom UI components
- **Mobile optimization** for on-the-go practice
- **Progress tracking** with visual dashboards
- **Offline capabilities** with PWA features
- **Real-time feedback** and notifications

#### Technical Benefits
- **Scalability** with proper API architecture
- **Maintainability** with separated concerns
- **Extensibility** for future features
- **Performance** with optimized data fetching
- **Testing** with isolated components

#### Business Benefits
- **Broader reach** beyond Discord users
- **Better analytics** and user tracking
- **Monetization options** with user accounts
- **Professional appearance** for enterprise clients
- **SEO optimization** for discoverability

### Implementation Timeline

**Total Timeline: 8-12 weeks**

#### Phase 1: Backend API (2-3 weeks)
- **Week 1**: API structure and basic endpoints
- **Week 2**: Service layer refactoring and database integration
- **Week 3**: Authentication and WebSocket implementation

#### Phase 2: Frontend Development (3-4 weeks)
- **Week 4**: Project setup and core components
- **Week 5**: Chat interface and scenario selection
- **Week 6**: Feedback display and progress tracking
- **Week 7**: User authentication and profiles

#### Phase 3: Real-time Communication (1-2 weeks)
- **Week 8**: WebSocket integration and real-time features

#### Phase 4: Enhanced UX (2-3 weeks)
- **Week 9**: Advanced features and progress dashboard
- **Week 10**: Achievement system and social features
- **Week 11**: Performance optimization and testing

#### Phase 5: Mobile Optimization (1-2 weeks)
- **Week 12**: PWA implementation and mobile optimization

### Success Metrics

#### Technical Metrics
- **API Response Time**: <200ms for all endpoints
- **WebSocket Latency**: <100ms for real-time messages
- **Frontend Load Time**: <2s for initial page load
- **Mobile Performance**: 90+ Lighthouse score

#### User Experience Metrics
- **User Engagement**: 3+ sessions per week
- **Session Completion**: 80%+ completion rate
- **User Retention**: 70%+ monthly retention
- **Mobile Usage**: 60%+ of total sessions

#### Business Metrics
- **User Acquisition**: 1000+ users in first 3 months
- **Conversion Rate**: 15%+ to premium features
- **User Satisfaction**: 4.5+ star rating
- **Platform Adoption**: 50/50 split between Discord and web

---

*This implementation plan provides a comprehensive roadmap for adding a modern web frontend to the Flir social skills training platform while maintaining the existing Discord bot functionality.*
