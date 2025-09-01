# Mental Health Chatbot - Backend Services Documentation

## Overview

This document provides comprehensive documentation for the backend services powering the Mental Health Chatbot application. The backend is built with FastAPI and integrates multiple specialized services to provide intelligent, context-aware mental health support.

## Architecture Overview

### Technology Stack
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

## Core Services

### 1. Chat Service (`app/services/chat_service.py`)

**Purpose**: Core conversational AI with mental health specialization

**Key Features**:
- Real-time WebSocket communication
- Streaming AI responses for better user experience
- Crisis detection and immediate intervention
- Context-aware responses using semantic search
- Session management per client
- Integration with assessment workflows

**API Endpoints**:
- `POST /api/v1/chat` - Send message and receive complete response
- `POST /api/v1/chat/stream` - Send message with streaming response
- `WebSocket /api/v1/ws/{client_id}` - Real-time chat connection
- `WebSocket /api/v1/ws/chat/stream` - Streaming WebSocket chat

**Message Flow**:
1. Receive user message
2. Perform semantic search for relevant context
3. Check for crisis indicators
4. Generate AI response with context
5. Stream response back to client
6. Update conversation history

### 2. Semantic Search Service (`app/services/semantic_search_service.py`)

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

**API Endpoints**:
- `POST /api/v1/vector/search` - Semantic search across collections

**Search Process**:
1. Generate query embedding using sentence transformer
2. Search vector database for similar content
3. Apply filters (domain, score threshold)
4. Return ranked results with metadata

### 3. Assessment Service (`app/services/assessment_service.py`)

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

**API Endpoints**:
- `POST /api/v1/assessment/start` - Initialize structured assessment
- `POST /api/v1/assessment/respond` - Process user responses
- `GET /api/v1/assessment/status` - Get current assessment status
- `POST /api/v1/assessment/cancel` - Cancel ongoing assessment
- `POST /api/v1/assessment/recommendations` - Get personalized recommendations

**Assessment Flow**:
1. User triggers assessment or system detects need
2. Search vector database for relevant questions
3. Initialize assessment session with first question
4. Process user responses and determine next question
5. Track progress and maintain session state
6. Generate final recommendations based on responses

**Data Models**:
```python
class AssessmentQuestion(BaseModel):
    question_id: str
    sub_category_id: str
    batch_id: str
    question_text: str
    response_type: ResponseType
    next_step: Optional[str]
    clusters: Optional[List[str]]
    domain: str
```

### 4. Vector Service (`app/services/vector_service.py`)

**Purpose**: Direct interface to Qdrant vector database

**Key Features**:
- Collection management and initialization
- Vector similarity search with filtering
- Batch data operations
- Connection pooling and error handling
- Automatic collection creation with proper schemas

**Core Operations**:
- `connect()`: Establish connection to Qdrant
- `create_collections()`: Initialize all required collections
- `search_similar()`: Perform vector similarity search
- `upsert_points()`: Insert or update vector points
- `delete_points()`: Remove vectors from collections

### 5. Embedding Service (`app/services/embedding_service.py`)

**Purpose**: Text-to-vector conversion for semantic search

**Key Features**:
- Sentence transformer model integration (all-MiniLM-L6-v2)
- Batch embedding generation for efficiency
- Caching for performance optimization
- Support for multiple languages (Indonesian, English)
- Automatic model downloading and initialization

**Core Operations**:
- `generate_embedding(text)`: Convert text to vector
- `generate_batch_embeddings(texts)`: Process multiple texts
- `initialize()`: Load and prepare embedding model

### 6. Ollama Service (`app/services/ollama_service.py`)

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

### 7. Language Service (`app/services/language_service.py`)

**Purpose**: Multi-language support and localization

**Key Features**:
- Automatic language detection
- Support for Indonesian and English
- Localized responses and assessments
- Cultural context preservation
- Language-specific crisis detection

### 8. Translation Service (`app/services/translation_service.py`)

**Purpose**: Real-time translation capabilities

**Key Features**:
- Cross-language conversation support
- Context-aware translation
- Mental health terminology preservation
- Cultural sensitivity in translations

### 9. Data Import Service (`app/services/data_import_service.py`)

**Purpose**: Bulk data ingestion and management

**Key Features**:
- Bulk data ingestion into vector database
- Data validation and cleaning
- Batch processing for large datasets
- CSV/JSON import support
- Data transformation and normalization

## API Endpoints Summary

### Chat Endpoints
- `POST /api/v1/chat` - Send message
- `POST /api/v1/chat/stream` - Streaming chat
- `WebSocket /api/v1/ws/{client_id}` - Real-time chat
- `WebSocket /api/v1/ws/chat/stream` - Streaming WebSocket

### Assessment Endpoints
- `POST /api/v1/assessment/start` - Start assessment
- `POST /api/v1/assessment/respond` - Submit response
- `GET /api/v1/assessment/status` - Get status
- `POST /api/v1/assessment/cancel` - Cancel assessment
- `POST /api/v1/assessment/recommendations` - Get recommendations

### Vector Search Endpoints
- `POST /api/v1/vector/search` - Semantic search

### Conversation Management
- `GET /api/v1/conversation/history` - Get chat history
- `DELETE /api/v1/conversation/clear` - Clear history

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
    "user_id": "user123",
    "conversation_id": "conv456"
  },
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

## Security and Authentication

### Authentication
- JWT tokens with HTTPBearer scheme
- Token verification for protected endpoints
- Session management with Redis

### CORS Configuration
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://ringan-landing.vercel.app"
]
```

### Crisis Detection
- Real-time monitoring for crisis keywords
- Immediate intervention protocols
- Emergency contact information
- Escalation procedures

## Performance Optimization

### Caching Strategy
- Redis for session data and frequent queries
- Embedding caching for repeated searches
- Connection pooling for database operations

### Async Operations
- Full async/await implementation
- Non-blocking I/O operations
- Concurrent request handling
- Streaming responses for better UX

## Monitoring and Logging

### Logging Configuration
- Structured logging with Python logging module
- Request/response logging
- Error tracking and alerting
- Performance metrics collection

### Health Checks
- Database connectivity monitoring
- AI model availability checks
- Vector database status verification
- Service dependency health

## Deployment and Scaling

### Environment Configuration
- Development, staging, and production environments
- Environment-specific settings
- Secret management
- Configuration validation

### Scalability Considerations
- Horizontal scaling with load balancers
- Database connection pooling
- Caching layers for performance
- Microservice architecture readiness

## Error Handling

### Exception Management
- Comprehensive error catching
- User-friendly error messages
- Fallback mechanisms (OpenAI when Ollama fails)
- Graceful degradation

### Retry Logic
- Automatic retries for transient failures
- Exponential backoff strategies
- Circuit breaker patterns
- Timeout management

## Future Enhancements

### Planned Features
- Advanced analytics and reporting
- Multi-modal support (voice, images)
- Integration with external mental health resources
- Enhanced personalization algorithms
- Mobile app API support

### Technical Improvements
- GraphQL API implementation
- Advanced caching strategies
- Real-time analytics dashboard
- A/B testing framework
- Enhanced security measures

This backend architecture provides a robust, scalable foundation for delivering intelligent mental health support through conversational AI, structured assessments, and evidence-based therapeutic recommendations.