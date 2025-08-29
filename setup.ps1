# Mental Health Chat Application Setup Script (PowerShell)
Write-Host "🚀 Setting up Mental Health Chat Application..." -ForegroundColor Green

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Create .env file from template if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "backend\env.local" "backend\.env"
    Write-Host "✅ .env file created. Please review and update if needed." -ForegroundColor Green
}

# Start Docker services
Write-Host "🐳 Starting Docker services (MongoDB, Redis, Qdrant)..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow

# Check MongoDB
$mongodbStatus = docker-compose ps mongodb
if ($mongodbStatus -match "Up") {
    Write-Host "✅ MongoDB is running" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB failed to start" -ForegroundColor Red
}

# Check Redis
$redisStatus = docker-compose ps redis
if ($redisStatus -match "Up") {
    Write-Host "✅ Redis is running" -ForegroundColor Green
} else {
    Write-Host "❌ Redis failed to start" -ForegroundColor Red
}

# Check Qdrant
$qdrantStatus = docker-compose ps qdrant
if ($qdrantStatus -match "Up") {
    Write-Host "✅ Qdrant is running" -ForegroundColor Green
} else {
    Write-Host "❌ Qdrant failed to start" -ForegroundColor Red
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
Set-Location ..

# Check if Ollama is installed and running
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "✅ Ollama is installed" -ForegroundColor Green

    # Check if gemma3:12 model is available
    $ollamaList = ollama list
    if ($ollamaList -match "gemma3:12") {
        Write-Host "✅ Gemma3:12 model is available" -ForegroundColor Green
    } else {
        Write-Host "📥 Pulling Gemma3:12 model..." -ForegroundColor Yellow
        ollama pull gemma3:12
    }
} else {
    Write-Host "⚠️  Ollama is not installed. Please install Ollama and pull the gemma3:12 model." -ForegroundColor Yellow
    Write-Host "   Visit: https://ollama.ai/download" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Start the backend: cd backend; python main.py" -ForegroundColor White
Write-Host "2. Start the frontend: npm run dev" -ForegroundColor White
Write-Host "3. Access the application at: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Services:" -ForegroundColor Cyan
Write-Host "- MongoDB: localhost:27017" -ForegroundColor White
Write-Host "- Redis: localhost:6379" -ForegroundColor White
Write-Host "- Qdrant: localhost:6333" -ForegroundColor White
Write-Host "- Backend API: localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "📚 Useful commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "- Stop services: docker-compose down" -ForegroundColor White
Write-Host "- Restart services: docker-compose restart" -ForegroundColor White
