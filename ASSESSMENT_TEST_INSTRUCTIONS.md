# Assessment Functionality Test Instructions

## How to Test the Assessment Feature

### Step 1: Open the Chatbot
1. Navigate to: http://localhost:3001/application/chatbot
2. Make sure both frontend (port 3001) and backend (port 8000) are running

### Step 2: Trigger Assessment Flow
Send one of these messages to trigger the assessment:

**Option A - Direct stress message:**
```
I'm feeling very stressed and anxious about work. I can't sleep and feel overwhelmed. I think I need help.
```

**Option B - Assessment request:**
```
I would like to take a stress assessment to understand my mental health better.
```

**Option C - Problem description:**
```
I've been having trouble sleeping and feeling anxious lately. Can you help me assess my stress levels?
```

### Step 3: Look for Assessment Suggestion
After sending the message, the system should:
1. Analyze your message
2. Suggest taking an assessment
3. Show a message like "Would you like to take a brief assessment?"

### Step 4: Accept Assessment
Respond with:
```
Yes, I would like to take the assessment.
```

### Step 5: Check for Assessment UI
Once the assessment starts, you should see:
1. **Debug information** showing `response_type = scale` or `response_type = text`
2. **Assessment question** with clear text
3. **Scale UI** (1-10 buttons) if response_type is "scale"
4. **Text input** if response_type is "text"

### Step 6: Debug Information
Look for the debug box that shows:
```
Debug: response_type = scale
Question structure: { ... }
```

### Expected Behavior
- If `response_type = "scale"`: You should see 10 numbered buttons (1-10)
- If `response_type = "text"`: You should see a text input area
- If `response_type = undefined`: There's a data structure issue

### Troubleshooting
1. **No assessment suggestion**: Try a more explicit stress-related message
2. **No scale UI**: Check the debug info for `response_type` value
3. **WebSocket errors**: Check browser console (F12) for connection issues
4. **Backend errors**: Check the backend terminal for error messages

### WebSocket Test Alternative
If the main interface doesn't work, use:
http://localhost:3001/test_assessment_websocket.html

1. Click "Connect WebSocket"
2. Click "Send Stress Message"
3. Click "Trigger Assessment"
4. Check the logs for assessment_data structure

### Key Data Structure to Look For
```json
{
  "type": "complete",
  "assessment_data": {
    "type": "assessment_question",
    "question": {
      "question_id": "...",
      "question_text": "...",
      "response_type": "scale",  // This should be "scale" for 1-10 UI
      "sub_category_id": "..."
    },
    "progress": {
      "current_step": 1,
      "completed_questions": 0,
      "total_estimated": 10
    }
  }
}
```

The key field is `assessment_data.question.response_type` - this determines which UI component is shown.