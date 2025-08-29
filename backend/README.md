# Mental Health Chat Backend

A Python FastAPI backend for the AI-powered mental health chat application using Ollama.

## Features

- **Ollama Integration**: Local AI model inference using Ollama
- **Real-time Chat**: WebSocket support for real-time conversations
- **Sentiment Analysis**: Emotion and crisis detection
- **Structured Assessment**: Mental health assessment flows
- **Crisis Detection**: Automatic detection of crisis situations
- **Streaming Responses**: Real-time streaming AI responses
- **Authentication**: JWT-based authentication system
- **Database Support**: MongoDB and Redis integration

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- MongoDB (optional, for production)
- Redis (optional, for caching)

## Installation

1. **Clone the repository**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Install and start Ollama**
   ```bash
   # Install Ollama (https://ollama.ai)
   ollama pull llama2  # or your preferred model
   ollama serve
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

- **OLLAMA_BASE_URL**: Ollama server URL (default: http://localhost:11434)
- **OLLAMA_MODEL**: Model name to use (default: llama2)
- **SECRET_KEY**: JWT secret key
- **Database URLs**: MongoDB and Redis connection strings

### Ollama Models

The backend is configured to use `llama2` by default. You can change this in the `.env` file:

```env
OLLAMA_MODEL=llama2
```

Available models you can use:

- `llama2` - General purpose
- `llama2:7b` - Smaller, faster
- `llama2:13b` - Larger, more capable
- `mistral` - Good performance/size ratio
- `codellama` - Code-focused

## Running the Backend

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/chat` - Send message and get response
- `POST /api/v1/chat/chat/stream` - Streaming chat response
- `POST /api/v1/chat/assessment/start` - Start structured assessment
- `GET /api/v1/chat/conversation/history` - Get conversation history
- `DELETE /api/v1/chat/conversation/clear` - Clear conversation history

### Model Management

- `GET /api/v1/chat/model/status` - Check Ollama model status
- `POST /api/v1/chat/model/pull` - Pull Ollama model

### WebSocket

- `WS /api/v1/chat/ws/{client_id}` - Real-time chat WebSocket

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples

### Basic Chat Request

```python
import requests

response = requests.post("http://localhost:8000/api/v1/chat/chat", json={
    "message": "Saya merasa sedih hari ini",
    "session_data": {
        "user_context": "User sedang mengalami kesedihan"
    }
})

print(response.json())
```

### Streaming Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat/chat/stream",
    json={"message": "Halo, bagaimana kabarmu?"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### WebSocket Chat

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws/client123");

ws.onmessage = function (event) {
	const data = JSON.parse(event.data);
	console.log("Received:", data);
};

ws.send(
	JSON.stringify({
		message: "Halo, saya butuh bantuan",
		session_data: {},
	})
);
```

## Mental Health Features

### Crisis Detection

The system automatically detects crisis keywords and provides appropriate responses with emergency contact information.

### Sentiment Analysis

Every message is analyzed for:

- Sentiment (positive/negative/neutral)
- Emotion (sad/anxious/angry/happy/stressed)
- Crisis risk level

### Structured Assessment

Supports structured mental health assessments based on problem categories.

## Development

### Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── chat.py
│   │       │   ├── auth.py
│   │       │   └── users.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── websocket.py
│   └── services/
│       ├── chat_service.py
│       └── ollama_service.py
├── main.py
├── requirements.txt
└── README.md
```

### Adding New Features

1. **New Service**: Add to `app/services/`
2. **New Endpoint**: Add to `app/api/v1/endpoints/`
3. **New Model**: Add to appropriate endpoint file
4. **Configuration**: Add to `app/core/config.py`

## Troubleshooting

### Ollama Connection Issues

1. Ensure Ollama is running: `ollama serve`
2. Check model availability: `ollama list`
3. Pull required model: `ollama pull llama2`

### Database Connection Issues

1. Check MongoDB/Redis are running
2. Verify connection strings in `.env`
3. Check network connectivity

### Performance Issues

1. Use smaller models for faster responses
2. Adjust `OLLAMA_MAX_TOKENS` in `.env`
3. Enable Redis caching for better performance

## Security

- JWT-based authentication
- Input validation and sanitization
- Rate limiting (implement as needed)
- CORS configuration for frontend

## License

This project is part of the Mental Health Chat application.


