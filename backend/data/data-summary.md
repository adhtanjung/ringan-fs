# Mental Health Data Summary

## Overview
This project contains a comprehensive mental health coaching system with data across 4 main categories:
- **Stress** (stress.xlsx)
- **Anxiety** (anxiety.xlsx) 
- **Trauma** (trauma.xlsx)
- **General Mental Health** (mentalhealthdata.xlsx)

## Data Structure

Each Excel file follows a consistent structure with 6 main sheets:

### 1. Problems Sheet (1.1 Problems)
- **Purpose**: Defines mental health problem categories and subcategories
- **Key Fields**: category, category_id, sub_category_id, problem_name, description
- **Sample Categories**:
  - Stress: Relationship stress, family stress, workplace stress, emotional dysregulation
  - Anxiety: Social anxiety, test anxiety, panic attacks, generalized anxiety
  - Trauma: Adjustment disorder, acute trauma, PTSD, complex trauma, childhood trauma

### 2. Self Assessment Sheet (1.2 Self Assessment)
- **Purpose**: Contains assessment questions for each problem subcategory
- **Key Fields**: question_id, sub_category_id, batch_id, question_text, response_type, next_step, clusters
- **Question Types**: Scale (0-4) and text responses
- **Total Questions**: ~168-240 questions per category

### 3. Suggestions Sheet (1.3 Suggestions)
- **Purpose**: Therapeutic suggestions and interventions for each problem cluster
- **Key Fields**: suggestion_id, sub_category_id, cluster, suggestion_text, resource_link
- **Content**: Evidence-based therapeutic techniques (CBT, ACT, Gottman Method, etc.)
- **Total Suggestions**: ~139-150 per category

### 4. Feedback Prompts Sheet (1.4 Feedback Prompts)
- **Purpose**: Follow-up questions to assess intervention effectiveness
- **Key Fields**: prompt_id, stage, prompt_text, next_action
- **Stages**: post_suggestion, ongoing

### 5. Next Action Sheet (1.5 Next Action After Feedback)
- **Purpose**: Defines possible next steps based on user feedback
- **Actions**: continue_same, show_problem_menu, end_session, escalate, schedule_followup

### 6. Fine-Tuning Examples Sheet (1.6 FineTuning Examples)
- **Purpose**: Training data for AI model fine-tuning
- **Key Fields**: id, problem, ConversationID, prompt, completion
- **Content**: Example conversations and responses for training purposes
- **Total Examples**: ~600-650 prompt-completion pairs per category

## Key Statistics

| Category | Problems | Assessment Questions | Suggestions | Training Examples |
|----------|----------|---------------------|-------------|-------------------|
| Stress | 7 | 168 | 139 | 602 |
| Anxiety | 8 | 240 | ~200 | ~600 |
| Trauma | 7 | 212 | 150 | ~600 |
| Mental Health | ~10 | 105 | 50 | 602 |

## Data Quality Notes

1. **Consistent Structure**: All files follow the same 6-sheet structure
2. **Rich Content**: Detailed therapeutic suggestions with evidence-based references
3. **Hierarchical Organization**: Problems → Subcategories → Clusters → Specific interventions
4. **Assessment Flow**: Structured question sequences with branching logic
5. **Training Ready**: Extensive prompt-completion pairs for AI model training

## Technical Implementation

- **File Format**: Excel (.xlsx) with multiple sheets
- **Data Types**: Primarily text with some numeric scales and IDs
- **Relationships**: Linked by category_id, sub_category_id, and cluster identifiers
- **Scalability**: Modular structure allows easy addition of new categories

## Use Cases

1. **Mental Health Assessment**: Structured questionnaires for problem identification
2. **Intervention Delivery**: Evidence-based therapeutic suggestions
3. **Progress Tracking**: Feedback collection and next-step determination
4. **AI Training**: Large dataset for conversational AI fine-tuning
5. **Clinical Decision Support**: Systematic approach to mental health coaching

This data represents a comprehensive digital mental health platform with structured assessment, intervention, and follow-up capabilities across major mental health domains.