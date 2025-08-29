<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
      <div class="flex items-center space-x-4">
        <button @click="goBack" class="p-2 hover:bg-white/20 rounded-full">
          <ArrowLeft class="w-5 h-5" />
        </button>
        <div class="flex-1">
          <div class="flex items-center space-x-2 mb-1">
            <span class="text-2xl">{{ entry?.mood?.emoji }}</span>
            <span class="text-sm text-purple-100">{{ entry?.mood?.label }}</span>
          </div>
          <h1 class="text-xl font-bold mb-1">{{ formatDate(entry?.createdAt) }}</h1>
          <p class="text-purple-100 text-sm">{{ entry?.wordCount }} kata • {{ entry?.readingTime }} min baca</p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="toggleBookmark"
            :class="[
              'p-2 rounded-full transition-colors',
              entry?.bookmarked 
                ? 'bg-yellow-500/20 text-yellow-200' 
                : 'hover:bg-white/20 text-white'
            ]"
          >
            <Bookmark class="w-5 h-5" />
          </button>
          <button
            @click="showMenu = true"
            class="p-2 hover:bg-white/20 rounded-full"
          >
            <MoreVertical class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Entry Content -->
    <div v-if="entry" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <!-- Meta Info -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div class="flex items-center space-x-4">
          <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
            <span class="text-lg">{{ entry.mood.emoji }}</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">{{ entry.mood.label }}</p>
            <p class="text-sm text-gray-500">{{ formatDetailedDate(entry.createdAt) }}</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">
            {{ getTimeAgo(entry.createdAt) }}
          </span>
          <div v-if="entry.prompt" class="flex items-center space-x-1 px-2 py-1 bg-green-100 rounded-full">
            <Lightbulb class="w-3 h-3 text-green-600" />
            <span class="text-xs text-green-700">Prompt</span>
          </div>
        </div>
      </div>

      <!-- Prompt Info (if used) -->
      <div v-if="entry.prompt" class="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
        <div class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
            <component :is="entry.prompt.icon" class="w-4 h-4 text-green-600" />
          </div>
          <div>
            <h4 class="font-medium text-green-900 mb-1">{{ entry.prompt.title }}</h4>
            <p class="text-sm text-green-700">{{ entry.prompt.question }}</p>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="prose prose-gray max-w-none">
        <div class="whitespace-pre-wrap text-gray-800 leading-relaxed" v-html="formatContent(entry.content)"></div>
      </div>

      <!-- Tags -->
      <div v-if="entry.tags && entry.tags.length > 0" class="mt-6 pt-4 border-t border-gray-200">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in entry.tags"
            :key="tag"
            class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
          >
            #{{ tag }}
          </span>
        </div>
      </div>

      <!-- Last Updated -->
      <div v-if="entry.updatedAt && entry.updatedAt !== entry.createdAt" class="mt-4 pt-4 border-t border-gray-200 text-center">
        <p class="text-xs text-gray-500">
          Terakhir diperbarui {{ formatDate(entry.updatedAt) }}
        </p>
      </div>
    </div>

    <!-- Navigation -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between">
        <button
          v-if="previousEntry"
          @click="navigateToEntry(previousEntry.id)"
          class="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
          <span class="text-sm">Sebelumnya</span>
        </button>
        <div v-else></div>
        
        <div class="text-center">
          <p class="text-sm text-gray-500">{{ currentEntryIndex + 1 }} dari {{ totalEntries }}</p>
        </div>
        
        <button
          v-if="nextEntry"
          @click="navigateToEntry(nextEntry.id)"
          class="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
        >
          <span class="text-sm">Selanjutnya</span>
          <ChevronRight class="w-4 h-4" />
        </button>
        <div v-else></div>
      </div>
    </div>

    <!-- Related Entries -->
    <div v-if="relatedEntries.length > 0" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h3 class="font-medium text-gray-900 mb-4">Jurnal Serupa</h3>
      <div class="space-y-3">
        <div
          v-for="relatedEntry in relatedEntries"
          :key="relatedEntry.id"
          @click="navigateToEntry(relatedEntry.id)"
          class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
            <span class="text-sm">{{ relatedEntry.mood.emoji }}</span>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900">{{ formatDate(relatedEntry.createdAt) }}</p>
            <p class="text-xs text-gray-500 line-clamp-1">{{ relatedEntry.excerpt }}</p>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </div>

    <!-- Menu Modal -->
    <div v-if="showMenu" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Opsi Jurnal</h3>
          <button @click="showMenu = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div class="space-y-2">
          <button
            @click="editEntry"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Edit class="w-5 h-5 text-blue-600" />
            <span class="text-gray-900">Edit Jurnal</span>
          </button>
          
          <button
            @click="shareEntry"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Share2 class="w-5 h-5 text-green-600" />
            <span class="text-gray-900">Bagikan</span>
          </button>
          
          <button
            @click="exportEntry"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Download class="w-5 h-5 text-purple-600" />
            <span class="text-gray-900">Ekspor</span>
          </button>
          
          <button
            @click="duplicateEntry"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Copy class="w-5 h-5 text-orange-600" />
            <span class="text-gray-900">Duplikat sebagai Template</span>
          </button>
          
          <button
            @click="deleteEntry"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-red-50 text-left"
          >
            <Trash2 class="w-5 h-5 text-red-600" />
            <span class="text-red-900">Hapus</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!entry" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Loader class="w-6 h-6 text-purple-600 animate-spin" />
        </div>
        <p class="text-gray-600">Memuat jurnal...</p>
      </div>
    </div>

    <!-- Entry Not Found -->
    <div v-if="!entry && !loading" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <BookOpen class="w-8 h-8 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Jurnal Tidak Ditemukan</h3>
      <p class="text-gray-500 text-sm mb-4">Jurnal yang Anda cari mungkin telah dihapus atau tidak ada</p>
      <button
        @click="goBack"
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
      >
        Kembali ke Daftar Jurnal
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  ArrowLeft,
  Bookmark,
  MoreVertical,
  Lightbulb,
  Edit,
  Share2,
  Download,
  Copy,
  Trash2,
  X,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Loader,
  Heart,
  Smile,
  Zap,
  Coffee,
  Sunset,
  Target
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Route
const route = useRoute()
const entryId = route.params.id

// Data
const entry = ref(null)
const showMenu = ref(false)
const loading = ref(true)
const allEntries = ref([])

// Computed
const currentEntryIndex = computed(() => {
  if (!entry.value || !allEntries.value.length) return -1
  return allEntries.value.findIndex(e => e.id == entry.value.id)
})

const totalEntries = computed(() => allEntries.value.length)

const previousEntry = computed(() => {
  const index = currentEntryIndex.value
  if (index > 0) {
    return allEntries.value[index - 1]
  }
  return null
})

const nextEntry = computed(() => {
  const index = currentEntryIndex.value
  if (index < allEntries.value.length - 1) {
    return allEntries.value[index + 1]
  }
  return null
})

const relatedEntries = computed(() => {
  if (!entry.value || !allEntries.value.length) return []
  
  // Find entries with same mood or similar tags
  return allEntries.value
    .filter(e => 
      e.id !== entry.value.id && 
      (e.mood.value === entry.value.mood.value || 
       e.tags.some(tag => entry.value.tags.includes(tag)))
    )
    .slice(0, 3)
})

// Methods
const formatDate = (date) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date(date))
}

const formatDetailedDate = (date) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

const getTimeAgo = (date) => {
  if (!date) return ''
  const now = new Date()
  const entryDate = new Date(date)
  const diffTime = Math.abs(now - entryDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) {
    return 'Hari ini'
  } else if (diffDays === 2) {
    return 'Kemarin'
  } else if (diffDays <= 7) {
    return `${diffDays - 1} hari lalu`
  } else if (diffDays <= 30) {
    return `${Math.ceil(diffDays / 7)} minggu lalu`
  } else {
    return `${Math.ceil(diffDays / 30)} bulan lalu`
  }
}

const formatContent = (content) => {
  if (!content) return ''
  
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^## (.*$)/gim, '<h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">$1</h3>')
    .replace(/^# (.*$)/gim, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
    .replace(/^- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^(\d+)\. (.*$)/gim, '<li class="ml-4 list-decimal">$2</li>')
    .replace(/\n\n/g, '</p><p class="mt-4">')
    .replace(/\n/g, '<br>')
}

const toggleBookmark = () => {
  if (!entry.value) return
  
  entry.value.bookmarked = !entry.value.bookmarked
  
  // Save to localStorage
  const existingEntries = JSON.parse(localStorage.getItem('journal-entries') || '[]')
  const entryIndex = existingEntries.findIndex(e => e.id == entry.value.id)
  if (entryIndex > -1) {
    existingEntries[entryIndex].bookmarked = entry.value.bookmarked
    localStorage.setItem('journal-entries', JSON.stringify(existingEntries))
  }
}

const editEntry = () => {
  showMenu.value = false
  navigateTo(`/application/journal/edit/${entry.value.id}`)
}

const shareEntry = () => {
  showMenu.value = false
  
  if (navigator.share) {
    navigator.share({
      title: `Jurnal: ${formatDate(entry.value.createdAt)}`,
      text: entry.value.excerpt
    })
  } else {
    // Fallback: copy to clipboard
    const content = `Jurnal: ${formatDate(entry.value.createdAt)}\n\n${entry.value.content}`
    navigator.clipboard.writeText(content).then(() => {
      alert('Jurnal berhasil disalin ke clipboard!')
    })
  }
}

const exportEntry = () => {
  showMenu.value = false
  
  const content = `# Jurnal - ${formatDate(entry.value.createdAt)}\n\n**Mood:** ${entry.value.mood.emoji} ${entry.value.mood.label}\n\n${entry.value.content}\n\n**Tags:** ${entry.value.tags.join(', ')}`
  
  const element = document.createElement('a')
  const file = new Blob([content], { type: 'text/plain' })
  element.href = URL.createObjectURL(file)
  element.download = `jurnal-${formatDate(entry.value.createdAt).replace(/\s/g, '-')}.txt`
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}

const duplicateEntry = () => {
  showMenu.value = false
  
  // Create URL with pre-filled content
  const params = new URLSearchParams({
    template: 'duplicate',
    content: entry.value.content,
    mood: entry.value.mood.value,
    tags: entry.value.tags.join(',')
  })
  
  navigateTo(`/application/journal/create?${params.toString()}`)
}

const deleteEntry = () => {
  showMenu.value = false
  
  if (confirm('Apakah Anda yakin ingin menghapus jurnal ini?')) {
    const existingEntries = JSON.parse(localStorage.getItem('journal-entries') || '[]')
    const filteredEntries = existingEntries.filter(e => e.id != entry.value.id)
    localStorage.setItem('journal-entries', JSON.stringify(filteredEntries))
    
    navigateTo('/application/journal')
  }
}

const navigateToEntry = (id) => {
  navigateTo(`/application/journal/view/${id}`)
}

const goBack = () => {
  navigateTo('/application/journal')
}

// Lifecycle
onMounted(async () => {
  try {
    // Load all entries
    const savedEntries = localStorage.getItem('journal-entries')
    if (savedEntries) {
      allEntries.value = JSON.parse(savedEntries).map(entry => ({
        ...entry,
        createdAt: new Date(entry.createdAt),
        updatedAt: entry.updatedAt ? new Date(entry.updatedAt) : new Date(entry.createdAt)
      })).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    }
    
    // Find the specific entry
    const foundEntry = allEntries.value.find(e => e.id == entryId)
    
    if (foundEntry) {
      entry.value = foundEntry
    }
    
    loading.value = false
  } catch (error) {
    console.error('Failed to load entry:', error)
    loading.value = false
  }
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prose p {
  margin-bottom: 1rem;
}

.prose h2, .prose h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.prose li {
  margin-bottom: 0.25rem;
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 