# Mental Health Chat Application - Setup Guide

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
3. **Node.js 16+** - [Download here](https://nodejs.org/)
4. **Ollama** - [Download here](https://ollama.ai/download)

### Automated Setup (Recommended)

#### Windows (PowerShell)

```powershell
# Run the setup script
.\setup.ps1
```

#### Linux/Mac (Bash)

```bash
# Make script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Manual Setup

#### 1. Start Database Services

```bash
# Start MongoDB, Redis, and Qdrant
docker-compose up -d
```

#### 2. Create Environment File

```bash
# Copy the environment template
cp backend/env.local backend/.env

# Edit the file if needed
# nano backend/.env
```

#### 3. Install Dependencies

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
npm install
```

#### 4. Install Ollama and Model

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the required model
ollama pull gemma3:12
```

#### 5. Start the Application

```bash
# Start the backend (Terminal 1)
cd backend
python main.py

# Start the frontend (Terminal 2)
npm run dev
```

## 🔧 Services

| Service     | URL                   | Description                |
| ----------- | --------------------- | -------------------------- |
| Frontend    | http://localhost:3000 | Nuxt.js application        |
| Backend API | http://localhost:8000 | FastAPI backend            |
| MongoDB     | localhost:27017       | Database for conversations |
| Redis       | localhost:6379        | Caching and sessions       |
| Qdrant      | localhost:6333        | Vector database            |

## 📊 Database Credentials

### MongoDB

- **Username**: admin
- **Password**: password123
- **Database**: mental_health_chat
- **Connection String**: `mongodb://admin:password123@localhost:27017/mental_health_chat?authSource=admin`

### Redis

- **No authentication** (development mode)
- **Connection String**: `redis://localhost:6379`

### Qdrant

- **No authentication** (development mode)
- **URL**: `http://localhost:6333`

## 🧪 Test Data

The setup includes test data:

### Test User

- **Email**: test@example.com
- **Password**: password123

### Excel Datasets

The following datasets are available in `backend/data/`:

- `stress.xlsx` - Stress-related mental health data
- `anxiety.xlsx` - Anxiety-related mental health data
- `trauma.xlsx` - Trauma-related mental health data
- `mentalhealthdata.xlsx` - General mental health data

## 🔍 Verification

### Check Services

```bash
# Check if all services are running
docker-compose ps

# View service logs
docker-compose logs -f
```

### Test Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test data import endpoint
curl http://localhost:8000/api/v1/data/status
```

### Test Frontend

1. Open http://localhost:3000 in your browser
2. Navigate to the chat interface
3. Test the conversation flow

## 🛠️ Development Commands

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Remove all data (WARNING: This will delete all data)
docker-compose down -v
```

### Backend Commands

```bash
# Start backend
cd backend
python main.py

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

### Frontend Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## 🔐 Environment Variables

Key environment variables in `backend/.env`:

```env
# Database URLs
MONGODB_URL=mongodb://admin:password123@localhost:27017/mental_health_chat?authSource=admin
REDIS_URL=redis://localhost:6379

# Vector Database
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=all-MiniLM-L6-v2

# AI Model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill the process or change the port in docker-compose.yml
```

#### 2. Docker Services Not Starting

```bash
# Check Docker is running
docker --version
docker-compose --version

# Check service logs
docker-compose logs [service_name]
```

#### 3. Python Dependencies Issues

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies with verbose output
pip install -r requirements.txt -v
```

#### 4. Ollama Model Issues

```bash
# Check if Ollama is running
ollama list

# Pull the model again
ollama pull gemma3:12

# Check model status
ollama show gemma3:12
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
./setup.sh  # or .\setup.ps1 on Windows
```

## 📚 Next Steps

After successful setup:

1. **Import Excel Data**: Use the data import API to vectorize your mental health datasets
2. **Test Chat Interface**: Try the conversation flow with the AI
3. **Customize Responses**: Modify the Ollama prompts for better mental health support
4. **Add Authentication**: Implement user registration and login
5. **Deploy**: Set up production environment

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the service logs: `docker-compose logs -f`
3. Verify all prerequisites are installed
4. Check the TODO list for current development status

## 📝 Notes

- This setup is for development only
- Change default passwords for production
- The SECRET_KEY should be changed in production
- Consider using environment-specific configurations
