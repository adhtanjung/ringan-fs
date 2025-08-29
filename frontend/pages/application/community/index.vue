<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-pink-500 to-purple-500 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold mb-1">Komunitas</h1>
          <p class="text-pink-100 text-sm">Ruang aman untuk berbagi dan saling mendukung</p>
        </div>
        <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
          <Heart class="w-6 h-6 text-white" />
        </div>
      </div>
      
      <!-- Community Stats -->
      <div class="grid grid-cols-3 gap-4 mt-4 text-sm">
        <div class="text-center">
          <p class="text-2xl font-bold">{{ communityStats.totalMembers }}</p>
          <p class="text-pink-100 text-xs">Anggota Aktif</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ communityStats.dailyPosts }}</p>
          <p class="text-pink-100 text-xs">Post Hari Ini</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ communityStats.hugsGiven }}</p>
          <p class="text-pink-100 text-xs">Pelukan Diberikan</p>
        </div>
      </div>
    </div>

    <!-- Community Guidelines -->
    <div class="bg-blue-50 rounded-2xl p-4 border-l-4 border-blue-400">
      <div class="flex items-start space-x-3">
        <Shield class="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div>
          <h3 class="font-medium text-blue-900 mb-1">Pedoman Komunitas</h3>
          <p class="text-blue-700 text-sm">Hormati privasi, berikan dukungan positif, hindari diagnosis medis. <button class="underline hover:no-underline">Baca selengkapnya</button></p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="grid grid-cols-2 gap-3">
        <button
          @click="showCreatePost = true"
          class="flex items-center justify-center p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors group"
        >
          <div class="flex items-center space-x-2">
            <Plus class="w-5 h-5 text-purple-600" />
            <span class="text-sm font-medium text-gray-900">Posting Anonim</span>
          </div>
        </button>
        
        <button
          @click="activeTab = 'groups'"
          class="flex items-center justify-center p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors group"
        >
          <div class="flex items-center space-x-2">
            <Users class="w-5 h-5 text-green-600" />
            <span class="text-sm font-medium text-gray-900">Grup Dukungan</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Forum Categories -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Ruang Diskusi</h2>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="category in forumCategories"
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
          <span class="text-xs text-gray-500">{{ category.postCount }} post</span>
        </button>
      </div>
    </div>

    <!-- Posts Feed -->
    <div class="space-y-4">
      <div
        v-for="post in filteredPosts"
        :key="post.id"
        class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200"
      >
        <!-- Post Header -->
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
            <span class="text-white font-bold text-sm">{{ post.author.anonymous ? '🎭' : post.author.name.charAt(0) }}</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center space-x-2">
              <h3 class="font-medium text-gray-900">{{ post.author.anonymous ? 'Anonim' : post.author.name }}</h3>
              <span :class="['px-2 py-0.5 text-xs rounded-full', getCategoryStyle(post.category)]">
                {{ post.category }}
              </span>
            </div>
            <p class="text-xs text-gray-500">{{ formatTimeAgo(post.createdAt) }}</p>
          </div>
          <button @click="reportPost(post)" class="p-1 hover:bg-gray-100 rounded">
            <Flag class="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <!-- Post Content -->
        <div class="mb-4">
          <p class="text-gray-700 text-sm leading-relaxed">{{ post.content }}</p>
          
          <!-- Mood Indicator -->
          <div v-if="post.mood" class="flex items-center space-x-2 mt-3 p-2 bg-gray-50 rounded-lg">
            <span class="text-lg">{{ getMoodEmoji(post.mood) }}</span>
            <span class="text-xs text-gray-600">Perasaan: {{ post.mood }}</span>
          </div>
          
          <!-- Post Tags -->
          <div v-if="post.tags.length > 0" class="flex flex-wrap gap-2 mt-3">
            <span
              v-for="tag in post.tags"
              :key="tag"
              class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
            >
              #{{ tag }}
            </span>
          </div>
        </div>

        <!-- Post Actions -->
        <div class="flex items-center justify-between pt-3 border-t border-gray-100">
          <div class="flex items-center space-x-4">
            <button
              @click="toggleHug(post)"
              :class="[
                'flex items-center space-x-1 transition-colors',
                post.hugged ? 'text-pink-500' : 'text-gray-500 hover:text-pink-500'
              ]"
            >
              <span class="text-lg">🤗</span>
              <span class="text-sm">{{ post.hugs }}</span>
            </button>
            
            <button
              @click="toggleComment(post)"
              class="flex items-center space-x-1 text-gray-500 hover:text-blue-500 transition-colors"
            >
              <MessageCircle class="w-4 h-4" />
              <span class="text-sm">{{ post.comments }}</span>
            </button>
            
            <button 
              @click="supportPost(post)"
              class="flex items-center space-x-1 text-gray-500 hover:text-green-500 transition-colors"
            >
              <Heart class="w-4 h-4" />
              <span class="text-sm">Dukung</span>
            </button>
          </div>
          
          <button 
            @click="viewPost(post)"
            class="text-xs text-gray-500 hover:text-gray-700"
          >
            Balas
          </button>
        </div>
      </div>
    </div>

    <!-- Create Post Modal -->
    <div v-if="showCreatePost" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Bagikan Perasaan Anda</h3>
          <button @click="showCreatePost = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <form @submit.prevent="createPost" class="space-y-4">
          <!-- Anonymous Toggle -->
          <div class="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
            <div class="flex items-center space-x-2">
              <span class="text-lg">🎭</span>
              <span class="text-sm font-medium text-gray-900">Posting sebagai anonim</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="newPost.anonymous" type="checkbox" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
          
          <!-- Category Selection -->
          <select
            v-model="newPost.category"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          >
            <option value="">Pilih kategori...</option>
            <option v-for="category in forumCategories" :key="category.id" :value="category.name">
              {{ category.name }}
            </option>
          </select>
          
          <!-- Mood Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Bagaimana perasaan Anda?</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="mood in moods"
                :key="mood.value"
                type="button"
                @click="newPost.mood = mood.value"
                :class="[
                  'p-2 rounded-lg text-center transition-colors',
                  newPost.mood === mood.value
                    ? 'bg-purple-100 border-2 border-purple-500'
                    : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                ]"
              >
                <div class="text-lg mb-1">{{ mood.emoji }}</div>
                <div class="text-xs text-gray-600">{{ mood.label }}</div>
              </button>
            </div>
          </div>
          
          <textarea
            v-model="newPost.content"
            placeholder="Ceritakan apa yang Anda rasakan... Ingat, ini adalah ruang yang aman dan mendukung."
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            required
          ></textarea>
          
          <input
            v-model="newPost.tags"
            placeholder="Tag (pisahkan dengan koma) - opsional"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          
          <div class="flex space-x-3">
            <button
              type="button"
              @click="showCreatePost = false"
              class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Batal
            </button>
            <button
              type="submit"
              class="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
            >
              Bagikan
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Heart,
  Users,
  Plus,
  MessageCircle,
  Shield,
  Flag,
  X,
  Brain,
  Smile,
  Moon,
  Target,
  BookOpen
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Data
const activeCategory = ref(1)
const showCreatePost = ref(false)

const communityStats = ref({
  totalMembers: 1247,
  dailyPosts: 23,
  hugsGiven: 156
})

const forumCategories = ref([
  { id: 1, name: 'Kecemasan', postCount: 45, icon: Shield, iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  { id: 2, name: 'Depresi', postCount: 32, icon: Heart, iconBg: 'bg-red-100', iconColor: 'text-red-600' },
  { id: 3, name: 'Stress', postCount: 28, icon: Brain, iconBg: 'bg-purple-100', iconColor: 'text-purple-600' },
  { id: 4, name: 'Hubungan', postCount: 19, icon: Users, iconBg: 'bg-pink-100', iconColor: 'text-pink-600' },
  { id: 5, name: 'Tidur', postCount: 15, icon: Moon, iconBg: 'bg-indigo-100', iconColor: 'text-indigo-600' },
  { id: 6, name: 'Motivasi', postCount: 21, icon: Target, iconBg: 'bg-green-100', iconColor: 'text-green-600' }
])

const moods = ref([
  { value: 'anxious', label: 'Cemas', emoji: '😰' },
  { value: 'sad', label: 'Sedih', emoji: '😢' },
  { value: 'stressed', label: 'Stress', emoji: '😫' },
  { value: 'hopeful', label: 'Berharap', emoji: '🙏' },
  { value: 'grateful', label: 'Bersyukur', emoji: '🙏' },
  { value: 'neutral', label: 'Biasa', emoji: '😐' }
])

const newPost = ref({
  content: '',
  category: '',
  mood: '',
  tags: '',
  anonymous: true
})

const posts = ref([
  {
    id: 1,
    content: 'Hari ini saya merasa sangat cemas tentang presentasi besok. Jantung saya berdebar-debar dan sulit tidur. Ada yang punya tips untuk mengatasi kecemasan sebelum presentasi?',
    author: { name: 'Sarah', anonymous: true },
    category: 'Kecemasan',
    mood: 'anxious',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    hugs: 12,
    comments: 8,
    hugged: false,
    tags: ['presentasi', 'kecemasan', 'tidur']
  },
  {
    id: 2,
    content: 'Terima kasih untuk semua dukungan kemarin. Hari ini saya merasa sedikit lebih baik. Teknik pernapasan yang kalian sarankan sangat membantu. 💙',
    author: { name: 'Alex', anonymous: false },
    category: 'Motivasi',
    mood: 'grateful',
    createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    hugs: 24,
    comments: 15,
    hugged: true,
    tags: ['terima kasih', 'pernapasan', 'recovery']
  },
  {
    id: 3,
    content: 'Sudah 3 minggu ini saya susah sekali tidur. Pikiran terus berputar tentang pekerjaan dan kehidupan. Rasanya seperti lingkaran setan. Ada yang mengalami hal serupa?',
    author: { name: 'Anonymous', anonymous: true },
    category: 'Tidur',
    mood: 'stressed',
    createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    hugs: 18,
    comments: 12,
    hugged: false,
    tags: ['insomnia', 'overthinking', 'pekerjaan']
  }
])

// Computed
const filteredPosts = computed(() => {
  if (activeCategory.value === null) return posts.value
  
  const categoryName = forumCategories.value.find(cat => cat.id === activeCategory.value)?.name
  return posts.value.filter(post => post.category === categoryName)
})

// Methods
const formatTimeAgo = (date) => {
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days} hari lalu`
  if (hours > 0) return `${hours} jam lalu`
  return 'Baru saja'
}

const getCategoryStyle = (category) => {
  const styles = {
    'Kecemasan': 'bg-blue-100 text-blue-800',
    'Depresi': 'bg-red-100 text-red-800',
    'Stress': 'bg-purple-100 text-purple-800',
    'Hubungan': 'bg-pink-100 text-pink-800',
    'Tidur': 'bg-indigo-100 text-indigo-800',
    'Motivasi': 'bg-green-100 text-green-800'
  }
  return styles[category] || 'bg-gray-100 text-gray-800'
}

const getMoodEmoji = (mood) => {
  const moodMap = {
    'anxious': '😰',
    'sad': '😢',
    'stressed': '😫',
    'hopeful': '🙏',
    'grateful': '🙏',
    'neutral': '😐'
  }
  return moodMap[mood] || '😐'
}

const toggleHug = (post) => {
  post.hugged = !post.hugged
  post.hugs += post.hugged ? 1 : -1
}

const toggleComment = (post) => {
  navigateTo(`/application/community/post/${post.id}`)
}

const supportPost = (post) => {
  // Add support reaction
  console.log('Supporting post:', post.id)
}

const viewPost = (post) => {
  navigateTo(`/application/community/post/${post.id}`)
}

const reportPost = (post) => {
  // Report post for moderation
  console.log('Reporting post:', post.id)
}

const createPost = () => {
  if (!newPost.value.content.trim() || !newPost.value.category) return
  
  const post = {
    id: Date.now(),
    content: newPost.value.content,
    author: { 
      name: newPost.value.anonymous ? 'Anonymous' : 'Anda', 
      anonymous: newPost.value.anonymous 
    },
    category: newPost.value.category,
    mood: newPost.value.mood,
    createdAt: new Date(),
    hugs: 0,
    comments: 0,
    hugged: false,
    tags: newPost.value.tags ? newPost.value.tags.split(',').map(tag => tag.trim()) : []
  }
  
  posts.value.unshift(post)
  
  // Reset form
  newPost.value = { content: '', category: '', mood: '', tags: '', anonymous: true }
  showCreatePost.value = false
}
</script>

<style scoped>
.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease;
}

.fixed.inset-0 {
  backdrop-filter: blur(4px);
}

/* Custom toggle switch styling */
input[type="checkbox"]:checked + div {
  background-color: #9333ea;
}
</style> 