<template>
  <Sheet :open="isOpen" @update:open="$emit('close')">
    <SheetContent
      side="right"
      class="w-full max-w-full sm:max-w-lg md:max-w-2xl lg:max-w-3xl xl:max-w-4xl h-full overflow-y-auto"
    >
      <SheetHeader class="pb-4">
        <SheetTitle class="text-lg sm:text-xl">Import Data</SheetTitle>
        <SheetDescription class="text-sm sm:text-base">
          Upload data files to import into the selected dataset
        </SheetDescription>
      </SheetHeader>

      <div class="grid gap-4 sm:gap-6 py-4">


        <!-- File Upload Area -->
        <div class="mb-4 sm:mb-6">
          <label class="block text-sm sm:text-base font-medium text-gray-700 mb-2 sm:mb-3">
            Select File
          </label>
          <div
            class="mt-1 flex justify-center px-4 sm:px-6 pt-4 sm:pt-5 pb-4 sm:pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors"
            :class="{
              'border-blue-400 bg-blue-50': isDragOver,
              'border-green-400 bg-green-50': selectedFile
            }"
            @drop="handleDrop"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
          >
            <div class="space-y-4 text-center">
              <div v-if="!selectedFile">
                <!-- Document icon -->
                <svg
                  class="mx-auto h-12 w-12 sm:h-16 sm:w-16 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>

                <!-- Primary upload button -->
                <div class="space-y-2">
                  <label
                    for="file-upload"
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer transition-colors"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Choose File
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      class="sr-only"
                      :accept="acceptedFileTypes"
                      @change="handleFileSelect"
                    />
                  </label>

                  <p class="text-sm text-gray-500">or drag and drop here</p>
                  <p class="text-xs text-gray-400">
                    {{ acceptedFileTypesText }}
                  </p>
                </div>

                <!-- Compact tip -->
                <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p class="text-xs text-blue-700">
                    💡 <strong>Tip:</strong> Upload actual data rows, not template files
                  </p>
                </div>
              </div>
              <div v-else class="space-y-2">
                <svg
                  class="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-gray-900 font-medium text-center break-all px-2">{{ selectedFile.name }}</div>
                <div class="text-xs text-gray-500 text-center">{{ formatFileSize(selectedFile.size) }}</div>
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

        <!-- Data Type Selection and Template Downloads -->
        <div class="mb-4 sm:mb-6 space-y-4">
          <div v-if="!dataType">
            <label class="block text-sm sm:text-base font-medium text-gray-700 mb-2 sm:mb-3">
              Data Type
            </label>
            <Select v-model="selectedDataType">
              <SelectTrigger>
                <SelectValue placeholder="Select a data type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="dataType in dataTypes" :key="dataType.value" :value="dataType.value">
                  {{ dataType.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Show selected data type when filtered -->
          <div v-else>
            <label class="block text-sm sm:text-base font-medium text-gray-700 mb-2 sm:mb-3">
              Data Type
            </label>
            <div class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md">
              <span class="text-sm sm:text-base text-gray-900">{{ dataTypes[0]?.label }}</span>
            </div>
          </div>

          <!-- Template and Example Downloads -->
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Download Template</h4>
                <p class="text-xs text-gray-600">
                  {{ selectedDataType ? 'Get a template file to fill out with your data' : 'Select a data type first' }}
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <Button
                  @click="downloadTemplate('csv')"
                  variant="outline"
                  size="sm"
                  :disabled="!selectedDataType"
                  class="flex-1 sm:flex-none min-w-0"
                >
                  CSV
                </Button>
                <Button
                  @click="downloadTemplate('xlsx')"
                  variant="outline"
                  size="sm"
                  :disabled="!selectedDataType"
                  class="flex-1 sm:flex-none min-w-0"
                >
                  Excel
                </Button>
                <Button
                  @click="downloadTemplate('json')"
                  variant="outline"
                  size="sm"
                  :disabled="!selectedDataType"
                  class="flex-1 sm:flex-none min-w-0"
                >
                  JSON
                </Button>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-blue-50 rounded-lg gap-3 sm:gap-0">
              <div class="flex-1">
                <h4 class="text-sm font-medium text-blue-900">Download Example</h4>
                <p class="text-xs text-blue-600">
                  {{ selectedDataType ? 'Get sample data to see the correct format' : 'Select a data type first' }}
                </p>
              </div>
              <Button
                @click="downloadExample"
                variant="outline"
                size="sm"
                class="border-blue-300 text-blue-700 hover:bg-blue-100 w-full sm:w-auto"
                :disabled="!selectedDataType"
              >
                Example
              </Button>
            </div>
          </div>
        </div>

        <!-- Import Options (only shown when file is selected) -->
        <div v-if="selectedFile" class="mb-4 sm:mb-6 space-y-4">
          <div class="flex items-center">
            <input
              id="overwrite-existing"
              v-model="overwriteExisting"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="overwrite-existing" class="ml-2 block text-sm sm:text-base text-gray-900">
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
            <label for="validate-data" class="ml-2 block text-sm sm:text-base text-gray-900">
              Validate data before import
            </label>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="isUploading" class="mb-4 sm:mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm sm:text-base font-medium text-gray-700">Uploading...</span>
            <span class="text-sm sm:text-base text-gray-500">{{ uploadProgress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <h3 class="text-sm sm:text-base font-medium text-red-800">Import Error</h3>
              <div class="mt-2 text-sm sm:text-base text-red-700 whitespace-pre-line">
                {{ errorMessage }}
              </div>
              <div v-if="errorMessage.includes('validation errors')" class="mt-3 p-3 bg-red-100 rounded border border-red-300">
                <h4 class="text-sm font-medium text-red-800 mb-2">💡 Quick Fix Tips:</h4>
                <ul class="text-xs text-red-700 space-y-1">
                  <li>• Make sure you're uploading actual data, not a template file</li>
                  <li>• For Excel files: Fill the template with your data before importing</li>
                  <li>• Check that your file has proper headers in the first row</li>
                  <li>• Ensure all required columns are present and have data</li>
                  <li>• Download the template to see the correct format</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-4 sm:mb-6 p-3 sm:p-4 bg-green-50 border border-green-200 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm sm:text-base font-medium text-green-800">Import Successful</h3>
              <div class="mt-2 text-sm sm:text-base text-green-700">
                {{ successMessage }}
              </div>
            </div>
          </div>
        </div>

      </div>

      <SheetFooter class="flex flex-col sm:flex-row gap-2 sm:gap-0">
        <Button
          variant="outline"
          @click="$emit('close')"
          :disabled="isUploading"
          class="w-full sm:w-auto order-2 sm:order-1"
        >
          Cancel
        </Button>
        <Button
          @click="startImport"
          :disabled="!canImport || isUploading"
          class="w-full sm:w-auto order-1 sm:order-2"
        >
          <svg
            v-if="isUploading"
            class="animate-spin -ml-1 mr-2 h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isUploading ? 'Importing...' : 'Import Data' }}
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  dataType: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'import-success'])

// Reactive data
const selectedFile = ref(null)
const selectedDataType = ref('')
const overwriteExisting = ref(false)
const validateData = ref(false)
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const successMessage = ref('')

// Static data
const allDataTypes = [
  { value: 'problems', label: 'Problem Categories' },
  { value: 'assessments', label: 'Assessment Questions' },
  { value: 'suggestions', label: 'Therapeutic Suggestions' },
  { value: 'feedback_prompts', label: 'Feedback Prompts' },
  { value: 'next_actions', label: 'Next Actions' },
  { value: 'training_examples', label: 'Fine-tuning Examples' },
  { value: 'problem_types', label: 'Problem Types' },
  { value: 'domain_types', label: 'Domain Types' }
]

// Computed properties
const dataTypes = computed(() => {
  if (props.dataType) {
    // Filter to only show the specified data type
    return allDataTypes.filter(dt => dt.value === props.dataType)
  }
  return allDataTypes
})
const acceptedFileTypes = computed(() => {
  return '.csv,.xlsx,.xls'
})

const acceptedFileTypesText = computed(() => {
  return 'CSV, Excel files up to 10MB'
})

const canImport = computed(() => {
  return selectedFile.value && selectedDataType.value
})

// Methods
const closeModal = () => {
  if (!isUploading.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  selectedFile.value = null
  selectedDataType.value = props.dataType || ''
  overwriteExisting.value = false
  validateData.value = false
  isDragOver.value = false
  isUploading.value = false
  uploadProgress.value = 0
  errorMessage.value = ''
  successMessage.value = ''
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await validateAndSetFile(file)
  }
}

const handleDrop = async (event) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer.files
  if (files.length > 0) {
    await validateAndSetFile(files[0])
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

const validateAndSetFile = async (file) => {
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

  // Template file validation removed - accepting all valid files

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
    formData.append('overwrite', overwriteExisting.value)
    formData.append('validate', validateData.value)

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
      }
    }, 200)

    // Make API call
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

    const response = await $fetch(`${adminApiUrl}/import-export/import/${selectedDataType.value}`, {
      method: 'POST',
      body: formData
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.success) {
      // Complete success
      successMessage.value = `Successfully imported ${response.imported_count} records.`
      emit('import-success', response)

      // Auto-close after success
      setTimeout(() => {
        closeModal()
      }, 2000)
    } else if (response.imported_count > 0) {
      // Partial success - some records imported, some failed
      successMessage.value = `Import completed with issues: ${response.imported_count} records imported, ${response.failed_count} failed.`
      if (response.errors && response.errors.length > 0) {
        const errorDetails = response.errors.slice(0, 5).join('\n• ')
        errorMessage.value = `Some records failed to import:\n\n• ${errorDetails}${response.errors.length > 5 ? `\n\n... and ${response.errors.length - 5} more errors` : ''}`
      }
      emit('import-success', response)
    } else {
      // Complete failure - show detailed errors
      if (response.errors && response.errors.length > 0) {
        const errorDetails = response.errors.slice(0, 5).join('\n• ')
        errorMessage.value = `Import failed:\n\n• ${errorDetails}${response.errors.length > 5 ? `\n\n... and ${response.errors.length - 5} more errors` : ''}`
      } else {
        throw new Error(response.message || 'Import failed')
      }
    }

  } catch (error) {
    console.error('Import error:', error)

    // Handle different types of errors
    if (error.data && error.data.errors) {
      // Backend validation errors
      const errorDetails = error.data.errors.slice(0, 3) // Show first 3 errors
      const errorSummary = errorDetails.map((err, index) => {
        if (err.includes('Model validation failed')) {
          return `Row ${index + 1}: Invalid data format - please check your CSV structure`
        }
        return `Row ${index + 1}: ${err.split(': ')[1] || err}`
      }).join('\n')

      errorMessage.value = `Import failed with validation errors:\n\n${errorSummary}${error.data.errors.length > 3 ? `\n\n... and ${error.data.errors.length - 3} more errors` : ''}\n\nPlease check your CSV file format and try again.`
    } else if (error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'An error occurred during import. Please try again.'
    }
  } finally {
    isUploading.value = false
  }
}

// Watchers
// Download methods
const downloadTemplate = async (format) => {
  if (!selectedDataType.value) {
    errorMessage.value = 'Please select a data type first'
    return
  }

  try {
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

    const downloadUrl = `${adminApiUrl}/import-export/template/${selectedDataType.value}?format=${format}`

    // Create download link
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${selectedDataType.value}_template.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

  } catch (error) {
    console.error('Template download failed:', error)
    errorMessage.value = 'Failed to download template. Please try again.'
  }
}

const downloadExample = async () => {
  if (!selectedDataType.value) {
    errorMessage.value = 'Please select a data type first'
    return
  }

  try {
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

    // Get sample data from test-data endpoint
    const response = await $fetch(`${adminApiUrl}/import-export/test-data/${selectedDataType.value}`)

    if (response.sample_data && response.sample_data.length > 0) {
      // Convert to CSV format
      const headers = Object.keys(response.sample_data[0])
      const csvContent = [
        headers.join(','),
        ...response.sample_data.map(row =>
          headers.map(header => {
            const value = row[header]
            // Escape CSV values
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
              return `"${value.replace(/"/g, '""')}"`
            }
            return value
          }).join(',')
        )
      ].join('\n')

      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${selectedDataType.value}_example.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } else {
      errorMessage.value = 'No example data available for this data type'
    }

  } catch (error) {
    console.error('Example download failed:', error)
    errorMessage.value = 'Failed to download example data. Please try again.'
  }
}

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