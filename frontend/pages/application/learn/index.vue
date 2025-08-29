<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-green-500 to-blue-500 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold mb-1">Pusat Pembelajaran</h1>
          <p class="text-green-100 text-sm">Artikel dan panduan untuk kesehatan mental</p>
        </div>
        <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
          <BookOpen class="w-6 h-6 text-white" />
        </div>
      </div>
      
      <!-- Reading Stats -->
      <div class="grid grid-cols-3 gap-4 mt-4 text-sm">
        <div class="text-center">
          <p class="text-2xl font-bold">{{ readingStats.articlesRead }}</p>
          <p class="text-green-100 text-xs">Artikel Dibaca</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ readingStats.timeSpent }}</p>
          <p class="text-green-100 text-xs">Menit Belajar</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ readingStats.bookmarked }}</p>
          <p class="text-green-100 text-xs">Disimpan</p>
        </div>
      </div>
    </div>

    <!-- Recommended for You -->
    <div v-if="recommendedArticles.length > 0" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Rekomendasi untuk Anda</h2>
        <div class="flex items-center space-x-1 text-sm text-purple-600">
          <Sparkles class="w-4 h-4" />
          <span>AI Powered</span>
        </div>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="article in recommendedArticles.slice(0, 2)" 
          :key="article.id"
          @click="readArticle(article)"
          class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" :class="article.iconBg">
            <component :is="article.icon" class="w-6 h-6" :class="article.iconColor" />
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-900 mb-1">{{ article.title }}</h3>
            <p class="text-xs text-gray-600 mb-2">{{ article.excerpt }}</p>
            <div class="flex items-center space-x-3 text-xs text-gray-500">
              <span class="bg-purple-100 text-purple-700 px-2 py-1 rounded-full">{{ article.category }}</span>
              <span>{{ article.readTime }} min</span>
              <span>{{ article.difficulty }}</span>
            </div>
          </div>
          <button 
            @click.stop="toggleBookmark(article)"
            :class="[
              'p-1 rounded hover:bg-gray-200 transition-colors',
              article.bookmarked ? 'text-purple-600' : 'text-gray-400'
            ]"
          >
            <Bookmark class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Categories -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Kategori Artikel</h2>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="category in categories"
          :key="category.id"
          @click="activeCategory = category.id"
          :class="[
            'flex flex-col items-center p-4 rounded-xl transition-colors',
            activeCategory === category.id
              ? 'bg-purple-50 border-2 border-purple-200'
              : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
          ]"
        >
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center mb-2', category.iconBg]">
            <component :is="category.icon" class="w-5 h-5" :class="category.iconColor" />
          </div>
          <span class="text-sm font-medium text-gray-900">{{ category.name }}</span>
          <span class="text-xs text-gray-500">{{ category.articleCount }} artikel</span>
        </button>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-3 mb-4">
        <div class="flex-1 relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            placeholder="Cari artikel atau topik..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <button
          @click="showFilter = !showFilter"
          class="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <Filter class="w-4 h-4 text-gray-600" />
        </button>
      </div>
      
      <!-- Filter Options -->
      <div v-if="showFilter" class="flex flex-wrap gap-2">
        <button
          v-for="filter in filters"
          :key="filter.key"
          @click="toggleFilter(filter.key)"
          :class="[
            'px-3 py-1 rounded-full text-sm transition-colors',
            activeFilters.includes(filter.key)
              ? 'bg-purple-100 text-purple-700'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <!-- Article Cards -->
    <div class="space-y-4">
      <div
        v-for="article in filteredArticles"
        :key="article.id"
        @click="readArticle(article)"
        class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
      >
        <div class="flex items-start space-x-4">
          <!-- Article Thumbnail -->
          <div class="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0" :class="article.iconBg">
            <component :is="article.icon" class="w-8 h-8" :class="article.iconColor" />
          </div>
          
          <!-- Article Info -->
          <div class="flex-1">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1 pr-4">
                <h3 class="font-bold text-gray-900 text-lg mb-1">{{ article.title }}</h3>
                <p class="text-sm text-gray-600 mb-2 line-clamp-2">{{ article.excerpt }}</p>
                
                <!-- Article Meta -->
                <div class="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                  <div class="flex items-center space-x-1">
                    <Clock class="w-3 h-3" />
                    <span>{{ article.readTime }} min baca</span>
                  </div>
                  <div class="flex items-center space-x-1">
                    <Eye class="w-3 h-3" />
                    <span>{{ article.views.toLocaleString() }} views</span>
                  </div>
                  <div class="flex items-center space-x-1">
                    <Star class="w-3 h-3" />
                    <span>{{ article.rating }}/5</span>
                  </div>
                </div>
                
                <!-- Tags -->
                <div class="flex flex-wrap gap-1 mb-2">
                  <span
                    v-for="tag in article.tags.slice(0, 3)"
                    :key="tag"
                    class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              
              <!-- Bookmark Button -->
              <button 
                @click.stop="toggleBookmark(article)"
                :class="[
                  'p-2 rounded-lg hover:bg-gray-100 transition-colors',
                  article.bookmarked ? 'text-purple-600' : 'text-gray-400'
                ]"
              >
                <Bookmark class="w-5 h-5" />
              </button>
            </div>
            
            <!-- Category Badge -->
            <div class="flex items-center justify-between">
              <span :class="['px-3 py-1 rounded-full text-xs font-medium', getCategoryStyle(article.category)]">
                {{ article.category }}
              </span>
              <span class="text-xs text-gray-500">{{ formatDate(article.publishedAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bookmarked Articles -->
    <div v-if="bookmarkedArticles.length > 0" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Artikel Tersimpan</h2>
        <NuxtLink to="/application/learn/bookmarks" class="text-sm text-purple-600 hover:text-purple-700">
          Lihat Semua
        </NuxtLink>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="article in bookmarkedArticles.slice(0, 3)" 
          :key="article.id"
          @click="readArticle(article)"
          class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :class="article.iconBg">
            <component :is="article.icon" class="w-4 h-4" :class="article.iconColor" />
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-900">{{ article.title }}</h3>
            <p class="text-xs text-gray-500">{{ article.readTime }} min • {{ article.category }}</p>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredArticles.length === 0" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Search class="w-8 h-8 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Tidak ada artikel ditemukan</h3>
      <p class="text-gray-500 text-sm">Coba ubah kata kunci pencarian atau filter</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  BookOpen,
  Clock,
  Eye,
  Star,
  Search,
  Filter,
  Bookmark,
  ChevronRight,
  Sparkles,
  Heart,
  Shield,
  Brain,
  Smile,
  Moon,
  Users,
  Target,
  Lightbulb
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Data
const searchQuery = ref('')
const showFilter = ref(false)
const activeCategory = ref(1)
const activeFilters = ref([])

const readingStats = ref({
  articlesRead: 12,
  timeSpent: 85,
  bookmarked: 6
})

const categories = ref([
  { id: 1, name: 'Kecemasan', articleCount: 24, icon: Shield, iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  { id: 2, name: 'Depresi', articleCount: 18, icon: Heart, iconBg: 'bg-red-100', iconColor: 'text-red-600' },
  { id: 3, name: 'Stress', articleCount: 21, icon: Brain, iconBg: 'bg-purple-100', iconColor: 'text-purple-600' },
  { id: 4, name: 'Relaksasi', articleCount: 15, icon: Smile, iconBg: 'bg-green-100', iconColor: 'text-green-600' },
  { id: 5, name: 'Tidur', articleCount: 12, icon: Moon, iconBg: 'bg-indigo-100', iconColor: 'text-indigo-600' },
  { id: 6, name: 'Hubungan', articleCount: 19, icon: Users, iconBg: 'bg-pink-100', iconColor: 'text-pink-600' }
])

const filters = ref([
  { key: 'recent', label: 'Terbaru' },
  { key: 'popular', label: 'Populer' },
  { key: 'beginner', label: 'Pemula' },
  { key: 'intermediate', label: 'Menengah' },
  { key: 'expert', label: 'Ahli' },
  { key: 'bookmarked', label: 'Tersimpan' }
])

const articles = ref([
  {
    id: 1,
    title: 'Mengelola Kecemasan di Tempat Kerja',
    excerpt: 'Strategi praktis untuk mengatasi stress dan kecemasan saat bekerja, termasuk teknik pernapasan dan mindfulness.',
    category: 'Kecemasan',
    categoryId: 1,
    readTime: 5,
    views: 1245,
    rating: 4.8,
    difficulty: 'Pemula',
    bookmarked: true,
    publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    tags: ['workplace', 'breathing', 'mindfulness', 'stress'],
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    moodRelevance: ['anxious', 'stressed']
  },
  {
    id: 2,
    title: 'Teknik Pernapasan untuk Ketenangan',
    excerpt: 'Panduan lengkap berbagai teknik pernapasan yang mudah dipraktikkan untuk menenangkan pikiran dan tubuh.',
    category: 'Relaksasi',
    categoryId: 4,
    readTime: 3,
    views: 987,
    rating: 4.9,
    difficulty: 'Pemula',
    bookmarked: false,
    publishedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    tags: ['breathing', 'relaxation', 'meditation'],
    icon: Smile,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    moodRelevance: ['anxious', 'stressed', 'neutral']
  },
  {
    id: 3,
    title: 'Memahami dan Mengatasi Depresi',
    excerpt: 'Panduan komprehensif untuk memahami gejala depresi dan langkah-langkah untuk mengatasinya dengan dukungan profesional.',
    category: 'Depresi',
    categoryId: 2,
    readTime: 8,
    views: 2156,
    rating: 4.7,
    difficulty: 'Menengah',
    bookmarked: true,
    publishedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    tags: ['depression', 'therapy', 'support', 'mental health'],
    icon: Heart,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    moodRelevance: ['sad', 'hopeless']
  },
  {
    id: 4,
    title: 'Membangun Rutinitas Tidur yang Sehat',
    excerpt: 'Tips untuk meningkatkan kualitas tidur dan menciptakan rutinitas tidur yang mendukung kesehatan mental.',
    category: 'Tidur',
    categoryId: 5,
    readTime: 6,
    views: 1567,
    rating: 4.6,
    difficulty: 'Pemula',
    bookmarked: false,
    publishedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    tags: ['sleep', 'routine', 'hygiene', 'wellness'],
    icon: Moon,
    iconBg: 'bg-indigo-100',
    iconColor: 'text-indigo-600',
    moodRelevance: ['tired', 'stressed', 'neutral']
  },
  {
    id: 5,
    title: 'Mindfulness untuk Pemula',
    excerpt: 'Pengenalan praktik mindfulness sederhana yang dapat dilakukan sehari-hari untuk kesehatan mental.',
    category: 'Relaksasi',
    categoryId: 4,
    readTime: 4,
    views: 892,
    rating: 4.5,
    difficulty: 'Pemula',
    bookmarked: true,
    publishedAt: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000),
    tags: ['mindfulness', 'beginner', 'meditation', 'awareness'],
    icon: Smile,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    moodRelevance: ['anxious', 'neutral', 'stressed']
  },
  {
    id: 6,
    title: 'Mengatasi Konflik dalam Hubungan',
    excerpt: 'Strategi komunikasi yang sehat untuk menyelesaikan konflik dan membangun hubungan yang lebih kuat.',
    category: 'Hubungan',
    categoryId: 6,
    readTime: 7,
    views: 1334,
    rating: 4.4,
    difficulty: 'Menengah',
    bookmarked: false,
    publishedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    tags: ['relationships', 'communication', 'conflict resolution'],
    icon: Users,
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
    moodRelevance: ['angry', 'frustrated', 'sad']
  },
  {
    id: 7,
    title: 'Teknik Grounding untuk Serangan Panik',
    excerpt: 'Metode praktis untuk mengatasi serangan panik menggunakan teknik grounding 5-4-3-2-1 dan strategi lainnya.',
    category: 'Kecemasan',
    categoryId: 1,
    readTime: 4,
    views: 2045,
    rating: 4.9,
    difficulty: 'Menengah',
    bookmarked: true,
    publishedAt: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000),
    tags: ['panic attacks', 'grounding', 'anxiety', 'emergency'],
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    moodRelevance: ['anxious', 'panicked']
  },
  {
    id: 8,
    title: 'Self-Care Harian untuk Kesehatan Mental',
    excerpt: 'Rutinitas self-care sederhana yang dapat Anda lakukan setiap hari untuk menjaga kesehatan mental.',
    category: 'Stress',
    categoryId: 3,
    readTime: 5,
    views: 1123,
    rating: 4.3,
    difficulty: 'Pemula',
    bookmarked: false,
    publishedAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    tags: ['self-care', 'daily routine', 'wellness', 'mental health'],
    icon: Brain,
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
    moodRelevance: ['neutral', 'tired', 'stressed']
  }
])

// Computed
const filteredArticles = computed(() => {
  let filtered = articles.value

  // Filter by category
  if (activeCategory.value) {
    filtered = filtered.filter(article => article.categoryId === activeCategory.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(article =>
      article.title.toLowerCase().includes(query) ||
      article.excerpt.toLowerCase().includes(query) ||
      article.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // Filter by active filters
  if (activeFilters.value.length > 0) {
    filtered = filtered.filter(article => {
      return activeFilters.value.every(filter => {
        switch (filter) {
          case 'recent': return true // Sort by date instead
          case 'popular': return article.views > 1000
          case 'beginner': return article.difficulty === 'Pemula'
          case 'intermediate': return article.difficulty === 'Menengah'
          case 'expert': return article.difficulty === 'Ahli'
          case 'bookmarked': return article.bookmarked
          default: return true
        }
      })
    })
  }

  // Sort by filters
  if (activeFilters.value.includes('recent')) {
    filtered = filtered.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt))
  } else if (activeFilters.value.includes('popular')) {
    filtered = filtered.sort((a, b) => b.views - a.views)
  }

  return filtered
})

const bookmarkedArticles = computed(() => {
  return articles.value.filter(article => article.bookmarked)
})

const recommendedArticles = computed(() => {
  // Get user's recent mood from localStorage
  const recentMood = localStorage.getItem('recent-mood') || 'neutral'
  
  // Filter articles based on mood relevance
  const relevant = articles.value.filter(article => 
    article.moodRelevance && article.moodRelevance.includes(recentMood)
  ).sort((a, b) => b.rating - a.rating)
  
  return relevant.slice(0, 3)
})

// Methods
const readArticle = (article) => {
  navigateTo(`/application/learn/article/${article.id}`)
}

const toggleBookmark = (article) => {
  article.bookmarked = !article.bookmarked
  
  // Update reading stats
  if (article.bookmarked) {
    readingStats.value.bookmarked++
  } else {
    readingStats.value.bookmarked--
  }
  
  // Save to localStorage
  const bookmarks = bookmarkedArticles.value.map(a => a.id)
  localStorage.setItem('mindcare-bookmarks', JSON.stringify(bookmarks))
}

const toggleFilter = (filterKey) => {
  const index = activeFilters.value.indexOf(filterKey)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(filterKey)
  }
}

const getCategoryStyle = (category) => {
  const styles = {
    'Kecemasan': 'bg-blue-100 text-blue-800',
    'Depresi': 'bg-red-100 text-red-800',
    'Stress': 'bg-purple-100 text-purple-800',
    'Relaksasi': 'bg-green-100 text-green-800',
    'Tidur': 'bg-indigo-100 text-indigo-800',
    'Hubungan': 'bg-pink-100 text-pink-800'
  }
  return styles[category] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'Kemarin'
  if (diffDays < 7) return `${diffDays} hari lalu`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} minggu lalu`
  return `${Math.floor(diffDays / 30)} bulan lalu`
}

// Lifecycle
onMounted(() => {
  // Load bookmarks from localStorage
  const savedBookmarks = JSON.parse(localStorage.getItem('mindcare-bookmarks') || '[]')
  articles.value.forEach(article => {
    if (savedBookmarks.includes(article.id)) {
      article.bookmarked = true
    }
  })
  
  // Update reading stats based on bookmarks
  readingStats.value.bookmarked = savedBookmarks.length
})
</script>

<style scoped>
/* Line clamp for excerpt text */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth transitions */
.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease;
}

.transition-shadow {
  transition: box-shadow 0.2s ease;
}

/* Custom scrollbar for article list */
@media (max-width: 768px) {
  ::-webkit-scrollbar {
    display: none;
  }
}
</style> 