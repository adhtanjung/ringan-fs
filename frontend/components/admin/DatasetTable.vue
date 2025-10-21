<template>
  <TooltipProvider>
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Table Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
            <p class="text-sm text-gray-600">Manage and edit {{ title.toLowerCase() }} data</p>
          </div>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {{ totalItems }} items
          </span>
        </div>
        <div class="flex items-center space-x-3">
          <!-- Search -->
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="block w-64 pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>

          <!-- Add New Button -->
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add New {{ title }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="px-6 py-12 text-center">
      <div class="text-red-600 mb-2">
        <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-1">Error loading data</h3>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <button
        @click="fetchData"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Try Again
      </button>
    </div>

    <!-- Data Table -->
    <div v-else class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <!-- Select All Checkbox -->
              <th scope="col" class="relative w-12 px-6 sm:w-16 sm:px-8">
                <input
                  type="checkbox"
                  :checked="selectedItems.length === filteredData.length && filteredData.length > 0"
                  :indeterminate="selectedItems.length > 0 && selectedItems.length < filteredData.length"
                  @change="toggleSelectAll"
                  class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 sm:left-6"
                />
              </th>

              <!-- Dynamic Headers -->
              <th
                v-for="column in columns"
                :key="column.key"
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                @click="sortBy(column.key)"
              >
                <div class="flex items-center space-x-1">
                  <span>{{ column.label }}</span>
                  <!-- Info Tooltip -->
                  <Tooltip v-if="column.description">
                    <TooltipTrigger as-child>
                      <button
                        type="button"
                        class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
                        @click.stop
                      >
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent class="max-w-xs bg-blue-700 text-white">
                      <p class="text-sm">{{ column.description }}</p>
                    </TooltipContent>
                  </Tooltip>
                  <!-- Sort Icon -->
                  <svg
                    v-if="sortColumn === column.key"
                    class="h-4 w-4 text-gray-400"
                    :class="{ 'transform rotate-180': sortDirection === 'desc' }"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>

              <!-- Actions -->
              <th scope="col" class="sticky right-0 bg-gray-50 px-6 py-3 z-10">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(item, index) in paginatedData"
              :key="item.id || index"
              class="hover:bg-gray-50 group"
              :class="{ 'bg-blue-50': selectedItems.includes(item.id) }"
            >
              <!-- Select Checkbox -->
              <td class="relative w-12 px-6 sm:w-16 sm:px-8">
                <input
                  type="checkbox"
                  :value="item.id"
                  v-model="selectedItems"
                  class="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 sm:left-6"
                />
              </td>

              <!-- Dynamic Cells -->
              <td
                v-for="column in columns"
                :key="column.key"
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
              >
                <div v-if="column.type === 'text'" class="max-w-xs truncate" :title="getNestedValue(item, column.key)">
                  {{ getNestedValue(item, column.key) || '-' }}
                </div>
                <div v-else-if="column.type === 'badge'" class="flex flex-wrap gap-1">
                  <span
                    v-for="tag in (Array.isArray(getNestedValue(item, column.key)) ? getNestedValue(item, column.key) : [getNestedValue(item, column.key)])"
                    :key="tag"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getBadgeClass(tag, column.key)"
                  >
                    {{ tag }}
                  </span>
                </div>
                <div v-else-if="column.type === 'boolean'">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getNestedValue(item, column.key) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ getNestedValue(item, column.key) ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div v-else-if="column.type === 'date'">
                  {{ formatDate(getNestedValue(item, column.key)) }}
                </div>
                <div v-else>
                  {{ getNestedValue(item, column.key) || '-' }}
                </div>
              </td>

              <!-- Actions -->
              <td class="sticky right-0 bg-white group-hover:bg-gray-50 px-6 py-4 whitespace-nowrap text-right text-sm font-medium z-10 shadow-[-4px_0_6px_-2px_rgba(0,0,0,0.1)]">
                <div class="flex items-center justify-end space-x-2">
                  <button
                    @click="editItem(item)"
                    class="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-100"
                    title="Edit"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteItem(item)"
                    class="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-100"
                    title="Delete"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="previousPage"
            :disabled="props.currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="props.currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ (props.currentPage - 1) * props.pagination.limit + 1 }}</span>
              to
              <span class="font-medium">{{ Math.min(props.currentPage * props.pagination.limit, totalItems) }}</span>
              of
              <span class="font-medium">{{ totalItems }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="previousPage"
                :disabled="props.currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  page === props.currentPage
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                ]"
              >
                {{ page }}
              </button>

              <button
                @click="nextPage"
                :disabled="props.currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions Bar -->
    <div
      v-if="selectedItems.length > 0"
      class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 sm:px-6 lg:px-8 shadow-lg z-50"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <span class="text-sm text-gray-700">
            {{ selectedItems.length }} item{{ selectedItems.length !== 1 ? 's' : '' }} selected
          </span>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="bulkDelete"
            class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <svg class="-ml-0.5 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete Selected
          </button>
          <button
            @click="clearSelection"
            class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Clear Selection
          </button>
        </div>
      </div>
    </div>
  </div>
  </TooltipProvider>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '~/components/ui/tooltip'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  pageSize: {
    type: Number,
    default: 20
  },
  pagination: {
    type: Object,
    default: () => ({ skip: 0, limit: 50, total: 0, has_more: false })
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  }
})

// Emits
const emit = defineEmits([
  'create',
  'edit',
  'delete',
  'bulk-delete',
  'refresh',
  'page-change',
  'page-size-change',
  'next-page',
  'prev-page'
])

// Reactive data
const searchQuery = ref('')
const selectedItems = ref([])
const currentPage = ref(1)
const sortColumn = ref('')
const sortDirection = ref('asc')

// Computed properties
const filteredData = computed(() => {
  if (!searchQuery.value) return props.data

  const query = searchQuery.value.toLowerCase()
  return props.data.filter(item => {
    return props.columns.some(column => {
      const value = getNestedValue(item, column.key)
      if (typeof value === 'string') {
        return value.toLowerCase().includes(query)
      }
      if (Array.isArray(value)) {
        return value.some(v => String(v).toLowerCase().includes(query))
      }
      return String(value).toLowerCase().includes(query)
    })
  })
})

const sortedData = computed(() => {
  if (!sortColumn.value) return filteredData.value

  return [...filteredData.value].sort((a, b) => {
    const aValue = getNestedValue(a, sortColumn.value)
    const bValue = getNestedValue(b, sortColumn.value)

    let comparison = 0
    if (aValue < bValue) comparison = -1
    if (aValue > bValue) comparison = 1

    return sortDirection.value === 'desc' ? -comparison : comparison
  })
})

const totalItems = computed(() => props.pagination.total || filteredData.value.length)
const totalPages = computed(() => props.totalPages || Math.ceil(totalItems.value / props.pageSize))

const paginatedData = computed(() => {
  // For server-side pagination, we use the data as-is since it's already paginated
  return sortedData.value
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = props.currentPage

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

// Methods
const getNestedValue = (obj, path) => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const getBadgeClass = (value, columnKey) => {
  if (!value) return 'bg-gray-100 text-gray-800'

  // Category-specific colors
  if (columnKey === 'category') {
    const categoryColors = {
      'Anxiety': 'bg-yellow-100 text-yellow-800',
      'Stress': 'bg-red-100 text-red-800',
      'Trauma': 'bg-purple-100 text-purple-800',
      'Depression': 'bg-blue-100 text-blue-800',
      'General': 'bg-gray-100 text-gray-800'
    }
    return categoryColors[value] || 'bg-gray-100 text-gray-800'
  }

  // Domain-specific colors
  if (columnKey === 'domain') {
    const domainColors = {
      'anxiety': 'bg-yellow-100 text-yellow-800',
      'stress': 'bg-red-100 text-red-800',
      'trauma': 'bg-purple-100 text-purple-800',
      'general': 'bg-gray-100 text-gray-800'
    }
    return domainColors[value] || 'bg-gray-100 text-gray-800'
  }

  // Severity level colors
  if (columnKey === 'severity_level') {
    const severity = parseInt(value)
    if (severity >= 4) return 'bg-red-100 text-red-800'
    if (severity >= 3) return 'bg-orange-100 text-orange-800'
    if (severity >= 2) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  // Default badge styling
  return 'bg-gray-100 text-gray-800'
}

const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
}

const toggleSelectAll = () => {
  if (selectedItems.value.length === filteredData.value.length) {
    selectedItems.value = []
  } else {
    selectedItems.value = filteredData.value.map(item => item.id)
  }
}

const clearSelection = () => {
  selectedItems.value = []
}

const previousPage = () => {
  if (props.currentPage > 1) {
    emit('prev-page')
  }
}

const nextPage = () => {
  if (props.currentPage < totalPages.value) {
    emit('next-page')
  }
}

const goToPage = (page) => {
  if (typeof page === 'number' && page >= 1 && page <= totalPages.value) {
    emit('page-change', page)
  }
}

const openCreateModal = () => {
  emit('create')
}

const editItem = (item) => {
  emit('edit', item)
}

const deleteItem = (item) => {
  if (confirm('Are you sure you want to delete this item?')) {
    emit('delete', item)
  }
}

const bulkDelete = () => {
  if (confirm(`Are you sure you want to delete ${selectedItems.value.length} selected items?`)) {
    emit('bulk-delete', selectedItems.value)
    selectedItems.value = []
  }
}

const fetchData = () => {
  emit('refresh')
}

// Watchers
watch(searchQuery, () => {
  // Note: For server-side pagination, we don't reset the page here
  // The parent component should handle search and pagination
})

watch(() => props.data, () => {
  // Clear selection when data changes
  selectedItems.value = []
})
</script>

<style scoped>
/* Custom checkbox indeterminate state */
input[type="checkbox"]:indeterminate {
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M5.707 7.293a1 1 0 0 0-1.414 1.414l2 2a1 1 0 0 0 1.414 0l4-4a1 1 0 0 0-1.414-1.414L7 8.586 5.707 7.293z'/%3e%3c/svg%3e");
  border-color: transparent;
  background-color: currentColor;
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
}

/* Smooth transitions */
.transition-colors {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Table hover effects */
tbody tr:hover {
  background-color: #f9fafb;
}

/* Selected row styling */
tbody tr.bg-blue-50:hover {
  background-color: #dbeafe;
}

/* Scrollbar styling */
.overflow-x-auto::-webkit-scrollbar {
  height: 8px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>