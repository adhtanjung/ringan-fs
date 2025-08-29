# Project Separation Guide: Frontend + Python Backend with Ollama

## Overview

This guide explains how to separate your current Nuxt.js application into a frontend and Python backend, with Ollama replacing the current chat system.

## Project Structure

```
ringan-landing/
├── frontend/                    # Your existing Nuxt.js app
│   ├── app.vue
│   ├── components/
│   ├── composables/
│   │   ├── useOllamaChat.ts    # NEW: Ollama chat composable
│   │   └── ... (existing)
│   ├── pages/
│   ├── nuxt.config.ts          # Updated for Python backend
│   └── ...
├── backend/                     # NEW: Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── chat.py
│   │   │       │   ├── auth.py
│   │   │       │   └── users.py
│   │   │       └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   └── websocket.py
│   │   └── services/
│   │       ├── chat_service.py
│   │       └── ollama_service.py
│   ├── main.py
│   ├── requirements.txt
│   ├── env.example
│   └── README.md
└── README.md
```

## Backend Setup (Python + Ollama)

### 1. Install Ollama

```bash
# Download and install Ollama from https://ollama.ai
# Then pull a model:
ollama pull llama2
ollama serve
```

### 2. Set up Python Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your configuration
# Most importantly:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama2
```

### 3. Start the Backend

```bash
# Development mode
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Backend is Running

- Visit: http://localhost:8000/docs (Swagger UI)
- Visit: http://localhost:8000/health (Health check)

## Frontend Updates

### 1. Update Configuration

The `nuxt.config.ts` has been updated to point to the Python backend:

```typescript
// Python Backend Configuration (Ollama)
customChatApiUrl: 'http://localhost:8000/api/v1/chat',
customChatWsUrl: 'ws://localhost:8000/api/v1/chat/ws/{client_id}',
```

### 2. New Ollama Chat Composable

The new `useOllamaChat.ts` composable provides:

- **sendMessage()**: Send message and get response
- **sendMessageStream()**: Streaming responses
- **connectWebSocket()**: Real-time WebSocket chat
- **startAssessment()**: Start structured assessment
- **checkModelStatus()**: Check Ollama model status

### 3. Update Existing Chat Components

Replace the old chat composables with the new Ollama one:

```typescript
// OLD
import { useOpenAI } from "~/composables/useOpenAI";
import { useCustomChat } from "~/composables/useCustomChat";

// NEW
import { useOllamaChat } from "~/composables/useOllamaChat";

// In your component:
const { sendMessage, sendMessageStream, isProcessing, error } = useOllamaChat();
```

## Migration Steps

### Step 1: Update Chat Pages

Update your chat pages to use the new Ollama composable:

```vue
<script setup>
import { useOllamaChat } from "~/composables/useOllamaChat";

const {
	sendMessage,
	sendMessageStream,
	isProcessing,
	error,
	messages,
	addMessage,
} = useOllamaChat();

const currentMessage = ref("");

const handleSendMessage = async () => {
	if (!currentMessage.value.trim()) return;

	// Add user message
	addMessage({
		text: currentMessage.value,
		sender: "user",
	});

	const messageText = currentMessage.value;
	currentMessage.value = "";

	// Get AI response
	const response = await sendMessage(messageText);

	if (response) {
		addMessage({
			text: response.message,
			sender: "ai",
			sentiment: response.sentiment,
			isCrisis: response.isCrisis,
		});
	}
};
</script>
```

### Step 2: Update Demo Page

Update `pages/demo/index.vue` to use Ollama:

```vue
<script setup>
// Replace existing chat imports
import { useOllamaChat } from "~/composables/useOllamaChat";

const { sendMessage, isProcessing, error, addMessage } = useOllamaChat();

// Update sendMessage function
const sendMessage = async () => {
	if (!currentInput.value.trim() || isTyping.value || isChatLimitReached.value)
		return;

	const userMessage = currentInput.value.trim();
	addMessage({
		text: userMessage,
		sender: "user",
	});

	currentInput.value = "";
	showQuickResponses.value = false;
	chatCount.value++;
	isTyping.value = true;

	try {
		const response = await sendMessage(userMessage);

		if (response) {
			addMessage({
				text: response.message,
				sender: "ai",
				sentiment: response.sentiment,
				isCrisis: response.isCrisis,
			});
		}
	} catch (err) {
		addMessage({
			text: "Maaf, terjadi kesalahan. Silakan coba lagi nanti.",
			sender: "ai",
		});
	} finally {
		isTyping.value = false;

		if (isChatLimitReached.value) {
			showRegistrationCTA.value = true;
			showQuickResponses.value = false;

			setTimeout(() => {
				addMessage({
					text: `Wah, kamu sudah mencoba ${maxChats} percakapan! 🎉 Untuk melanjutkan ngobrol tanpa batas, yuk daftar di aplikasi Ringan. Kamu akan mendapatkan akses penuh ke semua fitur! 💙`,
					sender: "ai",
				});
			}, 1000);
		} else {
			showQuickResponses.value = true;
		}
	}
};
</script>
```

### Step 3: Update Application Chatbot

Update `pages/application/chatbot/index.vue`:

```vue
<script setup>
// Replace existing imports
import { useOllamaChat } from "~/composables/useOllamaChat";

const { sendMessage, sendMessageStream, isProcessing, error, addMessage } =
	useOllamaChat();

// Update sendMessage function
const sendMessage = async () => {
	if (!currentMessage.value.trim() || isSending.value) return;

	const userMessage = {
		text: currentMessage.value.trim(),
		sender: "user",
		timestamp: new Date(),
		emotionTone: detectedEmotion.value,
	};

	// Check for crisis keywords
	if (checkForCrisis(userMessage.text)) {
		showCrisisAlert.value = true;
	}

	addMessage(userMessage);
	const messageText = currentMessage.value;
	const messageEmotion = detectedEmotion.value;
	currentMessage.value = "";
	detectedEmotion.value = null;

	await scrollToBottom();

	isTyping.value = true;
	isSending.value = true;

	try {
		const response = await sendMessage(messageText, {
			emotion: messageEmotion,
			mode: currentMode.value,
		});

		if (response) {
			addMessage({
				text: response.message,
				sender: "ai",
				timestamp: new Date(),
				sentiment: response.sentiment,
				isCrisis: response.isCrisis,
			});
		}
	} catch (error) {
		console.error("Error sending message:", error);
		addMessage({
			text: "Maaf, terjadi kesalahan teknis. Silakan coba lagi. Jika ini adalah situasi darurat, segera hubungi 112.",
			sender: "ai",
			timestamp: new Date(),
		});
	} finally {
		isTyping.value = false;
		isSending.value = false;
		await scrollToBottom();
	}
};
</script>
```

## Environment Variables

### Frontend (.env)

```env
# Python Backend URLs
CUSTOM_CHAT_API_URL=http://localhost:8000/api/v1/chat
CUSTOM_CHAT_WS_URL=ws://localhost:8000/api/v1/chat/ws/{client_id}
CUSTOM_CHAT_API_KEY=your_jwt_token

# Keep existing variables for fallback
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### Backend (.env)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000

# Security
SECRET_KEY=your-secret-key-here

# Database (optional for development)
MONGODB_URL=mongodb://localhost:27017/mental_health_chat
REDIS_URL=redis://localhost:6379
```

## Testing the Integration

### 1. Test Basic Chat

```bash
# Start backend
cd backend
python main.py

# Start frontend
cd frontend
npm run dev

# Visit: http://localhost:3000/demo
```

### 2. Test API Endpoints

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo, bagaimana kabarmu?"}'

# Test model status
curl http://localhost:8000/api/v1/chat/model/status
```

### 3. Test WebSocket

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws/test123");

ws.onmessage = function (event) {
	console.log("Received:", JSON.parse(event.data));
};

ws.send(
	JSON.stringify({
		message: "Halo, saya butuh bantuan",
		session_data: {},
	})
);
```

## Key Features

### 1. Mental Health Focused

- **Crisis Detection**: Automatically detects crisis keywords
- **Sentiment Analysis**: Analyzes user emotions
- **Structured Assessment**: Supports mental health assessments
- **Emergency Contacts**: Provides crisis hotline information

### 2. Real-time Communication

- **WebSocket Support**: Real-time chat
- **Streaming Responses**: Live AI responses
- **Session Management**: Maintains conversation context

### 3. Scalable Architecture

- **Modular Design**: Easy to extend and modify
- **Database Support**: MongoDB and Redis integration
- **Authentication**: JWT-based auth system
- **API Documentation**: Auto-generated Swagger docs

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**

   ```bash
   # Check if Ollama is running
   ollama list

   # Start Ollama
   ollama serve

   # Pull model if needed
   ollama pull llama2
   ```

2. **Backend Won't Start**

   ```bash
   # Check dependencies
   pip install -r requirements.txt

   # Check environment variables
   cp env.example .env
   # Edit .env with correct values
   ```

3. **Frontend Can't Connect**

   ```bash
   # Check backend is running
   curl http://localhost:8000/health

   # Check CORS settings in backend/config.py
   # Ensure frontend URL is in ALLOWED_ORIGINS
   ```

4. **Model Not Available**

   ```bash
   # Check available models
   ollama list

   # Pull the model
   ollama pull llama2

   # Or change model in .env
   OLLAMA_MODEL=mistral
   ```

## Next Steps

1. **Database Integration**: Set up MongoDB for conversation storage
2. **User Authentication**: Implement full auth system
3. **Assessment System**: Integrate with your mental health datasets
4. **Vector Database**: Add Pinecone for semantic search
5. **Production Deployment**: Deploy to production servers

## Benefits of This Architecture

1. **Local AI**: No API costs, full control over models
2. **Privacy**: All data stays on your servers
3. **Customization**: Easy to fine-tune models for mental health
4. **Scalability**: Can handle multiple users and conversations
5. **Real-time**: WebSocket support for live chat
6. **Mental Health Focus**: Built specifically for mental health support


