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
      <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
            Import Data
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

        <!-- Import Type Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Import Type
          </label>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="type in importTypes"
              :key="type.value"
              @click="selectedType = type.value"
              class="relative rounded-lg border p-4 flex flex-col items-center space-y-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              :class="[
                selectedType === type.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              ]"
            >
              <div class="text-2xl">{{ type.icon }}</div>
              <div class="text-sm font-medium text-gray-900">{{ type.label }}</div>
              <div class="text-xs text-gray-500 text-center">{{ type.description }}</div>
              <div
                v-if="selectedType === type.value"
                class="absolute top-2 right-2 text-blue-500"
              >
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
            </button>
          </div>
        </div>

        <!-- File Upload Area -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Select File
          </label>
          <div
            class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors"
            :class="{
              'border-blue-400 bg-blue-50': isDragOver,
              'border-green-400 bg-green-50': selectedFile
            }"
            @drop="handleDrop"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
          >
            <div class="space-y-1 text-center">
              <div v-if="!selectedFile">
                <svg
                  class="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                <div class="flex text-sm text-gray-600">
                  <label
                    for="file-upload"
                    class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                  >
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      class="sr-only"
                      :accept="acceptedFileTypes"
                      @change="handleFileSelect"
                    />
                  </label>
                  <p class="pl-1">or drag and drop</p>
                </div>
                <p class="text-xs text-gray-500">
                  {{ acceptedFileTypesText }}
                </p>
              </div>
              <div v-else class="space-y-2">
                <svg
                  class="mx-auto h-12 w-12 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-gray-900 font-medium">{{ selectedFile.name }}</div>
                <div class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</div>
                <button
                  @click="removeFile"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove file
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Import Options -->
        <div v-if="selectedFile" class="mb-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Data Type
            </label>
            <select
              v-model="selectedDataType"
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="">Auto-detect</option>
              <option v-for="dataType in dataTypes" :key="dataType.value" :value="dataType.value">
                {{ dataType.label }}
              </option>
            </select>
          </div>

          <div class="flex items-center">
            <input
              id="overwrite-existing"
              v-model="overwriteExisting"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="overwrite-existing" class="ml-2 block text-sm text-gray-900">
              Overwrite existing data
            </label>
          </div>

          <div class="flex items-center">
            <input
              id="validate-data"
              v-model="validateData"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="validate-data" class="ml-2 block text-sm text-gray-900">
              Validate data before import
            </label>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="isUploading" class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">Uploading...</span>
            <span class="text-sm text-gray-500">{{ uploadProgress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Import Error</h3>
              <div class="mt-2 text-sm text-red-700">
                {{ errorMessage }}
              </div>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">Import Successful</h3>
              <div class="mt-2 text-sm text-green-700">
                {{ successMessage }}
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-end space-x-3">
          <button
            @click="closeModal"
            type="button"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            :disabled="isUploading"
          >
            Cancel
          </button>
          <button
            @click="startImport"
            type="button"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!canImport || isUploading"
          >
            <svg
              v-if="isUploading"
              class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isUploading ? 'Importing...' : 'Import Data' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'import-success'])

// Reactive data
const selectedType = ref('file')
const selectedFile = ref(null)
const selectedDataType = ref('')
const overwriteExisting = ref(false)
const validateData = ref(true)
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const successMessage = ref('')

// Static data
const importTypes = [
  {
    value: 'file',
    label: 'File Upload',
    description: 'Upload CSV or Excel files',
    icon: '📁'
  },
  {
    value: 'url',
    label: 'From URL',
    description: 'Import from web URL',
    icon: '🌐'
  }
]

const dataTypes = [
  { value: 'problems', label: 'Problem Categories' },
  { value: 'assessments', label: 'Assessment Questions' },
  { value: 'suggestions', label: 'Therapeutic Suggestions' },
  { value: 'feedback', label: 'Feedback Prompts' },
  { value: 'next_actions', label: 'Next Actions' },
  { value: 'training', label: 'Fine-tuning Examples' }
]

// Computed properties
const acceptedFileTypes = computed(() => {
  return '.csv,.xlsx,.xls'
})

const acceptedFileTypesText = computed(() => {
  return 'CSV, Excel files up to 10MB'
})

const canImport = computed(() => {
  return selectedFile.value && selectedType.value
})

// Methods
const closeModal = () => {
  if (!isUploading.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  selectedType.value = 'file'
  selectedFile.value = null
  selectedDataType.value = ''
  overwriteExisting.value = false
  validateData.value = true
  isDragOver.value = false
  isUploading.value = false
  uploadProgress.value = 0
  errorMessage.value = ''
  successMessage.value = ''
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const validateAndSetFile = (file) => {
  // Reset messages
  errorMessage.value = ''
  successMessage.value = ''

  // Check file type
  const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
  const allowedExtensions = ['.csv', '.xls', '.xlsx']

  const isValidType = allowedTypes.includes(file.type) ||
    allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))

  if (!isValidType) {
    errorMessage.value = 'Please select a valid CSV or Excel file.'
    return
  }

  // Check file size (10MB limit)
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    errorMessage.value = 'File size must be less than 10MB.'
    return
  }

  selectedFile.value = file
}

const removeFile = () => {
  selectedFile.value = null
  errorMessage.value = ''
  successMessage.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const startImport = async () => {
  if (!canImport.value) return

  isUploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // Create FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('data_type', selectedDataType.value)
    formData.append('overwrite_existing', overwriteExisting.value)
    formData.append('validate_data', validateData.value)

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
      }
    }, 200)

    // Make API call
    const response = await $fetch('/api/v1/admin/dataset/import', {
      method: 'POST',
      body: formData
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.success) {
      successMessage.value = `Successfully imported ${response.imported_count} records.`
      emit('import-success', response)

      // Auto-close after success
      setTimeout(() => {
        closeModal()
      }, 2000)
    } else {
      throw new Error(response.message || 'Import failed')
    }

  } catch (error) {
    console.error('Import error:', error)
    errorMessage.value = error.message || 'An error occurred during import. Please try again.'
  } finally {
    isUploading.value = false
  }
}

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
/* Custom file input styling */
input[type="file"] {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Drag and drop animations */
.border-dashed {
  transition: all 0.2s ease-in-out;
}

/* Progress bar animation */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Modal animations */
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