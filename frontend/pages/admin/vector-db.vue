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
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h1 class="text-3xl font-bold text-gray-900">Vector Database</h1>
                </div>
                <p class="text-gray-600 text-lg">
                  Manage vector embeddings, semantic search, and collection statistics
                </p>
              </div>
              <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <button
                  @click="refreshCollectionStats"
                  :disabled="loading"
                  class="btn-secondary flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
                </button>
                <button
                  @click="checkVectorHealth"
                  class="btn-primary flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Health Check</span>
                </button>
                <button
                  @click="createCollections"
                  :disabled="loading"
                  class="btn-primary flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  <span>{{ loading ? 'Creating...' : 'Create Collections' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Health Status Card -->
        <div v-if="healthStatus" class="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">System Health</h2>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div class="flex items-center gap-3">
                <div class="w-3 h-3 rounded-full" :class="healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'"></div>
                <span class="font-medium">Overall Status: {{ healthStatus.status }}</span>
              </div>
              <div v-if="healthStatus.vector_service">
                <span class="text-sm text-gray-600">Vector Service: </span>
                <span class="font-medium" :class="healthStatus.vector_service.status === 'healthy' ? 'text-green-600' : 'text-red-600'">
                  {{ healthStatus.vector_service.status }}
                </span>
              </div>
              <div>
                <span class="text-sm text-gray-600">Connection Status: </span>
                <span class="font-medium" :class="{
                  'text-green-600': connectionStatus === 'connected',
                  'text-red-600': connectionStatus === 'disconnected',
                  'text-yellow-600': connectionStatus === 'connecting'
                }">
                  {{ connectionStatus || 'Unknown' }}
                </span>
              </div>
              <div v-if="healthStatus.embedding_service">
                <span class="text-sm text-gray-600">Embedding Model: </span>
                <span class="font-medium text-blue-600">{{ healthStatus.embedding_service.model_name }}</span>
              </div>
            </div>
            <div v-if="lastRefresh" class="mt-4 text-sm text-gray-600">
              Last updated: {{ new Date(lastRefresh).toLocaleString() }}
            </div>
          </div>
        </div>

        <!-- Collection Statistics -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Collection Statistics</h2>
            <p class="text-sm text-gray-600 mt-1">Overview of vector collections and their data</p>
          </div>
          <div class="p-6">
            <div v-if="collectionStats.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div
                v-for="collection in collectionStats"
                :key="collection.name"
                class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200 relative"
              >
                <div class="flex items-center justify-between mb-3">
                  <h3 class="font-semibold text-gray-900">{{ formatCollectionName(collection.name) }}</h3>
                  <div class="flex items-center gap-2">
                    <span class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                      {{ collection.status }}
                    </span>
                    <button
                      @click="deleteCollection(collection.name)"
                      :disabled="loading"
                      class="text-red-600 hover:text-red-800 text-sm disabled:opacity-50 p-1"
                      title="Delete Collection"
                    >
                      ✕
                    </button>
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Points:</span>
                    <span class="font-medium">{{ collection.points_count?.toLocaleString() || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Segments:</span>
                    <span class="font-medium">{{ collection.segments_count || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Vector Size:</span>
                    <span class="font-medium">{{ collection.config?.params?.vectors?.size || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Distance:</span>
                    <span class="font-medium">{{ collection.config?.params?.vectors?.distance || 'Unknown' }}</span>
                  </div>
                </div>
                <button
                  @click="getCollectionInfo(collection.name)"
                  class="mt-3 text-xs text-blue-600 hover:text-blue-800 underline"
                >
                  View Details
                </button>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8V4a1 1 0 00-1-1H7a1 1 0 00-1 1v1m8 0V4.5" />
              </svg>
              <p>No collection statistics available.</p>
              <button
                @click="createCollections"
                class="mt-2 text-blue-600 hover:text-blue-800 underline"
              >
                Create collections
              </button>
            </div>
          </div>
        </div>

        <!-- Error Logs & Search History -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Error Logs -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-semibold text-gray-900">Recent Errors</h2>
            </div>
            <div class="p-6">
              <div v-if="apiErrors.length > 0" class="space-y-2 max-h-64 overflow-y-auto">
                <div v-for="(error, index) in apiErrors.slice(0, 10)" :key="index" class="p-3 bg-red-50 border border-red-200 rounded text-sm">
                  <div class="font-semibold text-red-800">{{ error.operation }}</div>
                  <div class="text-red-600">{{ error.error }}</div>
                  <div class="text-xs text-red-500 mt-1">{{ new Date(error.timestamp).toLocaleString() }}</div>
                </div>
              </div>
              <div v-else class="text-gray-500 text-center py-4">
                No recent errors
              </div>
            </div>
          </div>

          <!-- Search History -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-semibold text-gray-900">Search History</h2>
            </div>
            <div class="p-6">
              <div v-if="searchHistory.length > 0" class="space-y-2 max-h-64 overflow-y-auto">
                <div v-for="(search, index) in searchHistory.slice(0, 10)" :key="index" class="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                  <div class="font-semibold text-blue-800">{{ search.query }}</div>
                  <div class="text-blue-600">Collection: {{ formatCollectionName(search.collection) }}</div>
                  <div class="text-xs text-blue-500 mt-1">
                    {{ search.resultsCount }} results in {{ search.searchTime }}ms - {{ new Date(search.timestamp).toLocaleString() }}
                  </div>
                </div>
              </div>
              <div v-else class="text-gray-500 text-center py-4">
                No search history
              </div>
            </div>
          </div>
        </div>

        <!-- Semantic Search Section -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Semantic Search</h2>
            <p class="text-sm text-gray-600 mt-1">Search across vector collections using natural language</p>
          </div>
          <div class="p-6">
            <!-- Search Form -->
            <div class="space-y-4 mb-6">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="lg:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Search Query</label>
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Enter your search query..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    @keyup.enter="performSearch"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Collection</label>
                  <select
                    v-model="selectedCollection"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="mental-health-problems">Problems</option>
                    <option value="mental-health-assessments">Assessments</option>
                    <option value="mental-health-suggestions">Suggestions</option>
                    <option value="mental-health-feedback">Feedback</option>
                    <option value="mental-health-training">Training</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Score Threshold</label>
                  <input
                    v-model.number="scoreThreshold"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div class="flex gap-3">
                <button
                  @click="performSearch"
                  :disabled="!searchQuery || searchLoading"
                  class="btn-primary flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-200"
                >
                  <svg class="w-4 h-4" :class="{ 'animate-spin': searchLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>{{ searchLoading ? 'Searching...' : 'Search' }}</span>
                </button>
                <button
                  @click="clearSearch"
                  class="btn-secondary px-4 py-2 text-sm font-medium transition-all duration-200"
                >
                  Clear
                </button>
              </div>
            </div>

            <!-- Search Results -->
            <div v-if="searchResults.length > 0">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                Search Results ({{ searchResults.length }} found)
              </h3>
              <div class="space-y-4">
                <div
                  v-for="(result, index) in searchResults"
                  :key="index"
                  class="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:bg-gray-100 transition-colors"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-3">
                      <span class="text-sm font-medium text-gray-900">Result {{ index + 1 }}</span>
                      <span class="text-xs px-2 py-1 rounded-full" :class="{
                        'bg-green-100 text-green-700': result.score >= 0.8,
                        'bg-yellow-100 text-yellow-700': result.score >= 0.6 && result.score < 0.8,
                        'bg-red-100 text-red-700': result.score < 0.6
                      }">
                        Score: {{ result.score.toFixed(4) }}
                      </span>
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ result.payload?.type || 'Unknown Type' }}
                    </div>
                  </div>
                  <div class="space-y-2">
                    <div v-if="result.payload?.text" class="text-sm text-gray-700">
                      <strong>Text:</strong> {{ result.payload.text }}
                    </div>
                    <div v-if="result.payload?.domain" class="text-sm text-gray-600">
                      <strong>Domain:</strong> {{ result.payload.domain }}
                    </div>
                    <div v-if="result.payload && Object.keys(result.payload).length > 0" class="text-xs text-gray-500">
                      <details>
                        <summary class="cursor-pointer hover:text-gray-700">View Metadata</summary>
                        <pre class="mt-2 p-2 bg-gray-100 rounded text-xs overflow-x-auto">{{ JSON.stringify(result.payload, null, 2) }}</pre>
                      </details>
                    </div>
                    <div v-if="result.id" class="text-xs text-gray-500 mt-3 font-mono bg-gray-200 p-2 rounded">
                      ID: {{ result.id }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="searchPerformed && !searchLoading" class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p>No results found for your search query</p>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 class="text-sm font-medium text-red-800">Error</h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Define page meta
definePageMeta({
  layout: false
})

// Reactive data
const loading = ref(false)
const searchLoading = ref(false)
const error = ref(null)
const healthStatus = ref(null)
const collectionStats = ref([])
const searchQuery = ref('')
const selectedCollection = ref('mental-health-problems')
const scoreThreshold = ref(0.7)
const searchResults = ref([])
const searchPerformed = ref(false)
const lastRefresh = ref(null)
const connectionStatus = ref('unknown')
const apiErrors = ref([])
const searchHistory = ref([])

// Get runtime config for API URLs
const config = useRuntimeConfig()
const vectorApiUrl = config.public.vectorApiUrl || 'http://localhost:8001/api/v1/vector'

// Enhanced error logging
const logError = (operation, error, context = {}) => {
  const errorEntry = {
    timestamp: new Date().toISOString(),
    operation,
    error: error.message || error,
    context,
    stack: error.stack
  }
  apiErrors.value.unshift(errorEntry)
  if (apiErrors.value.length > 50) apiErrors.value.pop()
  console.error(`[Vector DB Admin] ${operation}:`, error, context)
}

// Connection status checker
const updateConnectionStatus = (status) => {
  connectionStatus.value = status
  if (status === 'connected') {
    lastRefresh.value = new Date().toISOString()
  }
}

// Helper function to format collection names
const formatCollectionName = (name) => {
  return name.replace('mental-health-', '').replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Check vector database health
const checkVectorHealth = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await $fetch(`${vectorApiUrl}/health`, {
      timeout: 10000,
      retry: 2
    })
    healthStatus.value = response
    updateConnectionStatus('connected')
    
    // Enhanced health status validation
    if (response.vector_service?.status !== 'healthy') {
      logError('Health Check', new Error('Vector service unhealthy'), { response })
    }
    if (response.embedding_service?.status !== 'healthy') {
      logError('Health Check', new Error('Embedding service unhealthy'), { response })
    }
  } catch (err) {
    updateConnectionStatus('disconnected')
    error.value = `Health check failed: ${err.message}`
    logError('Health Check', err, { vectorApiUrl })
  } finally {
    loading.value = false
  }
}

// Refresh collection statistics
const refreshCollectionStats = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await $fetch(`${vectorApiUrl}/collections/stats`, {
      timeout: 15000,
      retry: 2
    })
    
    // Enhanced data processing
    if (response && typeof response === 'object') {
      const collections = response.collections || Object.values(response).filter(item => 
        item && typeof item === 'object' && item.name
      )
      collectionStats.value = collections
      updateConnectionStatus('connected')
      
      // Log collection health issues
      collections.forEach(collection => {
        if (collection.error) {
          logError('Collection Stats', new Error(collection.error), { collection: collection.name })
        }
      })
    } else {
      throw new Error('Invalid response format')
    }
  } catch (err) {
    updateConnectionStatus('disconnected')
    error.value = `Failed to fetch collection stats: ${err.message}`
    logError('Collection Stats', err, { vectorApiUrl })
    collectionStats.value = []
  } finally {
    loading.value = false
  }
}

// Perform semantic search
const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  searchLoading.value = true
  error.value = null
  searchPerformed.value = true
  
  const searchParams = {
    query: searchQuery.value,
    collection: selectedCollection.value,
    limit: 10,
    score_threshold: scoreThreshold.value
  }
  
  try {
    const startTime = Date.now()
    const response = await $fetch(`${vectorApiUrl}/search`, {
      method: 'POST',
      body: searchParams,
      timeout: 30000,
      retry: 1
    })
    
    const searchTime = Date.now() - startTime
    
    if (response.success) {
      searchResults.value = response.results || []
      
      // Add to search history
      const historyEntry = {
        timestamp: new Date().toISOString(),
        query: searchQuery.value,
        collection: selectedCollection.value,
        resultsCount: searchResults.value.length,
        searchTime,
        scoreThreshold: scoreThreshold.value
      }
      searchHistory.value.unshift(historyEntry)
      if (searchHistory.value.length > 20) searchHistory.value.pop()
      
      updateConnectionStatus('connected')
    } else {
      error.value = response.error || 'Search failed'
      searchResults.value = []
      logError('Search', new Error(response.error || 'Search failed'), { searchParams, response })
    }
  } catch (err) {
    updateConnectionStatus('disconnected')
    error.value = `Search failed: ${err.message}`
    searchResults.value = []
    logError('Search', err, { searchParams, vectorApiUrl })
  } finally {
    searchLoading.value = false
  }
}

// Clear search results
const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  searchPerformed.value = false
  error.value = null
}

// Get collection management functions
const createCollections = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await $fetch(`${vectorApiUrl}/collections/create`, {
      method: 'POST',
      timeout: 30000
    })
    
    if (response.success) {
      await refreshCollectionStats()
      updateConnectionStatus('connected')
    } else {
      error.value = response.error || 'Failed to create collections'
      logError('Create Collections', new Error(response.error || 'Failed to create collections'), { response })
    }
  } catch (err) {
    updateConnectionStatus('disconnected')
    error.value = `Failed to create collections: ${err.message}`
    logError('Create Collections', err, { vectorApiUrl })
  } finally {
    loading.value = false
  }
}

// Delete collection
const deleteCollection = async (collectionName) => {
  if (!confirm(`Are you sure you want to delete collection '${collectionName}'? This action cannot be undone.`)) {
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const response = await $fetch(`${vectorApiUrl}/collections/${collectionName}`, {
      method: 'DELETE',
      timeout: 15000
    })
    
    if (response.success) {
      await refreshCollectionStats()
      updateConnectionStatus('connected')
    } else {
      error.value = response.error || 'Failed to delete collection'
      logError('Delete Collection', new Error(response.error || 'Failed to delete collection'), { collectionName, response })
    }
  } catch (err) {
    updateConnectionStatus('disconnected')
    error.value = `Failed to delete collection: ${err.message}`
    logError('Delete Collection', err, { collectionName, vectorApiUrl })
  } finally {
    loading.value = false
  }
}

// Get detailed collection info
const getCollectionInfo = async (collectionName) => {
  try {
    const response = await $fetch(`${vectorApiUrl}/collections/${collectionName}/info`, {
      timeout: 10000
    })
    return response
  } catch (err) {
    logError('Collection Info', err, { collectionName })
    return null
  }
}

// Initialize page
onMounted(async () => {
  await Promise.all([
    checkVectorHealth(),
    refreshCollectionStats()
  ])
})
</script>

<style scoped>
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>