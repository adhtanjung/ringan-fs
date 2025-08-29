# Mental Health Chat App - Testing Guide

This guide provides comprehensive testing instructions for the AI-powered mental health chat application based on the requirements outlined in `PRD_Chat.md`.

## 📋 Test Coverage Overview

Our testing suite validates all core features from the PRD:

### 🎯 Core Features Tested

1. **Chat Consultation (PRD 3.1.1-3.1.2)**
   - Onboarding and initial interaction
   - AI-powered natural language understanding
   - Sentiment analysis and emotional state detection

2. **Structured Assessment Flow (PRD 3.1.3)**
   - Sequential question progression using `next_step` logic
   - Response type handling (scale, text, multiple choice)
   - Assessment completion and result generation

3. **Suggestion and Intervention Delivery (PRD 3.1.4)**
   - Contextual suggestion matching by `sub_category_id` and `cluster`
   - Resource link provision
   - Therapeutic intervention recommendations

4. **Feedback and Iteration (PRD 3.1.5)**
   - User feedback collection on suggestions
   - Next action determination based on feedback
   - Continuous improvement loop

5. **WebSocket Streaming**
   - Real-time message streaming
   - Progressive response building
   - Connection management

6. **Crisis Detection**
   - Automatic detection of crisis keywords
   - Emergency response protocols
   - Safety escalation procedures

## 🛠️ Available Test Scripts

### 1. Backend Comprehensive Test (`test_mental_health_chat.py`)

**Purpose**: Full backend API and functionality testing

**Features Tested**:
- ✅ Backend health and connectivity
- ✅ Chat session initialization
- ✅ Natural language understanding
- ✅ Assessment flow progression
- ✅ Suggestion delivery system
- ✅ Feedback collection
- ✅ Vector database semantic search
- ✅ Crisis detection algorithms
- ✅ WebSocket streaming functionality

**Usage**:
```bash
# Navigate to project root
cd d:\AITek\ringan-landing

# Run the comprehensive backend test
python test_mental_health_chat.py
```

**Requirements**:
- Backend server running on `http://localhost:8000`
- Python 3.8+ with required dependencies
- WebSocket server active

### 2. Frontend JavaScript Test (`frontend/test_frontend_features.js`)

**Purpose**: Frontend functionality and integration testing

**Features Tested**:
- ✅ WebSocket connection and streaming
- ✅ API endpoint connectivity
- ✅ Chat interface elements
- ✅ Assessment UI components
- ✅ Crisis detection integration

**Usage**:
```javascript
// In browser console or Node.js
const tester = new FrontendTester();
await tester.runAllTests();

// Or use convenience function
runFrontendTests();
```

### 3. Visual Test Runner (`frontend/test_runner.html`)

**Purpose**: Interactive browser-based testing with visual feedback

**Features**:
- 🎨 Beautiful, intuitive test interface
- 📊 Real-time progress tracking
- 📈 Visual test result summaries
- 📋 Detailed test reports
- 💾 Export functionality for test results

**Usage**:
1. Open `frontend/test_runner.html` in your browser
2. Click "Run All Tests" or run individual test suites
3. View real-time results and progress
4. Export reports for documentation

## 🚀 Quick Start Testing

### Prerequisites

1. **Start Backend Server**:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend Server**:
   ```bash
   cd frontend
   npm run dev
   ```

### Running Tests

#### Option 1: Visual Testing (Recommended)
1. Open `http://localhost:3000` in your browser
2. Navigate to `frontend/test_runner.html`
3. Click "Run All Tests"
4. Monitor progress and results in real-time

#### Option 2: Command Line Testing
```bash
# Run comprehensive backend tests
python test_mental_health_chat.py

# View generated report
cat test_report.txt
```

#### Option 3: Browser Console Testing
1. Open browser developer tools
2. Navigate to the chatbot page
3. Load the test script:
   ```javascript
   // Load test script
   const script = document.createElement('script');
   script.src = '/test_frontend_features.js';
   document.head.appendChild(script);
   
   // Run tests after loading
   setTimeout(() => runFrontendTests(), 1000);
   ```

## 📊 Understanding Test Results

### Test Status Indicators

- **✅ PASS**: Test completed successfully
- **❌ FAIL**: Test failed - requires attention
- **⚠️ WARN**: Test completed with warnings
- **⏭️ SKIP**: Test skipped (not applicable)

### Key Metrics

- **Success Rate**: Percentage of tests that passed
- **Response Time**: API and WebSocket response times
- **Coverage**: Features tested vs. total features
- **Reliability**: Consistency across multiple test runs

## 🔍 Detailed Test Scenarios

### Chat Consultation Tests

```python
# Example test messages for natural language understanding
test_messages = [
    "I've been feeling really stressed lately",
    "I can't sleep and I'm always worried about everything",
    "My heart races when I have to speak in public",
    "I feel overwhelmed with work and life",
    "I can't stop thinking about a traumatic event"
]
```

### Assessment Flow Tests

```python
# Test assessment progression
1. Start assessment for specific category (stress, anxiety, trauma)
2. Answer questions sequentially
3. Validate next_step logic
4. Confirm assessment completion
5. Verify result generation
```

### Crisis Detection Tests

```python
# Crisis keywords tested
crisis_keywords = [
    "bunuh diri", "mengakhiri hidup", "tidak ingin hidup",
    "suicide", "kill myself", "end it all"
]
```

### WebSocket Streaming Tests

```javascript
// Test streaming message flow
1. Establish WebSocket connection
2. Send chat message
3. Receive streaming chunks
4. Validate message completion
5. Test connection cleanup
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Not Running**
   - Error: Connection refused
   - Solution: Start backend with `uvicorn main:app --reload`

2. **WebSocket Connection Failed**
   - Error: WebSocket connection timeout
   - Solution: Verify WebSocket endpoint and firewall settings

3. **Database Connection Issues**
   - Error: MongoDB/Vector DB connection failed
   - Solution: Check database configuration and connectivity

4. **Missing Dependencies**
   - Error: Module not found
   - Solution: Install requirements with `pip install -r requirements.txt`

### Debug Mode

Enable verbose logging for detailed debugging:

```python
# In test scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

- **API Response Time**: < 500ms
- **WebSocket Connection**: < 100ms
- **Message Streaming**: < 50ms per chunk
- **Assessment Question Load**: < 200ms
- **Suggestion Retrieval**: < 300ms

### Load Testing

For production readiness, consider running load tests:

```bash
# Example load test with multiple concurrent users
python -m pytest test_load.py --users=50 --duration=60s
```

## 📋 Test Checklist

Before deployment, ensure all tests pass:

- [ ] Backend health check
- [ ] Chat initialization
- [ ] Natural language understanding
- [ ] Assessment flow progression
- [ ] Suggestion delivery
- [ ] Feedback collection
- [ ] WebSocket streaming
- [ ] Crisis detection
- [ ] UI element validation
- [ ] API endpoint connectivity
- [ ] Error handling
- [ ] Performance benchmarks

## 📝 Reporting Issues

When reporting test failures, include:

1. **Test Environment**:
   - OS and browser version
   - Backend/frontend versions
   - Database configuration

2. **Error Details**:
   - Full error messages
   - Stack traces
   - Test logs

3. **Reproduction Steps**:
   - Exact steps to reproduce
   - Expected vs. actual behavior
   - Screenshots if applicable

## 🔄 Continuous Integration

For automated testing in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Mental Health Chat Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test_mental_health_chat.py
```

## 📚 Additional Resources

- [PRD_Chat.md](./PRD_Chat.md) - Product Requirements Document
- [API Documentation](./backend/README.md) - Backend API reference
- [Frontend Guide](./frontend/README.md) - Frontend development guide
- [Deployment Guide](./SETUP_README.md) - Production deployment instructions

---

**Note**: This testing suite is designed to validate compliance with the Mental Health Chat App PRD. Regular testing ensures the application meets all specified requirements and maintains high quality standards.