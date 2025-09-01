# Mental Health Chatbot - Comprehensive Documentation

## Overview

This document provides complete documentation for the Mental Health Chatbot application, covering both frontend and backend components. The application is a comprehensive mental health support system built with Vue 3/Nuxt 3 frontend and FastAPI backend, providing real-time conversational AI assistance with advanced features including crisis detection, emotional analysis, speech recognition, structured assessments, and multi-language support.

## System Architecture

### Technology Stack

**Frontend:**
- **Framework**: Vue 3 with Composition API
- **Meta-framework**: Nuxt 3 with SSR capabilities
- **Real-time Communication**: WebSocket API
- **Speech**: Web Speech API for recognition and synthesis
- **Styling**: Tailwind CSS with responsive design
- **Internationalization**: i18n support for Indonesian/English

**Backend:**
- **Framework**: FastAPI with async/await support
- **Vector Database**: Qdrant for semantic search and embeddings
- **AI Models**: 
  - Primary: Ollama (Gemma 3:4b)
  - Fallback: OpenAI GPT-4
  - Embeddings: all-MiniLM-L6-v2
- **Databases**: 
  - PostgreSQL (primary data storage)
  - MongoDB (document storage)
  - Redis (caching and sessions)
- **Real-time Communication**: WebSocket
- **Authentication**: JWT with HTTPBearer

## Frontend Application

### Core Functionality

#### 1. **Conversational AI Interface**
- Real-time streaming chat responses via WebSocket connections
- Message history management with local storage persistence
- Markdown-to-HTML conversion for rich text responses
- Auto-resizing text input with keyboard shortcuts

#### 2. **Crisis Detection & Emergency Support**
- Automatic crisis detection in user messages
- Emergency contact information display
- WhatsApp support integration
- Crisis alert system with dismissible notifications

#### 3. **Emotional Analysis**
- Real-time emotion detection from user input
- Emotion-based response customization
- Visual emotion indicators with emoji representations
- Counselor response generation based on detected emotions

#### 4. **Speech Recognition & Synthesis**
- Voice input using Web Speech API
- Text-to-speech output for AI responses
- Fluid conversation mode for hands-free interaction
- Speech transcript management and export
- Mobile-optimized speech controls

#### 5. **Assessment System**
- Dialog-based mental health assessments
- Dynamic question retrieval from vector database
- Progress tracking and state management
- Assessment completion with recommendations
- Problem category detection and suggestions

#### 6. **Multi-language Support**
- Dynamic language switching (English/Indonesian)
- Intelligent translation based on user preferences
- Localized UI components and messages
- Language-aware response generation

#### 7. **Data Management**
- Chat history export functionality
- Data deletion requests
- Session management with unique identifiers
- Local storage integration for persistence

### Frontend Components

1. **Main Component:** `index.vue`
   - Vue 3 Composition API
   - Reactive state management
   - Event handling and lifecycle management
   - UI component orchestration

2. **Composable:** `useOllamaChat.ts`
   - Centralized chat logic
   - WebSocket connection management
   - API service integrations
   - State management for chat, assessment, and session data

### State Management

**Reactive References:**
- `messages`: Chat message history
- `isStreaming`: Streaming status indicator
- `assessmentProgress`: Assessment state tracking
- `currentProblemCategory`: Active problem category
- `sessionId` & `conversationId`: Session identifiers
- `detectedProblemCategory`: AI-detected problem category
- `shouldShowAssessmentSuggestion`: Assessment suggestion flag

### Frontend Configuration

**Environment Variables:**
- `config.public.customChatApiUrl`: REST API base URL
- `config.public.customChatWsUrl`: WebSocket endpoint URL
- `config.public.customChatApiKey`: API authentication key

## Backend Services

### Core Configuration

The backend is configured through environment variables and the `Settings` class in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Mental Health Chat API"
    
    # Vector Database (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # AI Models
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    OPENAI_API_KEY: str = ""
    
    # Crisis Detection Keywords
    CRISIS_KEYWORDS: List[str] = [
        "bunuh diri", "suicide", "mati", "death",
        "tidak ada harapan", "no hope", "putus asa"
    ]
```

### Backend Services

#### 1. Chat Service (`app/services/chat_service.py`)

**Purpose**: Core conversational AI with mental health specialization

**Key Features**:
- Real-time WebSocket communication
- Streaming AI responses for better user experience
- Crisis detection and immediate intervention
- Context-aware responses using semantic search
- Session management per client
- Integration with assessment workflows

**Message Flow**:
1. Receive user message
2. Perform semantic search for relevant context
3. Check for crisis indicators
4. Generate AI response with context
5. Stream response back to client
6. Update conversation history

#### 2. Semantic Search Service (`app/services/semantic_search_service.py`)

**Purpose**: Intelligent content retrieval using vector embeddings and semantic similarity

**Vector Collections**:
- `mental-health-problems`: Problem categories and descriptions
- `mental-health-assessments`: Assessment questions with flow control
- `mental-health-suggestions`: Evidence-based therapeutic recommendations
- `mental-health-feedback`: User feedback and follow-up prompts
- `mental-health-training`: Training data for model improvement

**Key Features**:
- Semantic similarity search with configurable score thresholds
- Multi-collection search capabilities
- Domain-specific filtering (stress, anxiety, trauma, general)
- Real-time embedding generation
- Context-aware content matching

**Search Process**:
1. Generate query embedding using sentence transformer
2. Search vector database for similar content
3. Apply filters (domain, score threshold)
4. Return ranked results with metadata

#### 3. Assessment Service (`app/services/assessment_service.py`)

**Purpose**: Structured mental health assessments with dynamic question flow

**Key Features**:
- Dynamic question sequencing based on user responses
- Progress tracking with completion percentages
- Session state management across conversations
- Integration with vector database for question retrieval
- Support for multiple response types:
  - `scale`: Likert scale responses (1-5, 1-10)
  - `text`: Open-ended text responses
  - `multiple_choice`: Predefined options

**Assessment Flow**:
1. User triggers assessment or system detects need
2. Search vector database for relevant questions
3. Initialize assessment session with first question
4. Process user responses and determine next question
5. Track progress and maintain session state
6. Generate final recommendations based on responses

#### 4. Vector Service (`app/services/vector_service.py`)

**Purpose**: Direct interface to Qdrant vector database

**Key Features**:
- Collection management and initialization
- Vector similarity search with filtering
- Batch data operations
- Connection pooling and error handling
- Automatic collection creation with proper schemas

#### 5. Embedding Service (`app/services/embedding_service.py`)

**Purpose**: Text-to-vector conversion for semantic search

**Key Features**:
- Sentence transformer model integration (all-MiniLM-L6-v2)
- Batch embedding generation for efficiency
- Caching for performance optimization
- Support for multiple languages (Indonesian, English)
- Automatic model downloading and initialization

#### 6. Ollama Service (`app/services/ollama_service.py`)

**Purpose**: Integration with local Ollama AI models

**Key Features**:
- Direct API integration with Ollama
- Model configuration and parameter tuning
- Response streaming for real-time chat
- Error handling with OpenAI fallback
- Model health monitoring

**Configuration**:
- Model: Gemma 3:4b (optimized for mental health conversations)
- Temperature: 0.7 (balanced creativity and consistency)
- Max Tokens: 2000 (comprehensive responses)

#### 7. Language Service (`app/services/language_service.py`)

**Purpose**: Multi-language support and localization

**Key Features**:
- Automatic language detection
- Support for Indonesian and English
- Localized responses and assessments
- Cultural context preservation
- Language-specific crisis detection

#### 8. Translation Service (`app/services/translation_service.py`)

**Purpose**: Real-time translation capabilities

**Key Features**:
- Cross-language conversation support
- Context-aware translation
- Mental health terminology preservation
- Cultural sensitivity in translations

#### 9. Data Import Service (`app/services/data_import_service.py`)

**Purpose**: Bulk data ingestion and management

**Key Features**:
- Bulk data ingestion into vector database
- Data validation and cleaning
- Batch processing for large datasets
- CSV/JSON import support
- Data transformation and normalization

## API Endpoints

### Chat Endpoints
- `POST /api/v1/chat` - Send message and receive complete response
- `POST /api/v1/chat/stream` - Send message with streaming response
- `WebSocket /api/v1/ws/{client_id}` - Real-time chat connection
- `WebSocket /api/v1/ws/chat/stream` - Streaming WebSocket chat

### Assessment Endpoints
- `POST /api/v1/assessment/start` - Initialize structured assessment
- `POST /api/v1/assessment/respond` - Process user responses
- `GET /api/v1/assessment/status` - Get current assessment status
- `POST /api/v1/assessment/cancel` - Cancel ongoing assessment
- `POST /api/v1/assessment/recommendations` - Get personalized recommendations

### Vector Search Endpoints
- `POST /api/v1/vector/search` - Semantic search across collections

### Conversation Management
- `GET /api/v1/conversation/history` - Get chat history (authenticated)
- `DELETE /api/v1/conversation/clear` - Clear history (authenticated)

### Model Management
- `GET /api/v1/model/status` - Check model status
- `POST /api/v1/model/pull` - Download model

## Data Models and Schemas

### Core Models (`app/models/vector_models.py`)

```python
class ProblemCategory(BaseModel):
    category_id: str
    sub_category_id: str
    category: str
    problem_name: str
    description: str
    domain: str  # stress, anxiety, trauma, general

class AssessmentQuestion(BaseModel):
    question_id: str
    sub_category_id: str
    batch_id: str
    question_text: str
    response_type: ResponseType  # scale, text, multiple_choice
    next_step: Optional[str]
    clusters: Optional[List[str]]
    domain: str

class TherapeuticSuggestion(BaseModel):
    suggestion_id: str
    sub_category_id: str
    cluster: str
    suggestion_text: str
    resource_link: Optional[str]
    evidence_based: bool
    domain: str
```

## WebSocket Communication

### Message Types

**Client to Server**:
```json
{
  "type": "message",
  "content": "User message text",
  "session_data": {
    "sessionId": "session123",
    "conversationId": "conv456",
    "preferredLanguage": "en",
    "mode": "chat",
    "emotion": {
      "detected": "neutral",
      "confidence": 0.8
    }
  },
  "semantic_context": [],
  "problem_category": "stress",
  "assessment_progress": {
    "current_question": 1,
    "total_questions": 10
  }
}
```

**Server to Client**:
```json
{
  "type": "chunk",
  "content": "Partial response text",
  "is_complete": false
}

{
  "type": "complete",
  "content": "Complete response",
  "detected_problem_category": "anxiety",
  "should_show_assessment": true,
  "assessment_questions": [...]
}

{
  "type": "error",
  "message": "Error description"
}
```

## Frontend-Backend Integration

### 1. Chat Service Integration

**Frontend (`useOllamaChat.ts`):**
- `sendMessage()`: Sends messages via WebSocket
- `sendMessageStream()`: Handles streaming responses
- `connectWebSocket()`: Establishes WebSocket connection
- `disconnectWebSocket()`: Closes connection

**Backend Integration:**
- WebSocket endpoint: `config.public.customChatWsUrl`
- Message format includes session data, semantic context, and assessment progress
- Real-time streaming with chunk processing

### 2. Vector Search Integration

**Frontend Functions:**
- `searchMentalHealthContext(query)`: Search mental health problems collection
- `getProblemCategories()`: Retrieve problem categories
- `getAssessmentQuestions(problemCategory)`: Get assessment questions
- `getTherapeuticSuggestions(problemCategory)`: Fetch therapeutic suggestions

**Backend Collections:**
- `mental-health-problems`: Problem categories and descriptions
- `mental-health-assessments`: Assessment questions with flow control
- `mental-health-suggestions`: Evidence-based therapeutic recommendations

### 3. Assessment Flow Integration

**Frontend Functions:**
- `startAssessment(problemCategory)`: Initialize assessment
- `continueAssessment(response, questionId)`: Submit responses
- `getAssessmentStatus()`: Check assessment state
- `cancelAssessment()`: Terminate assessment

**Backend Processing:**
- Dynamic question sequencing based on responses
- Progress tracking with completion percentages
- Session state management across conversations
- Integration with vector database for question retrieval

### 4. Conversation Management

**Frontend Functions:**
- `getConversationHistory()`: Retrieve chat history
- `clearConversationHistory()`: Clear conversation data

**Backend Features:**
- User-specific history tracking
- Authentication-protected endpoints
- Privacy controls and data retention

## Security and Authentication

### Authentication
- **Frontend**: Bearer token management with API key
- **Backend**: JWT tokens with HTTPBearer scheme
- **Session Management**: Unique session identifiers for user isolation
- **Token Verification**: Protected endpoints require authentication

### CORS Configuration
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://ringan-landing.vercel.app"
]
```

### Crisis Detection
- **Real-time Monitoring**: Crisis keywords detection in user messages
- **Immediate Intervention**: Emergency contact information display
- **Escalation Procedures**: WhatsApp support integration
- **Alert System**: Dismissible crisis notifications

### Data Privacy
- **Local Storage**: Sensitive data stored locally with deletion capabilities
- **Input Validation**: Client-side and server-side validation
- **Error Handling**: Comprehensive error catching and user feedback

## Performance Optimization

### Frontend Optimizations
1. **Streaming Responses**: Real-time chunk processing for better UX
2. **WebSocket Reuse**: Connection pooling and management
3. **Lazy Loading**: On-demand component and data loading
4. **Debounced Inputs**: Optimized user input handling
5. **Memory Management**: Proper cleanup of WebSocket connections

### Backend Optimizations
1. **Caching Strategy**: Redis for session data and frequent queries
2. **Async Operations**: Full async/await implementation
3. **Connection Pooling**: Database connection optimization
4. **Embedding Caching**: Performance optimization for repeated searches
5. **Streaming Responses**: Non-blocking I/O operations

## Monitoring and Logging

### Frontend Monitoring
- **Error Tracking**: Comprehensive error catching and reporting
- **Performance Metrics**: WebSocket connection monitoring
- **User Analytics**: Interaction tracking and usage patterns

### Backend Monitoring
- **Structured Logging**: Python logging module with request/response logging
- **Health Checks**: Database connectivity and AI model availability
- **Performance Metrics**: Response times and throughput monitoring
- **Error Alerting**: Real-time error notification system

## Mobile Responsiveness and Accessibility

### Mobile Features
- Touch-optimized controls for speech functionality
- Responsive design for various screen sizes
- Mobile-specific UI adaptations
- Gesture support for common actions

### Accessibility Features
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Voice interaction capabilities
- Clear visual feedback for all actions

## Deployment and Scaling

### Environment Configuration
- Development, staging, and production environments
- Environment-specific settings for frontend and backend
- Secret management and configuration validation

### Scalability Considerations
- **Frontend**: CDN deployment with Vercel/Netlify
- **Backend**: Horizontal scaling with load balancers
- **Database**: Connection pooling and caching layers
- **Microservices**: Architecture readiness for service separation

## Error Handling and Fallbacks

### Frontend Error Handling
- **WebSocket Reconnection**: Automatic reconnection on connection loss
- **API Fallbacks**: Graceful degradation when services unavailable
- **User Feedback**: Clear error messages and recovery suggestions

### Backend Error Handling
- **Exception Management**: Comprehensive error catching
- **Fallback Mechanisms**: OpenAI when Ollama fails
- **Retry Logic**: Automatic retries with exponential backoff
- **Circuit Breakers**: Protection against cascading failures

## Future Enhancements

### Planned Features
- **Advanced Analytics**: Real-time dashboard and reporting
- **Multi-modal Support**: Voice and image processing
- **External Integrations**: Mental health resource APIs
- **Enhanced Personalization**: Machine learning-based recommendations
- **Mobile App**: Native iOS/Android applications

### Technical Improvements
- **GraphQL API**: More efficient data fetching
- **Advanced Caching**: Multi-layer caching strategies
- **A/B Testing**: Feature experimentation framework
- **Enhanced Security**: Advanced authentication and authorization
- **Real-time Analytics**: Live user behavior tracking

This comprehensive documentation provides a complete technical reference for understanding how the frontend and backend components work together to deliver an intelligent, accessible, and empathetic mental health support system through conversational AI, structured assessments, and evidence-based therapeutic recommendations.