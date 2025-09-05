<template>
  <NuxtLayout name="admin">
    <div class="min-h-screen bg-gray-50">
      <!-- Main Container -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header Section -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div class="px-6 py-8 sm:px-8">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h1 class="text-3xl font-bold text-gray-900">Dataset Management</h1>
                </div>
                <p class="text-gray-600 text-lg">
                  Manage mental health datasets with an intuitive, spreadsheet-like interface
                </p>
              </div>
              <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <button
                  @click="refreshData"
                  :disabled="loading"
                  class="btn-secondary flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
                </button>
                <button
                  @click="openImportModal"
                  class="btn-primary flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span>Import Data</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 lg:gap-6 mb-8">
          <div
            v-for="stat in statistics"
            :key="stat.key"
            class="stats-card bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all duration-200"
          >
            <div class="p-6">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-3">
                    <div class="w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-lg" :class="getStatIconClass(stat.key)">
                      {{ stat.icon }}
                    </div>
                  </div>
                  <p class="text-sm font-medium text-gray-600 mb-1">
                    {{ stat.label }}
                  </p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ stat.value.toLocaleString() }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Type Navigation -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Data Categories</h2>
            <p class="text-sm text-gray-600 mt-1">Select a category to view and manage its data</p>
          </div>
          <div class="p-2">
            <nav class="flex flex-wrap gap-2" aria-label="Data type tabs">
              <button
                v-for="dataType in dataTypes"
                :key="dataType.key"
                @click="setActiveDataType(dataType.key)"
                class="tab-button flex items-center gap-2 px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200"
                :class="[
                  activeDataType === dataType.key
                    ? 'bg-blue-50 text-blue-700 border-2 border-blue-200 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 border-2 border-transparent'
                ]"
              >
                <span>{{ dataType.label }}</span>
                <span
                  class="inline-flex items-center justify-center min-w-[24px] h-6 px-2 rounded-full text-xs font-semibold"
                  :class="[
                    activeDataType === dataType.key
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600'
                  ]"
                >
                  {{ dataType.count.toLocaleString() }}
                </span>
              </button>
            </nav>
          </div>
        </div>

        <!-- Dataset Table Container -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-gray-900">{{ currentDataTypeLabel }}</h2>
                <p class="text-sm text-gray-600 mt-1">Manage and edit {{ currentDataTypeLabel.toLowerCase() }} data</p>
              </div>
              <div class="flex items-center gap-3">
                <button
                  @click="openCreateModal"
                  class="btn-primary flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Add New</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Dataset Table -->
          <DatasetTable
            :title="currentDataTypeLabel"
            :data="currentData"
            :columns="currentColumns"
            :loading="loading"
            :error="error"
            @create="openCreateModal"
            @edit="openEditModal"
            @delete="deleteItem"
            @bulk-delete="bulkDeleteItems"
            @refresh="refreshData"
          />
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <ImportModal
      :is-open="showImportModal"
      @close="closeImportModal"
      @import-success="handleImportSuccess"
    />

    <!-- Edit Modal -->
    <DatasetEditModal
      :is-open="showEditModal"
      :data-type="activeDataType"
      :item="editingItem"
      @close="closeEditModal"
      @save="handleSave"
    />
  </NuxtLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Define page meta
definePageMeta({
  layout: false
  // TEMPORARILY DISABLED: Admin authentication middleware
  // middleware: 'auth-admin'  // Uncomment to restore authentication
})

// Components
import DatasetTable from '~/components/admin/DatasetTable.vue'
import ImportModal from '~/components/admin/ImportModal.vue'
import DatasetEditModal from '~/components/admin/DatasetEditModal.vue'

// Reactive data
const loading = ref(false)
const error = ref(null)
const activeDataType = ref('problems')
const showImportModal = ref(false)
const showEditModal = ref(false)
const editingItem = ref(null)

// Get runtime config for API URLs
const config = useRuntimeConfig()
const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

// Dataset storage
const datasets = ref({
  problems: [],
  assessments: [],
  suggestions: [],
  feedback_prompts: [],
  next_actions: [],
  training_examples: [],
  vector_database: []
})

// Static configuration
const dataTypes = ref([
  { key: 'problems', label: 'Problem Categories', count: 0 },
  { key: 'assessments', label: 'Assessment Questions', count: 0 },
  { key: 'suggestions', label: 'Therapeutic Suggestions', count: 0 },
  { key: 'feedback_prompts', label: 'Feedback Prompts', count: 0 },
  { key: 'next_actions', label: 'Next Actions', count: 0 },
  { key: 'training_examples', label: 'Fine-tuning Examples', count: 0 },
  { key: 'vector_database', label: 'Vector Database', count: 0 }
])

// Column configurations for each data type
const columnConfigs = {
  problems: [
    { key: 'problem_id', label: 'Problem ID', type: 'text' },
    { key: 'problem_name', label: 'Problem Name', type: 'text' },
    { key: 'category', label: 'Category', type: 'badge' },
    { key: 'domain', label: 'Domain', type: 'badge' },
    { key: 'description', label: 'Description', type: 'text' },
    { key: 'severity_level', label: 'Severity', type: 'badge' },
    { key: 'category_id', label: 'Category ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'is_active', label: 'Active', type: 'boolean' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  assessments: [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'question_id', label: 'Question ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'question_text', label: 'Question', type: 'text' },
    { key: 'question_type', label: 'Question Type', type: 'text' },
    { key: 'options', label: 'Options', type: 'badge' },
    { key: 'scoring_weights', label: 'Scoring Weights', type: 'badge' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  suggestions: [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'suggestion_id', label: 'Suggestion ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'suggestion_text', label: 'Suggestion', type: 'text' },
    { key: 'suggestion_type', label: 'Type', type: 'text' },
    { key: 'effectiveness_rating', label: 'Effectiveness', type: 'text' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  'feedback_prompts': [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'prompt_id', label: 'Prompt ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'prompt_text', label: 'Prompt', type: 'text' },
    { key: 'prompt_type', label: 'Type', type: 'text' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  'next_actions': [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'action_id', label: 'Action ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'action_text', label: 'Action', type: 'text' },
    { key: 'action_type', label: 'Type', type: 'text' },
    { key: 'priority_level', label: 'Priority', type: 'badge' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  'training_examples': [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'example_id', label: 'Example ID', type: 'text' },
    { key: 'sub_category_id', label: 'Subcategory ID', type: 'text' },
    { key: 'user_input', label: 'User Input', type: 'text' },
    { key: 'ai_response', label: 'AI Response', type: 'text' },
    { key: 'context', label: 'Context', type: 'text' },
    { key: 'created_at', label: 'Created', type: 'date' }
  ],
  'vector_database': [
    { key: 'id', label: 'Point ID', type: 'text' },
    { key: 'collection', label: 'Collection', type: 'badge' },
    { key: 'text', label: 'Text Content', type: 'text' },
    { key: 'domain', label: 'Domain', type: 'badge' },
    { key: 'type', label: 'Type', type: 'badge' },
    { key: 'score', label: 'Similarity Score', type: 'number' },
    { key: 'vector_size', label: 'Vector Size', type: 'number' },
    { key: 'metadata', label: 'Metadata', type: 'json' }
  ]
}

// Computed properties
const currentData = computed(() => datasets.value[activeDataType.value] || [])
const currentColumns = computed(() => columnConfigs[activeDataType.value] || [])
const currentDataTypeLabel = computed(() => {
  const dataType = dataTypes.value.find(dt => dt.key === activeDataType.value)
  return dataType ? dataType.label : 'Dataset'
})

const statistics = computed(() => [
  {
    key: 'total_problems',
    label: 'Problem Categories',
    value: dataTypes.value.find(dt => dt.key === 'problems')?.count || 0,
    icon: '🧠'
  },
  {
    key: 'total_assessments',
    label: 'Assessment Questions',
    value: dataTypes.value.find(dt => dt.key === 'assessments')?.count || 0,
    icon: '📋'
  },
  {
    key: 'total_suggestions',
    label: 'Therapeutic Suggestions',
    value: dataTypes.value.find(dt => dt.key === 'suggestions')?.count || 0,
    icon: '💡'
  },
  {
    key: 'total_feedback',
    label: 'Feedback Prompts',
    value: dataTypes.value.find(dt => dt.key === 'feedback_prompts')?.count || 0,
    icon: '💬'
  },
  {
    key: 'total_actions',
    label: 'Next Actions',
    value: dataTypes.value.find(dt => dt.key === 'next_actions')?.count || 0,
    icon: '⚡'
  },
  {
    key: 'total_training',
    label: 'Training Examples',
    value: dataTypes.value.find(dt => dt.key === 'training_examples')?.count || 0,
    icon: '🎯'
  }
])

// Helper function for stat card styling
const getStatIconClass = (key) => {
  const classes = {
    'total_problems': 'from-purple-500 to-purple-600',
    'total_assessments': 'from-blue-500 to-blue-600',
    'total_suggestions': 'from-yellow-500 to-yellow-600',
    'total_feedback': 'from-green-500 to-green-600',
    'total_actions': 'from-red-500 to-red-600',
    'total_training': 'from-indigo-500 to-indigo-600'
  }
  return classes[key] || 'from-gray-500 to-gray-600'
}

// Methods
const setActiveDataType = (dataType) => {
  activeDataType.value = dataType
  error.value = null
}

const refreshData = async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch data for all types
    const promises = dataTypes.value.map(async (dataType) => {
      try {
        const response = await $fetch(`${adminApiUrl}/dataset/${dataType.key}`
          // TEMPORARILY DISABLED: Authentication headers
          // , {
          //   headers: {
          //     'Authorization': `Bearer ${useCookie('auth-token').value}`
          //   }
          // }
        )
        return {
          key: dataType.key,
          data: response.data?.items || [],
          total: response.data?.total || 0
        }
      } catch (err) {
        console.warn(`Failed to fetch ${dataType.key}:`, err)
        return { key: dataType.key, data: [], total: 0 }
      }
    })

    const results = await Promise.all(promises)

    results.forEach(result => {
      datasets.value[result.key] = result.data
      // Update count using the total from API response
      const dataType = dataTypes.value.find(dt => dt.key === result.key)
      if (dataType) {
        dataType.count = result.total
      }
    })

  } catch (err) {
    console.error('Error fetching data:', err)
    error.value = 'Failed to load data. Please try again.'
  } finally {
    loading.value = false
  }
}

const openImportModal = () => {
  showImportModal.value = true
}

const closeImportModal = () => {
  showImportModal.value = false
}

const openCreateModal = () => {
  editingItem.value = null
  showEditModal.value = true
}

const openEditModal = (item) => {
  editingItem.value = item
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingItem.value = null
}

const handleSave = async (itemData) => {
  try {
    // TEMPORARILY DISABLED: Authentication token
    // const authToken = useCookie('auth-token').value

    if (editingItem.value) {
      // Update existing item
      await $fetch(`${adminApiUrl}/dataset/${activeDataType.value}/${editingItem.value.id}`, {
        method: 'PUT',
        body: itemData
        // TEMPORARILY DISABLED: Authentication headers
        // , headers: {
        //   'Authorization': `Bearer ${authToken}`
        // }
      })
    } else {
      // Create new item
      await $fetch(`${adminApiUrl}/dataset/${activeDataType.value}`, {
        method: 'POST',
        body: itemData
        // TEMPORARILY DISABLED: Authentication headers
        // , headers: {
        //   'Authorization': `Bearer ${authToken}`
        // }
      })
    }

    // Refresh data
    await refreshData()

  } catch (err) {
    console.error('Error saving item:', err)
    throw err
  }
}

const deleteItem = async (item) => {
  try {
    // TEMPORARILY DISABLED: Authentication token
    // const authToken = useCookie('auth-token').value

    await $fetch(`${adminApiUrl}/dataset/${activeDataType.value}/${item.id}`, {
      method: 'DELETE'
      // TEMPORARILY DISABLED: Authentication headers
      // , headers: {
      //   'Authorization': `Bearer ${authToken}`
      // }
    })

    // Refresh data
    await refreshData()

  } catch (err) {
    console.error('Error deleting item:', err)
    alert('Failed to delete item. Please try again.')
  }
}

const bulkDeleteItems = async (itemIds) => {
  try {
    // TEMPORARILY DISABLED: Authentication token
    // const authToken = useCookie('auth-token').value

    await $fetch(`${adminApiUrl}/dataset/${activeDataType.value}/bulk-delete`, {
      method: 'POST',
      body: { ids: itemIds }
      // TEMPORARILY DISABLED: Authentication headers
      // , headers: {
      //   'Authorization': `Bearer ${authToken}`
      // }
    })

    // Refresh data
    await refreshData()

  } catch (err) {
    console.error('Error bulk deleting items:', err)
    alert('Failed to delete items. Please try again.')
  }
}

const handleImportSuccess = async (result) => {
  // Refresh data after successful import
  await refreshData()
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
/* Modern Admin Interface Styles */

/* Button Components */
.btn-primary {
  @apply bg-gradient-to-r from-blue-600 to-blue-700 text-white border border-transparent rounded-lg shadow-sm hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-white text-gray-700 border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

/* Statistics Cards */
.stats-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stats-card:hover {
  transform: translateY(-4px) scale(1.02);
}

/* Tab Navigation */
.tab-button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 48px;
}

.tab-button:hover {
  transform: translateY(-1px);
}

/* Loading Animation */
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

/* Responsive Design */
@media (max-width: 640px) {
  .stats-card {
    transform: none;
  }

  .stats-card:hover {
    transform: translateY(-2px);
  }

  .tab-button {
    min-width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 1024px) {
  .xl\:grid-cols-6 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Focus States */
.focus\:ring-2:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

/* Smooth Transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

.duration-200 {
  transition-duration: 200ms;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Enhanced Shadow System */
.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Glass Effect for Cards */
.bg-white {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}

/* Improved Border Radius */
.rounded-xl {
  border-radius: 0.75rem;
}

.rounded-lg {
  border-radius: 0.5rem;
}
</style>