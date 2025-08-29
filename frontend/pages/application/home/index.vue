<template>
  <div class="space-y-6">
    <!-- Welcome Section -->
    <div class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold mb-1">Halo, {{ userName }}! 👋</h1>
          <p class="text-purple-100 text-sm">{{ getGreetingMessage() }}</p>
        </div>
        <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
          <Heart class="w-6 h-6 text-white" />
        </div>
      </div>
      <div class="mt-4 flex items-center space-x-2 text-sm">
        <div class="flex items-center space-x-1">
          <Calendar class="w-4 h-4" />
          <span>{{ currentDate }}</span>
        </div>
        <div class="text-purple-200">•</div>
        <div class="flex items-center space-x-1">
          <Sun class="w-4 h-4" />
          <span>{{ getTimeOfDay() }}</span>
        </div>
      </div>
    </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Aksi Cepat</h2>
      <div class="grid grid-cols-1 gap-3">
        <NuxtLink
          to="/application/assessment"
          class="flex items-center p-4 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors group"
        >
          <div class="w-12 h-12 bg-blue-100 group-hover:bg-blue-200 rounded-full flex items-center justify-center mr-4">
            <ClipboardCheck class="w-6 h-6 text-blue-600" />
          </div>
          <div class="flex-1">
            <h3 class="font-medium text-gray-900">Self-Assess</h3>
            <p class="text-sm text-gray-600">Evaluasi kesehatan mental Anda</p>
          </div>
        </NuxtLink>

        <NuxtLink
          to="/application/chatbot"
          class="flex items-center p-4 rounded-xl bg-green-50 hover:bg-green-100 transition-colors group"
        >
          <div class="w-12 h-12 bg-green-100 group-hover:bg-green-200 rounded-full flex items-center justify-center mr-4">
            <MessageCircle class="w-6 h-6 text-green-600" />
          </div>
          <div class="flex-1">
            <h3 class="font-medium text-gray-900">Talk to AI</h3>
            <p class="text-sm text-gray-600">Berbicara dengan AI counselor</p>
          </div>
        </NuxtLink>

        <button
          @click="openJournal"
          class="flex items-center p-4 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors group"
        >
          <div class="w-12 h-12 bg-purple-100 group-hover:bg-purple-200 rounded-full flex items-center justify-center mr-4">
            <BookOpen class="w-6 h-6 text-purple-600" />
          </div>
          <div class="flex-1">
            <h3 class="font-medium text-gray-900">Journal</h3>
            <p class="text-sm text-gray-600">Tulis jurnal perasaan Anda</p>
          </div>
        </button>
      </div>
    </div>
    <!-- Daily Mood Check-in -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h2 class="text-lg font-bold text-gray-900 mb-4">Bagaimana perasaan Anda hari ini?</h2>
      
      <!-- Mood Emoji Slider -->
      <div class="relative mb-6">
        <div class="flex justify-between items-center mb-3">
          <span class="text-2xl">😔</span>
          <span class="text-2xl">😐</span>
          <span class="text-2xl">🙂</span>
          <span class="text-2xl">😊</span>
          <span class="text-2xl">😁</span>
        </div>
        <input
          v-model="todayMood"
          @input="updateMoodSlider"
          type="range"
          min="1"
          max="5"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mood-slider"
        />
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Sangat Buruk</span>
          <span>Sangat Baik</span>
        </div>
      </div>

      <div v-if="todayMood" class="text-center mb-4">
        <div class="text-4xl mb-2">{{ getMoodEmoji(todayMood) }}</div>
        <p class="text-sm text-gray-600">{{ getMoodLabel(todayMood) }}</p>
      </div>

      <button
        @click="saveMoodCheckIn"
        :disabled="!todayMood || moodSaved"
        :class="[
          'w-full py-3 px-4 rounded-lg font-medium transition-colors',
          moodSaved 
            ? 'bg-green-100 text-green-700 cursor-not-allowed'
            : todayMood
            ? 'bg-purple-600 hover:bg-purple-700 text-white'
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        ]"
      >
        {{ moodSaved ? '✓ Mood tersimpan' : 'Simpan Mood Hari Ini' }}
      </button>
    </div>

    <!-- 7-Day Mood Trends -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Tren Mood 7 Hari</h2>
        <TrendingUp class="w-5 h-5 text-gray-400" />
      </div>
      
      <!-- Simple Line Chart Representation -->
      <div class="space-y-3">
        <div v-for="(day, index) in moodHistory" :key="index" class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-500 w-12">{{ day.day }}</span>
            <span class="text-lg">{{ getMoodEmoji(day.mood) }}</span>
            <span class="text-sm text-gray-600">{{ getMoodLabel(day.mood) }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-20 bg-gray-200 rounded-full h-2">
              <div 
                :class="[
                  'h-2 rounded-full transition-all duration-300',
                  day.mood >= 4 ? 'bg-green-500' : day.mood >= 3 ? 'bg-yellow-500' : 'bg-red-500'
                ]"
                :style="{ width: `${day.mood * 20}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-400">{{ day.mood }}/5</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Suggested Articles -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Artikel Untuk Anda</h2>
        <NuxtLink to="/application/learn" class="text-sm text-purple-600 hover:text-purple-700">
          Lihat Semua
        </NuxtLink>
      </div>
      
      <div class="space-y-3">
        <div v-for="article in suggestedArticles" :key="article.id" class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="article.iconBg">
            <component :is="article.icon" class="w-5 h-5" :class="article.iconColor" />
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-900 mb-1">{{ article.title }}</h3>
            <p class="text-xs text-gray-600">{{ article.description }}</p>
            <div class="flex items-center space-x-2 mt-2">
              <span class="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">{{ article.category }}</span>
              <span class="text-xs text-gray-400">{{ article.readTime }} min</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Daily Nudge -->
    <div v-if="showDailyNudge" class="bg-gradient-to-r from-orange-400 to-pink-400 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h3 class="font-bold mb-2">{{ dailyNudge.title }}</h3>
          <p class="text-sm text-orange-100">{{ dailyNudge.message }}</p>
        </div>
        <button @click="dismissNudge" class="p-2 hover:bg-white/20 rounded-full">
          <X class="w-5 h-5" />
        </button>
      </div>
      <button
        @click="handleNudgeAction"
        class="mt-4 bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        {{ dailyNudge.actionText }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Heart, 
  Calendar, 
  Sun, 
  TrendingUp, 
  ClipboardCheck, 
  MessageCircle, 
  BookOpen,
  Lightbulb,
  Shield,
  Smile,
  X
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Reactive data
const userName = ref('Sarah')
const currentDate = ref('')
const todayMood = ref(0)
const moodSaved = ref(false)
const showDailyNudge = ref(true)

const moodHistory = ref([
  { day: 'Sen', mood: 3 },
  { day: 'Sel', mood: 4 },
  { day: 'Rab', mood: 2 },
  { day: 'Kam', mood: 3 },
  { day: 'Jum', mood: 4 },
  { day: 'Sab', mood: 5 },
  { day: 'Min', mood: 3 }
])

const suggestedArticles = ref([
  {
    id: 1,
    title: 'Mengelola Kecemasan di Tempat Kerja',
    description: 'Tips praktis untuk mengatasi stress dan kecemasan saat bekerja',
    category: 'Kecemasan',
    readTime: 5,
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    id: 2,
    title: 'Teknik Pernapasan untuk Ketenangan',
    description: 'Panduan lengkap teknik pernapasan yang mudah dipraktikkan',
    category: 'Relaksasi',
    readTime: 3,
    icon: Smile,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    id: 3,
    title: 'Membangun Rutinitas Tidur yang Sehat',
    description: 'Cara meningkatkan kualitas tidur untuk kesehatan mental',
    category: 'Tidur',
    readTime: 7,
    icon: Lightbulb,
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600'
  }
])

const dailyNudge = ref({
  title: '🌟 Jangan lupa diri sendiri!',
  message: 'Anda sudah melakukan hal-hal hebat hari ini. Bagaimana kalau meluangkan 5 menit untuk bernapas dalam-dalam?',
  actionText: 'Mulai Relaksasi'
})

// Methods
const getGreetingMessage = () => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Semoga pagi Anda menyenangkan!'
  if (hour < 17) return 'Semoga siang Anda produktif!'
  return 'Semoga malam Anda tenang!'
}

const getTimeOfDay = () => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Pagi'
  if (hour < 17) return 'Siang'
  return 'Malam'
}

const getMoodEmoji = (mood) => {
  const emojis = ['', '😔', '😐', '🙂', '😊', '😁']
  return emojis[mood] || '😐'
}

const getMoodLabel = (mood) => {
  const labels = ['', 'Sangat Buruk', 'Buruk', 'Biasa', 'Baik', 'Sangat Baik']
  return labels[mood] || 'Biasa'
}

const updateMoodSlider = () => {
  // Real-time feedback when slider moves
}

const saveMoodCheckIn = () => {
  if (!todayMood.value) return
  
  // Save mood to storage/API
  moodSaved.value = true
  
  // Update today's mood in history
  const today = new Date().toLocaleDateString('id-ID', { weekday: 'short' })
  const todayIndex = moodHistory.value.findIndex(day => day.day === today.slice(0, 3))
  if (todayIndex !== -1) {
    moodHistory.value[todayIndex].mood = parseInt(todayMood.value)
  }
  
  // Show success message
  setTimeout(() => {
    // Could show a toast or update UI
  }, 1000)
}

const openJournal = () => {
  // Navigate to journal or open modal
  navigateTo('/application/journal')
}

const dismissNudge = () => {
  showDailyNudge.value = false
}

const handleNudgeAction = () => {
  // Handle nudge action - could open breathing exercise, etc.
  navigateTo('/application/chatbot?mode=relax')
}

// Lifecycle
onMounted(() => {
  currentDate.value = new Date().toLocaleDateString('id-ID', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
  
  // Check if mood already saved today
  const savedMood = localStorage.getItem(`mood-${new Date().toDateString()}`)
  if (savedMood) {
    todayMood.value = parseInt(savedMood)
    moodSaved.value = true
  }
  
  // Set up gentle nudges timing
  setTimeout(() => {
    if (Math.random() > 0.7) { // 30% chance to show nudge
      showDailyNudge.value = true
    }
  }, 5000)
})
</script>

<style scoped>
.mood-slider::-webkit-slider-thumb {
  appearance: none;
  height: 24px;
  width: 24px;
  border-radius: 50%;
  background: linear-gradient(45deg, #8b5cf6, #ec4899);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.mood-slider::-moz-range-thumb {
  height: 24px;
  width: 24px;
  border-radius: 50%;
  background: linear-gradient(45deg, #8b5cf6, #ec4899);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style> 