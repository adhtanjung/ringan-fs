# Import/Export System Documentation

## Overview

The Import/Export system provides comprehensive functionality for managing mental health datasets through file-based operations. It supports importing data from CSV, Excel, and JSON files, exporting data in multiple formats, and generating templates for easy data preparation.

## Features

### ✅ Import Functionality
- **File Formats**: CSV, Excel (.xlsx, .xls), JSON
- **Data Types**: All 6 dataset types (problems, assessments, suggestions, feedback_prompts, next_actions, training_examples)
- **Validation**: Comprehensive data validation with detailed error reporting
- **Options**: Overwrite existing data, validate before import
- **Progress Tracking**: Real-time upload progress with visual feedback

### ✅ Export Functionality
- **File Formats**: CSV, Excel (.xlsx), JSON
- **Filtering**: Export by domain, active status, and custom filters
- **Batch Operations**: Export all data or filtered subsets
- **Automatic Naming**: Timestamped filenames for easy organization

### ✅ Template Generation
- **Smart Templates**: Pre-filled with sample data and field descriptions
- **Multiple Formats**: CSV, Excel (with instructions sheet), JSON
- **Field Instructions**: Detailed descriptions for each field
- **Validation Rules**: Built-in validation examples

## Backend Implementation

### Services

#### ImportExportService (`backend/app/services/import_export_service.py`)
- **Template Generation**: Creates sample templates for each data type
- **File Processing**: Handles CSV, Excel, and JSON file parsing
- **Data Validation**: Integrates with validation service
- **Export Processing**: Formats data for different output formats

#### DatasetManagementService (Enhanced)
- **Bulk Operations**: Enhanced bulk create with overwrite support
- **Data Retrieval**: New `get_all_data()` method with filtering
- **Vector Sync**: Automatic synchronization to vector database

#### DatasetValidationService (Enhanced)
- **Bulk Validation**: New `validate_bulk_data()` method
- **Comprehensive Rules**: Field validation, foreign key checks, business logic

### API Endpoints

#### Template Generation
```http
GET /api/v1/admin/import-export/template/{data_type}?format={format}
```
- **Parameters**:
  - `data_type`: problems, assessments, suggestions, feedback_prompts, next_actions, training_examples
  - `format`: csv, xlsx, json
- **Response**: File download with template

#### Import Data
```http
POST /api/v1/admin/import-export/import/{data_type}
```
- **Body**: Multipart form data with file
- **Parameters**:
  - `overwrite`: boolean (default: false)
  - `validate`: boolean (default: true)
- **Response**: Import result with counts and errors

#### Export Data
```http
GET /api/v1/admin/import-export/export/{data_type}?format={format}&domain={domain}&is_active={boolean}
```
- **Parameters**:
  - `data_type`: Data type to export
  - `format`: csv, xlsx, json
  - `domain`: Filter by domain (optional)
  - `is_active`: Filter by active status (optional)
- **Response**: File download with exported data

#### Metadata
```http
GET /api/v1/admin/import-export/supported-types
GET /api/v1/admin/import-export/field-schema/{data_type}
```

## Frontend Implementation

### Components

#### ImportModal (`frontend/components/admin/ImportModal.vue`)
- **File Upload**: Drag & drop and file picker
- **Template Download**: Direct template download integration
- **Progress Tracking**: Real-time upload progress
- **Error Handling**: Comprehensive error display
- **Validation**: Client-side validation with server feedback

#### ExportModal (`frontend/components/admin/ExportModal.vue`)
- **Format Selection**: Visual format picker with descriptions
- **Filtering Options**: Domain and status filters
- **Preview**: Export preview with selected options
- **Template Download**: Template generation for selected data type
- **Batch Export**: Export all data or filtered subsets

### Integration

#### Admin Interface (`frontend/pages/admin/index.vue`)
- **Import Button**: Opens import modal with file upload
- **Export Button**: Opens export modal with filtering options
- **Template Access**: Quick template download from import modal
- **Success Handling**: Automatic data refresh after import

## Data Types and Schemas

### Problems
```csv
domain,category,category_id,sub_category_id,problem_name,description,severity_level,is_active
anxiety,Social Anxiety,SOC_ANX_001,SOC_ANX_001_001,Fear of Public Speaking,Intense fear when speaking in front of groups,3,true
```

### Assessments
```csv
question_id,sub_category_id,batch_id,question_text,response_type,scale_min,scale_max,scale_label_1,scale_label_2,scale_label_3,scale_label_4,options,next_step,clusters,is_active
ASSESS_001,SOC_ANX_001_001,BATCH_001,How often do you avoid social situations?,scale,1,4,Not at all,A little,Quite a bit,Very much,,If score > 3 show coping strategies,social_anxiety,true
```

**Scale Questions (1-4 System)**:
- All scale questions now use a standardized 1-4 range
- `scale_min` must be 1, `scale_max` must be 4
- `scale_label_1` through `scale_label_4` define the text labels for each scale value
- Default labels: "Not at all", "A little", "Quite a bit", "Very much"
- Labels can be customized for different languages or contexts

### Suggestions
```csv
suggestion_id,sub_category_id,cluster,suggestion_text,resource_link,evidence_base,difficulty_level,estimated_duration,tags,is_active
SUGG_001,SOC_ANX_001_001,breathing_techniques,Practice deep breathing exercises,https://example.com/breathing,CBT,1,5-10 minutes,"[""breathing"", ""anxiety""]",true
```

### Feedback Prompts
```csv
prompt_id,stage,prompt_text,next_action_id,context,is_active
PROMPT_001,post_suggestion,How did the breathing exercise make you feel?,ACTION_001,Follow-up after breathing exercise,true
```

### Next Actions
```csv
action_id,action_type,action_name,description,parameters,conditions,is_active
ACTION_001,continue_same,Continue with current approach,Continue with current therapeutic approach,"{""duration"": ""1 week""}","{""anxiety_level"": ""< 3""}",true
```

### Training Examples
```csv
example_id,domain,problem,conversation_id,user_intent,prompt,completion,context,quality_score,tags,is_active
TRAIN_001,anxiety,Social anxiety in group settings,CONV_001,seeking_help,I get really nervous when I have to speak in meetings,I understand that speaking in meetings can feel overwhelming,User expressing social anxiety,0.9,"[""social_anxiety"", ""workplace""]",true
```

## Usage Examples

### 1. Import New Data

1. **Download Template**:
   ```bash
   curl -o problems_template.csv "http://localhost:8000/api/v1/admin/import-export/template/problems?format=csv"
   ```

2. **Fill Template**: Edit the CSV file with your data

3. **Import Data**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/admin/import-export/import/problems" \
        -F "file=@problems_template.csv" \
        -F "overwrite=false" \
        -F "validate=true"
   ```

### 2. Export Data

```bash
# Export all problems as CSV
curl -o problems_export.csv "http://localhost:8000/api/v1/admin/import-export/export/problems?format=csv"

# Export anxiety problems only
curl -o anxiety_problems.csv "http://localhost:8000/api/v1/admin/import-export/export/problems?format=csv&domain=anxiety"

# Export as Excel with filters
curl -o active_assessments.xlsx "http://localhost:8000/api/v1/admin/import-export/export/assessments?format=xlsx&is_active=true"
```

### 3. Frontend Usage

```vue
<!-- Import Modal -->
<ImportModal
  :is-open="showImportModal"
  @close="closeImportModal"
  @import-success="handleImportSuccess"
/>

<!-- Export Modal -->
<ExportModal
  :is-open="showExportModal"
  @close="closeExportModal"
  @export-success="handleExportSuccess"
/>
```

## Validation Rules

### Field Validation
- **Required Fields**: All data types have required fields that must be present
- **Data Types**: Proper type validation (strings, numbers, booleans, arrays)
- **Format Validation**: ID patterns, URL formats, email formats
- **Length Limits**: Text field length restrictions

### Business Logic Validation
- **Foreign Key Relationships**: References between data types must be valid
- **Duplicate Prevention**: Unique ID validation across collections
- **Enum Values**: Restricted values for specific fields (response_type, stage, etc.)
- **Range Validation**: Numeric ranges for severity levels, quality scores

### Error Reporting
- **Field-Level Errors**: Specific field validation errors
- **Row-Level Errors**: Complete row validation failures
- **Bulk Operation Results**: Summary of successful/failed operations
- **Detailed Messages**: Human-readable error descriptions

## File Format Specifications

### CSV Format
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Headers**: First row contains field names
- **Quotes**: Fields containing commas or quotes are properly escaped
- **Comments**: Template files include instruction comments

### Excel Format
- **Instructions Sheet**: First sheet with field descriptions
- **Data Sheet**: Second sheet with actual data
- **Formatting**: Proper data type formatting
- **Validation**: Built-in Excel validation where applicable

### JSON Format
- **Structure**: Array of objects or structured template
- **Schema**: Includes JSON schema for validation
- **Instructions**: Embedded field instructions
- **Sample Data**: Pre-filled with example data

## Error Handling

### Import Errors
- **File Format Errors**: Invalid file types or corrupted files
- **Validation Errors**: Data that doesn't meet schema requirements
- **Business Logic Errors**: Foreign key violations, duplicate IDs
- **System Errors**: Database connection issues, permission problems

### Export Errors
- **Filter Errors**: Invalid filter parameters
- **Data Access Errors**: Permission or connection issues
- **Format Errors**: Unsupported export formats
- **File Generation Errors**: Memory or disk space issues

### User Experience
- **Progress Indicators**: Real-time progress for long operations
- **Error Messages**: Clear, actionable error descriptions
- **Success Feedback**: Confirmation of successful operations
- **Recovery Options**: Retry mechanisms and partial success handling

## Performance Considerations

### Import Performance
- **Batch Processing**: Large files processed in chunks
- **Memory Management**: Streaming file processing for large datasets
- **Validation Optimization**: Efficient validation with early termination
- **Database Optimization**: Bulk insert operations

### Export Performance
- **Streaming**: Large exports streamed to avoid memory issues
- **Filtering**: Database-level filtering for efficiency
- **Caching**: Template caching for repeated downloads
- **Compression**: Optional compression for large exports

## Security Considerations

### File Upload Security
- **File Type Validation**: Strict file type checking
- **Size Limits**: Maximum file size restrictions
- **Content Scanning**: Basic content validation
- **Path Traversal Protection**: Secure file handling

### Data Security
- **Input Sanitization**: All input data sanitized
- **SQL Injection Prevention**: Parameterized queries
- **Access Control**: Admin-only access to import/export
- **Audit Logging**: Operation logging for security

## Testing

### Test Script
Run the test script to verify functionality:
```bash
cd backend
python test_import_export.py
```

### Test Coverage
- **Template Generation**: All data types and formats
- **Import Operations**: Various file formats and data scenarios
- **Export Operations**: Different filters and formats
- **Validation**: Error cases and edge conditions
- **Integration**: End-to-end workflow testing

## Troubleshooting

### Common Issues

1. **Import Validation Errors**
   - Check field names match template exactly
   - Verify required fields are present
   - Ensure data types are correct

2. **Export File Issues**
   - Check file permissions
   - Verify sufficient disk space
   - Ensure proper MIME type handling

3. **Template Download Problems**
   - Verify data type parameter
   - Check format parameter (csv, xlsx, json)
   - Ensure proper authentication

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.getLogger('app.services.import_export_service').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Bulk Template Download**: Download all templates at once
- **Advanced Filtering**: More complex filter options
- **Scheduled Exports**: Automated export scheduling
- **Data Transformation**: Custom data transformation rules
- **API Integration**: External system integration
- **Audit Trail**: Complete operation history
- **Data Backup**: Automated backup functionality

### Performance Improvements
- **Async Processing**: Background job processing
- **Caching**: Template and metadata caching
- **Compression**: Advanced compression options
- **Parallel Processing**: Multi-threaded operations

This comprehensive import/export system provides a robust foundation for managing mental health datasets with professional-grade features for data validation, error handling, and user experience.








