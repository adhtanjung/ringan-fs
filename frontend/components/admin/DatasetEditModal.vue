<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
  >
    <!-- Background overlay -->
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        aria-hidden="true"
        @click="closeModal"
      ></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
            {{ isEditing ? 'Edit' : 'Create' }} {{ dataTypeLabel }}
          </h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md p-1"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveItem" class="space-y-6">
          <!-- Dynamic Form Fields -->
          <div v-for="field in formFields" :key="field.key" class="space-y-2">
            <!-- Text Input -->
            <div v-if="field.type === 'text'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <input
                :id="field.key"
                v-model="formData[field.key]"
                type="text"
                :placeholder="field.placeholder"
                :required="field.required"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <!-- Textarea -->
            <div v-else-if="field.type === 'textarea'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <textarea
                :id="field.key"
                v-model="formData[field.key]"
                :rows="field.rows || 3"
                :placeholder="field.placeholder"
                :required="field.required"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              ></textarea>
            </div>

            <!-- Select Dropdown -->
            <div v-else-if="field.type === 'select'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <select
                :id="field.key"
                v-model="formData[field.key]"
                :required="field.required"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="">{{ field.placeholder || 'Select an option' }}</option>
                <option v-for="option in field.options" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <!-- Multi-select Tags -->
            <div v-else-if="field.type === 'tags'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <div class="mt-1">
                <div class="flex flex-wrap gap-2 mb-2">
                  <span
                    v-for="(tag, index) in formData[field.key] || []"
                    :key="index"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      @click="removeTag(field.key, index)"
                      class="ml-1 inline-flex items-center p-0.5 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-600 focus:outline-none focus:bg-blue-200 focus:text-blue-600"
                    >
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                </div>
                <div class="flex">
                  <input
                    v-model="newTag[field.key]"
                    type="text"
                    :placeholder="field.placeholder"
                    class="flex-1 border-gray-300 rounded-l-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    @keydown.enter.prevent="addTag(field.key)"
                    @keydown.comma.prevent="addTag(field.key)"
                  />
                  <button
                    type="button"
                    @click="addTag(field.key)"
                    class="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 text-sm hover:bg-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- Number Input -->
            <div v-else-if="field.type === 'number'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <input
                :id="field.key"
                v-model.number="formData[field.key]"
                type="number"
                :min="field.min"
                :max="field.max"
                :step="field.step"
                :placeholder="field.placeholder"
                :required="field.required"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <!-- Checkbox -->
            <div v-else-if="field.type === 'checkbox'">
              <div class="flex items-center">
                <input
                  :id="field.key"
                  v-model="formData[field.key]"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label :for="field.key" class="ml-2 block text-sm text-gray-900">
                  {{ field.label }}
                </label>
              </div>
            </div>

            <!-- JSON Editor -->
            <div v-else-if="field.type === 'json'">
              <label :for="field.key" class="block text-sm font-medium text-gray-700">
                {{ field.label }}
                <span v-if="field.required" class="text-red-500">*</span>
              </label>
              <textarea
                :id="field.key"
                v-model="jsonFields[field.key]"
                :rows="field.rows || 4"
                :placeholder="field.placeholder"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono text-xs"
                @blur="validateJson(field.key)"
              ></textarea>
              <p v-if="jsonErrors[field.key]" class="mt-1 text-sm text-red-600">
                {{ jsonErrors[field.key] }}
              </p>
            </div>
          </div>

          <!-- Validation Errors -->
          <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Validation Errors</h3>
                <div class="mt-2 text-sm text-red-700">
                  <ul class="list-disc pl-5 space-y-1">
                    <li v-for="error in validationErrors" :key="error">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              @click="closeModal"
              type="button"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              :disabled="isSaving"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isSaving || validationErrors.length > 0"
            >
              <svg
                v-if="isSaving"
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isSaving ? 'Saving...' : (isEditing ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  dataType: {
    type: String,
    required: true
  },
  item: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// Reactive data
const formData = reactive({})
const jsonFields = reactive({})
const jsonErrors = reactive({})
const newTag = reactive({})
const isSaving = ref(false)
const validationErrors = ref([])

// Computed properties
const isEditing = computed(() => !!props.item)

const dataTypeLabel = computed(() => {
  const labels = {
    problems: 'Problem Category',
    assessments: 'Assessment Question',
    suggestions: 'Therapeutic Suggestion',
    feedback: 'Feedback Prompt',
    next_actions: 'Next Action',
    training: 'Fine-tuning Example'
  }
  return labels[props.dataType] || 'Item'
})

const formFields = computed(() => {
  const fieldConfigs = {
    problems: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., PROB_001' },
      { key: 'category', label: 'Category', type: 'text', required: true, placeholder: 'e.g., Anxiety' },
      { key: 'subcategory', label: 'Subcategory', type: 'text', placeholder: 'e.g., Social Anxiety' },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3 },
      { key: 'severity_levels', label: 'Severity Levels', type: 'tags', placeholder: 'Add severity level' },
      { key: 'related_domains', label: 'Related Domains', type: 'tags', placeholder: 'Add domain' },
      { key: 'keywords', label: 'Keywords', type: 'tags', placeholder: 'Add keyword' },
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ],
    assessments: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., ASSESS_001' },
      { key: 'question_text', label: 'Question Text', type: 'textarea', required: true, rows: 2 },
      { key: 'response_type', label: 'Response Type', type: 'select', required: true, options: [
        { value: 'scale', label: 'Scale (1-10)' },
        { value: 'multiple_choice', label: 'Multiple Choice' },
        { value: 'yes_no', label: 'Yes/No' },
        { value: 'text', label: 'Text Input' }
      ]},
      { key: 'response_options', label: 'Response Options', type: 'json', placeholder: 'JSON array of options', rows: 3 },
      { key: 'category', label: 'Category', type: 'text', required: true },
      { key: 'domain', label: 'Domain', type: 'text', required: true },
      { key: 'weight', label: 'Weight', type: 'number', min: 0, max: 10, step: 0.1 },
      { key: 'is_required', label: 'Required', type: 'checkbox' },
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ],
    suggestions: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., SUGG_001' },
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'content', label: 'Content', type: 'textarea', required: true, rows: 4 },
      { key: 'category', label: 'Category', type: 'text', required: true },
      { key: 'target_problems', label: 'Target Problems', type: 'tags', placeholder: 'Add problem ID' },
      { key: 'severity_range', label: 'Severity Range', type: 'json', placeholder: '{"min": 1, "max": 10}' },
      { key: 'techniques', label: 'Techniques', type: 'tags', placeholder: 'Add technique' },
      { key: 'duration_minutes', label: 'Duration (minutes)', type: 'number', min: 1 },
      { key: 'difficulty_level', label: 'Difficulty Level', type: 'select', options: [
        { value: 'beginner', label: 'Beginner' },
        { value: 'intermediate', label: 'Intermediate' },
        { value: 'advanced', label: 'Advanced' }
      ]},
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ],
    feedback: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., FEED_001' },
      { key: 'prompt_text', label: 'Prompt Text', type: 'textarea', required: true, rows: 3 },
      { key: 'stage', label: 'Stage', type: 'select', required: true, options: [
        { value: 'initial', label: 'Initial Assessment' },
        { value: 'progress', label: 'Progress Check' },
        { value: 'completion', label: 'Completion' },
        { value: 'follow_up', label: 'Follow-up' }
      ]},
      { key: 'trigger_conditions', label: 'Trigger Conditions', type: 'json', placeholder: 'JSON object with conditions' },
      { key: 'expected_responses', label: 'Expected Responses', type: 'tags', placeholder: 'Add expected response' },
      { key: 'follow_up_actions', label: 'Follow-up Actions', type: 'tags', placeholder: 'Add action' },
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ],
    next_actions: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., ACTION_001' },
      { key: 'action_type', label: 'Action Type', type: 'select', required: true, options: [
        { value: 'suggestion', label: 'Provide Suggestion' },
        { value: 'assessment', label: 'Additional Assessment' },
        { value: 'referral', label: 'Professional Referral' },
        { value: 'resource', label: 'Resource Recommendation' },
        { value: 'follow_up', label: 'Schedule Follow-up' }
      ]},
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3 },
      { key: 'trigger_conditions', label: 'Trigger Conditions', type: 'json', placeholder: 'JSON object with conditions' },
      { key: 'priority', label: 'Priority', type: 'number', min: 1, max: 10 },
      { key: 'estimated_duration', label: 'Estimated Duration', type: 'text', placeholder: 'e.g., 15 minutes' },
      { key: 'required_resources', label: 'Required Resources', type: 'tags', placeholder: 'Add resource' },
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ],
    training: [
      { key: 'id', label: 'ID', type: 'text', required: true, placeholder: 'e.g., TRAIN_001' },
      { key: 'user_intent', label: 'User Intent', type: 'select', required: true, options: [
        { value: 'seeking_help', label: 'Seeking Help' },
        { value: 'crisis_support', label: 'Crisis Support' },
        { value: 'information_request', label: 'Information Request' },
        { value: 'progress_update', label: 'Progress Update' },
        { value: 'feedback', label: 'Providing Feedback' }
      ]},
      { key: 'user_input', label: 'User Input', type: 'textarea', required: true, rows: 3 },
      { key: 'expected_response', label: 'Expected Response', type: 'textarea', required: true, rows: 4 },
      { key: 'context', label: 'Context', type: 'json', placeholder: 'JSON object with context information' },
      { key: 'difficulty_level', label: 'Difficulty Level', type: 'select', options: [
        { value: 'basic', label: 'Basic' },
        { value: 'intermediate', label: 'Intermediate' },
        { value: 'complex', label: 'Complex' }
      ]},
      { key: 'tags', label: 'Tags', type: 'tags', placeholder: 'Add tag' },
      { key: 'is_active', label: 'Active', type: 'checkbox' }
    ]
  }

  return fieldConfigs[props.dataType] || []
})

// Methods
const closeModal = () => {
  if (!isSaving.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    delete formData[key]
  })
  Object.keys(jsonFields).forEach(key => {
    delete jsonFields[key]
  })
  Object.keys(jsonErrors).forEach(key => {
    delete jsonErrors[key]
  })
  Object.keys(newTag).forEach(key => {
    delete newTag[key]
  })
  validationErrors.value = []
  isSaving.value = false
}

const initializeForm = () => {
  resetForm()

  if (props.item) {
    // Edit mode - populate with existing data
    Object.assign(formData, { ...props.item })

    // Handle JSON fields
    formFields.value.forEach(field => {
      if (field.type === 'json' && props.item[field.key]) {
        jsonFields[field.key] = JSON.stringify(props.item[field.key], null, 2)
      }
    })
  } else {
    // Create mode - set defaults
    formFields.value.forEach(field => {
      if (field.type === 'checkbox') {
        formData[field.key] = true
      } else if (field.type === 'tags') {
        formData[field.key] = []
      } else if (field.type === 'json') {
        jsonFields[field.key] = ''
      }
    })
  }
}

const validateJson = (fieldKey) => {
  const value = jsonFields[fieldKey]
  if (!value) {
    delete jsonErrors[fieldKey]
    return
  }

  try {
    const parsed = JSON.parse(value)
    formData[fieldKey] = parsed
    delete jsonErrors[fieldKey]
  } catch (error) {
    jsonErrors[fieldKey] = 'Invalid JSON format'
  }
}

const addTag = (fieldKey) => {
  const value = newTag[fieldKey]?.trim()
  if (value && !formData[fieldKey]?.includes(value)) {
    if (!formData[fieldKey]) {
      formData[fieldKey] = []
    }
    formData[fieldKey].push(value)
    newTag[fieldKey] = ''
  }
}

const removeTag = (fieldKey, index) => {
  if (formData[fieldKey]) {
    formData[fieldKey].splice(index, 1)
  }
}

const validateForm = () => {
  const errors = []

  formFields.value.forEach(field => {
    if (field.required && !formData[field.key]) {
      errors.push(`${field.label} is required`)
    }

    if (field.type === 'json' && jsonErrors[field.key]) {
      errors.push(`${field.label}: ${jsonErrors[field.key]}`)
    }
  })

  validationErrors.value = errors
  return errors.length === 0
}

const saveItem = async () => {
  if (!validateForm()) {
    return
  }

  isSaving.value = true

  try {
    // Process JSON fields
    formFields.value.forEach(field => {
      if (field.type === 'json' && jsonFields[field.key]) {
        validateJson(field.key)
      }
    })

    // Emit save event
    emit('save', { ...formData })

    // Close modal after successful save
    setTimeout(() => {
      closeModal()
    }, 500)

  } catch (error) {
    console.error('Save error:', error)
    validationErrors.value = ['An error occurred while saving. Please try again.']
  } finally {
    isSaving.value = false
  }
}

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

watch(() => props.item, () => {
  if (props.isOpen) {
    initializeForm()
  }
})
</script>

<style scoped>
/* Form styling */
.form-input {
  @apply mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm;
}

/* JSON editor styling */
.json-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* Tag styling */
.tag {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800;
}

/* Animation classes */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* Spinner animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>