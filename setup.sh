#!/bin/bash

# Mental Health Chat Application Setup Script
echo "🚀 Setting up Mental Health Chat Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file from template if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/env.local backend/.env
    echo "✅ .env file created. Please review and update if needed."
fi

# Start Docker services
echo "🐳 Starting Docker services (MongoDB, Redis, Qdrant)..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."

# Check MongoDB
if docker-compose ps mongodb | grep -q "Up"; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB failed to start"
fi

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
fi

# Check Qdrant
if docker-compose ps qdrant | grep -q "Up"; then
    echo "✅ Qdrant is running"
else
    echo "❌ Qdrant failed to start"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Check if Ollama is installed and running
echo "🤖 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"

    # Check if gemma3:12 model is available
    if ollama list | grep -q "gemma3:12"; then
        echo "✅ Gemma3:12 model is available"
    else
        echo "📥 Pulling Gemma3:12 model..."
        ollama pull gemma3:12
    fi
else
    echo "⚠️  Ollama is not installed. Please install Ollama and pull the gemma3:12 model."
    echo "   Visit: https://ollama.ai/download"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend: cd backend && python main.py"
echo "2. Start the frontend: npm run dev"
echo "3. Access the application at: http://localhost:3000"
echo ""
echo "🔧 Services:"
echo "- MongoDB: localhost:27017"
echo "- Redis: localhost:6379"
echo "- Qdrant: localhost:6333"
echo "- Backend API: localhost:8000"
echo ""
echo "📚 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Restart services: docker-compose restart"
