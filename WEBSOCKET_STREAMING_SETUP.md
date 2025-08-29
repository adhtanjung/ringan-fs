# WebSocket Streaming Setup Guide

This guide will help you set up and test the WebSocket streaming functionality for the chat application.

## 🔧 Backend Setup

### 1. Start the Backend Server

```bash
cd backend

# Create virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Start Ollama (if not already running)
ollama serve

# Start the backend server
python main.py
```

The backend will be available at:

- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

### 2. Test Backend WebSocket

Run the Python test script:

```bash
cd backend
python test_websocket_streaming.py
```

This will test the WebSocket streaming endpoint directly.

## 🌐 Frontend Setup

### 1. Start the Frontend

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will be available at:

- **Main App**: http://localhost:3000
- **Demo Page**: http://localhost:3000/demo

### 2. Test Frontend WebSocket

Open the test page in your browser:

```
http://localhost:3000/test-websocket.html
```

This will allow you to test the WebSocket connection directly from the browser.

## 🧪 Testing the Demo Page

1. Navigate to http://localhost:3000/demo
2. Enter your name to start the chat
3. Try sending messages to test the streaming functionality

## 🔍 Troubleshooting

### WebSocket Connection Issues

1. **Backend not running**: Make sure the backend is running on localhost:8000
2. **Ollama not running**: Ensure Ollama is running with `ollama serve`
3. **CORS issues**: Check that CORS is properly configured in the backend
4. **Port conflicts**: Ensure ports 8000 (backend) and 3000 (frontend) are available

### Common Error Messages

- **"WebSocket connection failed"**: Backend server is not running
- **"Connection refused"**: Check if the backend is running on the correct port
- **"Model not found"**: Pull the required Ollama model with `ollama pull gemma3:12`

### Debug Steps

1. Check backend logs for any errors
2. Open browser developer tools and check the Console tab
3. Use the test-websocket.html page to isolate WebSocket issues
4. Verify the WebSocket URL in the frontend configuration

## 📁 File Structure

```
backend/
├── main.py                          # Main FastAPI application
├── app/api/v1/endpoints/chat.py     # Chat endpoints including WebSocket
├── app/services/chat_service.py     # Chat service with streaming
├── test_websocket_streaming.py      # WebSocket test script
└── requirements.txt                 # Python dependencies

frontend/
├── nuxt.config.ts                   # Configuration including WebSocket URL
├── composables/
│   ├── useOllamaChat.ts            # Ollama chat composable
│   └── useCustomChat.ts            # Custom chat composable
├── pages/demo/index.vue            # Demo chat page
└── test-websocket.html             # WebSocket test page
```

## 🔄 WebSocket Endpoints

### Backend Endpoints

- **Streaming WebSocket**: `ws://localhost:8000/api/v1/chat/ws/chat/stream`
- **Regular WebSocket**: `ws://localhost:8000/api/v1/chat/ws/{client_id}`
- **HTTP Streaming**: `POST http://localhost:8000/api/v1/chat/chat/stream`

### Message Format

**Request (Client → Server)**:

```json
{
	"message": "Your message here",
	"session_data": {
		"user_name": "User Name",
		"session_id": "unique_session_id"
	}
}
```

**Response (Server → Client)**:

```json
{
	"type": "chunk",
	"content": "Partial response text"
}
```

**Completion Signal**:

```json
{
	"type": "complete",
	"message": "Stream completed"
}
```

## 🚀 Next Steps

1. Test the basic WebSocket connection
2. Verify streaming functionality works
3. Test the demo page at http://localhost:3000/demo
4. Monitor for any errors in both backend and frontend logs

If you encounter any issues, check the troubleshooting section above or refer to the backend and frontend logs for more detailed error information.

