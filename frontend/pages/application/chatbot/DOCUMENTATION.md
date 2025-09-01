# Chatbot Application Documentation

## Overview

The chatbot application located at `/d:/AITek/ringan-landing/frontend/pages/application/chatbot/index.vue` is a comprehensive mental health support chatbot built with Vue 3 and Nuxt 3. This application provides real-time conversational AI assistance with advanced features including crisis detection, emotional analysis, speech recognition, assessment flows, and multi-language support.

## Core Functionality

### 1. **Conversational AI Interface**
- Real-time streaming chat responses via WebSocket connections
- Message history management with local storage persistence
- Markdown-to-HTML conversion for rich text responses
- Auto-resizing text input with keyboard shortcuts

### 2. **Crisis Detection & Emergency Support**
- Automatic crisis detection in user messages
- Emergency contact information display
- WhatsApp support integration
- Crisis alert system with dismissible notifications

### 3. **Emotional Analysis**
- Real-time emotion detection from user input
- Emotion-based response customization
- Visual emotion indicators with emoji representations
- Counselor response generation based on detected emotions

### 4. **Speech Recognition & Synthesis**
- Voice input using Web Speech API
- Text-to-speech output for AI responses
- Fluid conversation mode for hands-free interaction
- Speech transcript management and export
- Mobile-optimized speech controls

### 5. **Assessment System**
- Dialog-based mental health assessments
- Dynamic question retrieval from vector database
- Progress tracking and state management
- Assessment completion with recommendations
- Problem category detection and suggestions

### 6. **Multi-language Support**
- Dynamic language switching (English/Indonesian)
- Intelligent translation based on user preferences
- Localized UI components and messages
- Language-aware response generation

### 7. **Data Management**
- Chat history export functionality
- Data deletion requests
- Session management with unique identifiers
- Local storage integration for persistence

## Backend Services & Integrations

### 1. **Chat Service (WebSocket Streaming)**

**Endpoint:** WebSocket connection to streaming chat service  
**Configuration:** `config.public.customChatWsUrl`  
**Purpose:** Real-time bidirectional communication for chat messages

**Features:**
- Streaming response chunks for real-time typing effect
- Session data transmission including user preferences
- Semantic context integration
- Assessment progress tracking
- Error handling and connection management

**Message Format:**
```javascript
{
  message: string,
  session_data: {
    sessionId: string,
    conversationId: string,
    preferredLanguage: string,
    mode: string,
    emotion: object
  },
  semantic_context: array,
  problem_category: string,
  assessment_progress: object
}
```

### 2. **Vector Search Service**

**Base Endpoint:** `${config.public.customChatApiUrl}/vector/search`  
**Purpose:** Semantic search and context retrieval for mental health content

#### 2.1 Mental Health Context Search
**Function:** `searchMentalHealthContext(query)`  
**Collection:** "mental-health-problems"  
**Purpose:** Retrieve relevant mental health information based on user queries

#### 2.2 Problem Categories Retrieval
**Function:** `getProblemCategories()`  
**Collection:** "mental-health-problems"  
**Query:** "mental health problems categories"  
**Purpose:** Fetch available mental health problem categories

#### 2.3 Assessment Questions Retrieval
**Function:** `getAssessmentQuestions(problemCategory)`  
**Collection:** "mental-health-assessments"  
**Purpose:** Get assessment questions for specific problem categories

#### 2.4 Therapeutic Suggestions
**Function:** `getTherapeuticSuggestions(problemCategory)`  
**Collection:** "mental-health-suggestions"  
**Purpose:** Retrieve therapeutic suggestions for specific problem categories

### 3. **Assessment Service**

**Base Endpoint:** `${config.public.customChatApiUrl}/assessment`  
**Authentication:** Bearer token (auth_token or customChatApiKey)

#### 3.1 Start Assessment
**Endpoint:** `POST /assessment/start`  
**Purpose:** Initialize a new mental health assessment session

**Request Body:**
```javascript
{
  problem_category: string,
  sub_category_id?: string,
  session_data: object
}
```

#### 3.2 Continue Assessment
**Endpoint:** `POST /assessment/respond`  
**Purpose:** Submit assessment responses and get next questions

**Request Body:**
```javascript
{
  response: string,
  question_id: string
}
```

#### 3.3 Assessment Status
**Endpoint:** `GET /assessment/status`  
**Purpose:** Check current assessment state and progress

#### 3.4 Cancel Assessment
**Endpoint:** `POST /assessment/cancel`  
**Purpose:** Terminate active assessment session

### 4. **Conversation Management Service**

**Base Endpoint:** `${config.public.customChatApiUrl}/conversation`  
**Authentication:** Bearer token required

#### 4.1 Conversation History
**Endpoint:** `GET /conversation/history`  
**Purpose:** Retrieve user's conversation history

#### 4.2 Clear History
**Endpoint:** `DELETE /conversation/clear`  
**Purpose:** Delete user's conversation history

### 5. **Model Management Service**

**Base Endpoint:** `${config.public.customChatApiUrl}/model`  
**Purpose:** AI model status and management

#### 5.1 Model Status
**Endpoint:** `GET /model/status`  
**Purpose:** Check AI model availability and status

#### 5.2 Pull Model
**Endpoint:** `POST /model/pull`  
**Purpose:** Download or update AI model

## Technical Architecture

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

### Key Dependencies

- **Vue 3:** Core framework with Composition API
- **Nuxt 3:** Full-stack framework with SSR capabilities
- **WebSocket API:** Real-time communication
- **Web Speech API:** Voice recognition and synthesis
- **Markdown Processing:** Rich text rendering
- **i18n:** Internationalization support

### State Management

**Reactive References:**
- `messages`: Chat message history
- `isStreaming`: Streaming status indicator
- `assessmentProgress`: Assessment state tracking
- `currentProblemCategory`: Active problem category
- `sessionId` & `conversationId`: Session identifiers
- `detectedProblemCategory`: AI-detected problem category
- `shouldShowAssessmentSuggestion`: Assessment suggestion flag

### Configuration

**Environment Variables:**
- `config.public.customChatApiUrl`: REST API base URL
- `config.public.customChatWsUrl`: WebSocket endpoint URL
- `config.public.customChatApiKey`: API authentication key

## Security Considerations

1. **Authentication:** Bearer token-based authentication for protected endpoints
2. **Session Management:** Unique session identifiers for user isolation
3. **Data Privacy:** Local storage for sensitive data with deletion capabilities
4. **Error Handling:** Comprehensive error catching and user feedback
5. **Input Validation:** Client-side validation for user inputs

## Performance Optimizations

1. **Streaming Responses:** Real-time chunk processing for better UX
2. **WebSocket Reuse:** Connection pooling and management
3. **Lazy Loading:** On-demand component and data loading
4. **Debounced Inputs:** Optimized user input handling
5. **Memory Management:** Proper cleanup of WebSocket connections

## Mobile Responsiveness

- Touch-optimized controls for speech functionality
- Responsive design for various screen sizes
- Mobile-specific UI adaptations
- Gesture support for common actions

## Accessibility Features

- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Voice interaction capabilities
- Clear visual feedback for all actions

This chatbot application represents a comprehensive mental health support system that combines modern web technologies with AI-powered conversational capabilities, providing users with accessible, intelligent, and empathetic mental health assistance.