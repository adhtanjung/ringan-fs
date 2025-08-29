<template>
  <div class="space-y-6">
    <!-- Profile Header -->
    <div class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
      <div class="flex items-center space-x-4">
        <div class="relative">
          <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-3xl">
            {{ userProfile.emoji }}
          </div>
          <button 
            @click="showEmojiPicker = true"
            class="absolute -bottom-1 -right-1 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-gray-50 transition-colors"
          >
            <Edit3 class="w-4 h-4 text-purple-600" />
          </button>
        </div>
        <div class="flex-1">
          <div class="flex items-center space-x-2 mb-1">
            <h1 class="text-xl font-bold">{{ userProfile.name }}</h1>
            <button @click="editName = true" class="p-1 hover:bg-white/20 rounded">
              <Edit3 class="w-4 h-4" />
            </button>
          </div>
          <p class="text-purple-100 text-sm">Member sejak {{ formatDate(userProfile.joinDate) }}</p>
          <div class="flex items-center space-x-4 mt-2 text-sm">
            <div class="flex items-center space-x-1">
              <CheckCircle class="w-4 h-4" />
              <span>{{ userProfile.assessmentsCompleted }} Tes Selesai</span>
            </div>
            <div class="flex items-center space-x-1">
              <Bookmark class="w-4 h-4" />
              <span>{{ userProfile.bookmarkedArticles }} Artikel</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Name Modal -->
    <div v-if="editName" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Edit Nama</h3>
        <input
          v-model="tempName"
          placeholder="Masukkan nama baru"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4"
          @keyup.enter="saveName"
        />
        <div class="flex space-x-3">
          <button
            @click="cancelEditName"
            class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            @click="saveName"
            class="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            Simpan
          </button>
        </div>
      </div>
    </div>

    <!-- Emoji Picker Modal -->
    <div v-if="showEmojiPicker" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Pilih Avatar</h3>
          <button @click="showEmojiPicker = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div class="grid grid-cols-6 gap-3 max-h-60 overflow-y-auto">
          <button
            v-for="emoji in availableEmojis"
            :key="emoji"
            @click="selectEmoji(emoji)"
            :class="[
              'w-12 h-12 rounded-lg text-2xl hover:bg-purple-100 transition-colors',
              userProfile.emoji === emoji ? 'bg-purple-100 ring-2 ring-purple-500' : 'hover:bg-gray-100'
            ]"
          >
            {{ emoji }}
          </button>
        </div>
      </div>
    </div>

    <!-- Mental Health Insights -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Insight Kesehatan Mental</h2>
        <Brain class="w-6 h-6 text-purple-600" />
      </div>
      
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-blue-50 rounded-xl p-4">
          <div class="flex items-center space-x-2 mb-2">
            <TrendingUp class="w-5 h-5 text-blue-600" />
            <span class="text-sm font-medium text-gray-900">Progress Mood</span>
          </div>
          <p class="text-2xl font-bold text-blue-600">{{ userProfile.moodTrend }}%</p>
          <p class="text-xs text-gray-600">7 hari terakhir</p>
        </div>
        
        <div class="bg-green-50 rounded-xl p-4">
          <div class="flex items-center space-x-2 mb-2">
            <Target class="w-5 h-5 text-green-600" />
            <span class="text-sm font-medium text-gray-900">Streak Harian</span>
          </div>
          <p class="text-2xl font-bold text-green-600">{{ userProfile.dailyStreak }}</p>
          <p class="text-xs text-gray-600">hari berturut-turut</p>
        </div>
      </div>
    </div>

    <!-- Journal Overview -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-2">
          <BookOpen class="w-6 h-6 text-purple-600" />
          <h2 class="text-lg font-bold text-gray-900">Jurnal Pribadi</h2>
        </div>
        <NuxtLink to="/application/journal" class="text-sm text-purple-600 hover:text-purple-700">
          Lihat Semua
        </NuxtLink>
      </div>
      
      <!-- Journal Stats -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="text-center bg-purple-50 rounded-xl p-4">
          <p class="text-2xl font-bold text-purple-600">{{ journalStats.totalEntries }}</p>
          <p class="text-xs text-gray-600">Total Entri</p>
        </div>
        <div class="text-center bg-green-50 rounded-xl p-4">
          <p class="text-2xl font-bold text-green-600">{{ journalStats.currentStreak }}</p>
          <p class="text-xs text-gray-600">Hari Berturut</p>
        </div>
        <div class="text-center bg-blue-50 rounded-xl p-4">
          <p class="text-2xl font-bold text-blue-600">{{ journalStats.averageWords }}</p>
          <p class="text-xs text-gray-600">Kata/Entri</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <NuxtLink
          to="/application/journal/create"
          class="flex items-center justify-center p-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-colors"
        >
          <div class="flex items-center space-x-2">
            <Plus class="w-4 h-4" />
            <span class="text-sm font-medium">Tulis Baru</span>
          </div>
        </NuxtLink>
        
        <button
          @click="showJournalPrompts = true"
          class="flex items-center justify-center p-3 bg-green-50 hover:bg-green-100 text-green-700 rounded-xl transition-colors border border-green-200"
        >
          <div class="flex items-center space-x-2">
            <Lightbulb class="w-4 h-4" />
            <span class="text-sm font-medium">Prompt Harian</span>
          </div>
        </button>
      </div>

      <!-- Recent Mood Tracking -->
      <div class="mb-6">
        <h3 class="text-sm font-medium text-gray-900 mb-3">Mood 7 Hari Terakhir</h3>
        <div class="flex items-center justify-between">
          <div 
            v-for="(mood, index) in recentMoods"
            :key="index"
            class="flex flex-col items-center space-y-1"
          >
            <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-lg">
              {{ mood.emoji }}
            </div>
            <span class="text-xs text-gray-500">{{ mood.day }}</span>
          </div>
        </div>
      </div>

      <!-- Recent Journal Entries -->
      <div>
        <h3 class="text-sm font-medium text-gray-900 mb-3">Entri Terbaru</h3>
        <div class="space-y-3">
          <div 
            v-for="entry in recentJournalEntries"
            :key="entry.id"
            @click="viewJournalEntry(entry)"
            class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border border-gray-100"
          >
            <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <span class="text-lg">{{ entry.mood.emoji }}</span>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ formatJournalDate(entry.createdAt) }}</p>
              <p class="text-xs text-gray-500 line-clamp-1">{{ entry.excerpt }}</p>
              <div class="flex items-center space-x-2 mt-1">
                <span class="text-xs text-gray-400">{{ entry.wordCount }} kata</span>
                <span v-if="entry.bookmarked" class="text-xs text-purple-600">• Disimpan</span>
              </div>
            </div>
            <div class="flex items-center space-x-1">
              <Bookmark v-if="entry.bookmarked" class="w-3 h-3 text-purple-600" />
              <ChevronRight class="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Journal Prompts Modal -->
    <div v-if="showJournalPrompts" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Prompt Jurnal Hari Ini</h3>
          <button @click="showJournalPrompts = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="prompt in journalPrompts"
            :key="prompt.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            @click.stop="startWithPrompt(prompt)"
            @mousedown.stop
            @mouseup.stop
          >
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="prompt.iconBg">
                <component :is="prompt.icon" class="w-4 h-4" :class="prompt.iconColor" />
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 mb-1">{{ prompt.title }}</h4>
                <p class="text-sm text-gray-600">{{ prompt.question }}</p>
              </div>
              <button 
                @click.stop="startWithPrompt(prompt)"
                class="px-3 py-1 text-xs bg-purple-600 hover:bg-purple-700 text-white rounded-md transition-colors"
              >
                Pilih
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assessment History -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Riwayat Assessment</h2>
        <NuxtLink to="/application/assessment" class="text-sm text-purple-600 hover:text-purple-700">
          Lihat Semua
        </NuxtLink>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="assessment in recentAssessments"
          :key="assessment.id"
          class="flex items-center justify-between p-3 rounded-lg border border-gray-100"
        >
          <div class="flex items-center space-x-3">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center', getAssessmentIconBg(assessment.severity)]">
              <component :is="getAssessmentIcon(assessment.severity)" class="w-5 h-5" :class="getAssessmentIconColor(assessment.severity)" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ assessment.type }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(assessment.date) }}</p>
            </div>
          </div>
          <div class="text-right">
            <span :class="['text-xs px-2 py-1 rounded-full', getAssessmentBadgeStyle(assessment.severity)]">
              {{ assessment.severity }}
            </span>
            <p class="text-xs text-gray-500 mt-1">{{ assessment.score }}/{{ assessment.maxScore }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bookmarked Articles -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Artikel Tersimpan</h2>
        <NuxtLink to="/application/learn" class="text-sm text-purple-600 hover:text-purple-700">
          Lihat Semua
        </NuxtLink>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="article in recentBookmarks"
          :key="article.id"
          @click="readArticle(article)"
          class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="article.iconBg">
            <component :is="article.icon" class="w-5 h-5" :class="article.iconColor" />
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-900">{{ article.title }}</h3>
            <p class="text-xs text-gray-500">{{ article.category }} • {{ article.readTime }} min</p>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </div>

    <!-- Preferences -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-2 mb-4">
        <Settings class="w-6 h-6 text-gray-600" />
        <h2 class="text-lg font-bold text-gray-900">Preferensi</h2>
      </div>
      
      <div class="space-y-4">
        <!-- Mental Health Goals -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tujuan Kesehatan Mental</label>
          <div class="space-y-2">
            <label 
              v-for="goal in mentalHealthGoals"
              :key="goal.id"
              class="flex items-center space-x-3 cursor-pointer"
            >
              <input
                v-model="userProfile.selectedGoals"
                :value="goal.id"
                type="checkbox"
                class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <span class="text-sm text-gray-700">{{ goal.label }}</span>
            </label>
          </div>
        </div>

        <!-- Reminder Frequency -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Frekuensi Pengingat Mood</label>
          <select
            v-model="userProfile.reminderFrequency"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="none">Tidak ada</option>
            <option value="daily">Harian</option>
            <option value="weekly">Mingguan</option>
            <option value="custom">Kustom</option>
          </select>
        </div>

        <!-- Privacy Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tingkat Privasi</label>
          <div class="space-y-2">
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                v-model="userProfile.privacyLevel"
                value="public"
                type="radio"
                class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
              />
              <span class="text-sm text-gray-700">Publik - Berbagi progress dengan komunitas</span>
            </label>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                v-model="userProfile.privacyLevel"
                value="friends"
                type="radio"
                class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
              />
              <span class="text-sm text-gray-700">Teman - Hanya teman yang dapat melihat</span>
            </label>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                v-model="userProfile.privacyLevel"
                value="private"
                type="radio"
                class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
              />
              <span class="text-sm text-gray-700">Privat - Semua data bersifat pribadi</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications Settings -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-2 mb-4">
        <Bell class="w-6 h-6 text-gray-600" />
        <h2 class="text-lg font-bold text-gray-900">Notifikasi</h2>
      </div>
      
      <div class="space-y-4">
        <div
          v-for="notification in notificationSettings"
          :key="notification.key"
          class="flex items-center justify-between"
        >
          <div>
            <h3 class="text-sm font-medium text-gray-900">{{ notification.title }}</h3>
            <p class="text-xs text-gray-500">{{ notification.description }}</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              v-model="notification.enabled"
              type="checkbox" 
              class="sr-only peer"
            >
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Privacy & Security -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-2 mb-4">
        <Shield class="w-6 h-6 text-gray-600" />
        <h2 class="text-lg font-bold text-gray-900">Privasi & Keamanan</h2>
      </div>
      
      <div class="space-y-3">
        <button
          @click="exportData"
          class="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <Download class="w-5 h-5 text-blue-600" />
            <div class="text-left">
              <p class="text-sm font-medium text-gray-900">Ekspor Data</p>
              <p class="text-xs text-gray-500">Download semua data Anda</p>
            </div>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </button>

        <button
          @click="clearChatData"
          class="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <MessageCircle class="w-5 h-5 text-orange-600" />
            <div class="text-left">
              <p class="text-sm font-medium text-gray-900">Hapus Data Chat</p>
              <p class="text-xs text-gray-500">Bersihkan riwayat percakapan AI</p>
            </div>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </button>

        <button
          @click="requestDataRestore"
          class="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <RotateCcw class="w-5 h-5 text-green-600" />
            <div class="text-left">
              <p class="text-sm font-medium text-gray-900">Pulihkan Data</p>
              <p class="text-xs text-gray-500">Minta pemulihan data yang dihapus</p>
            </div>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-400" />
        </button>

        <button
          @click="deleteAccount"
          class="w-full flex items-center justify-between p-3 rounded-lg border border-red-200 bg-red-50 hover:bg-red-100 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <Trash2 class="w-5 h-5 text-red-600" />
            <div class="text-left">
              <p class="text-sm font-medium text-red-900">Hapus Akun</p>
              <p class="text-xs text-red-600">Hapus akun secara permanen</p>
            </div>
          </div>
          <ChevronRight class="w-4 h-4 text-red-400" />
        </button>
      </div>
    </div>

    <!-- Action Confirmation Modals -->
    <div v-if="showConfirmation" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <div class="flex items-center space-x-3 mb-4">
          <div :class="['w-12 h-12 rounded-full flex items-center justify-center', confirmationData.iconBg]">
            <component :is="confirmationData.icon" class="w-6 h-6" :class="confirmationData.iconColor" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">{{ confirmationData.title }}</h3>
            <p class="text-sm text-gray-600">{{ confirmationData.message }}</p>
          </div>
        </div>
        
        <div v-if="confirmationData.requiresInput" class="mb-4">
          <input
            v-model="confirmationInput"
            :placeholder="confirmationData.inputPlaceholder"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        
        <div class="flex space-x-3">
          <button
            @click="showConfirmation = false"
            class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Batal
          </button>
          <button
            @click="confirmAction"
            :disabled="confirmationData.requiresInput && !confirmationInput"
            :class="[
              'flex-1 py-2 px-4 rounded-lg font-medium transition-colors',
              confirmationData.dangerous
                ? 'bg-red-600 hover:bg-red-700 text-white disabled:bg-red-300'
                : 'bg-purple-600 hover:bg-purple-700 text-white disabled:bg-purple-300'
            ]"
          >
            {{ confirmationData.confirmText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="showSuccess" class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
      <div class="flex items-center space-x-2">
        <Check class="w-4 h-4" />
        <span class="text-sm">{{ successMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Edit3,
  X,
  CheckCircle,
  Bookmark,
  Brain,
  TrendingUp,
  Target,
  Settings,
  Bell,
  Shield,
  Download,
  MessageCircle,
  RotateCcw,
  Trash2,
  ChevronRight,
  Check,
  AlertCircle,
  AlertOctagon,
  Heart,
  Smile,
  Moon,
  Users,
  BookOpen,
  Plus,
  Lightbulb
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Data
const editName = ref(false)
const tempName = ref('')
const showEmojiPicker = ref(false)
const showConfirmation = ref(false)
const confirmationData = ref({})
const confirmationInput = ref('')
const showSuccess = ref(false)
const successMessage = ref('')
const showJournalPrompts = ref(false)

const userProfile = ref({
  name: 'Dina Arafah',
  emoji: '😊',
  joinDate: new Date(2024, 0, 1),
  assessmentsCompleted: 8,
  bookmarkedArticles: 6,
  moodTrend: 75,
  dailyStreak: 12,
  selectedGoals: ['anxiety', 'sleep'],
  reminderFrequency: 'daily',
  privacyLevel: 'private'
})

const availableEmojis = [
  '😊', '😄', '🙂', '😌', '😊', '🥰', '😇', '🤗', '🙃', '😉',
  '🌟', '🌈', '🌸', '🦋', '🌱', '💙', '💜', '💚', '🧡', '💛',
  '🌙', '☀️', '🌻', '🍀', '🕊️', '🦄', '🎈', '🎵', '📚', '☕'
]

const mentalHealthGoals = [
  { id: 'anxiety', label: 'Mengelola kecemasan' },
  { id: 'sleep', label: 'Meningkatkan kualitas tidur' },
  { id: 'stress', label: 'Mengurangi stress' },
  { id: 'mood', label: 'Stabilitas mood' },
  { id: 'relationships', label: 'Hubungan yang lebih baik' },
  { id: 'mindfulness', label: 'Praktik mindfulness' }
]

const notificationSettings = ref([
  {
    key: 'mood_reminder',
    title: 'Pengingat Mood Check-in',
    description: 'Notifikasi harian untuk mencatat mood',
    enabled: true
  },
  {
    key: 'assessment_reminder',
    title: 'Pengingat Assessment',
    description: 'Notifikasi mingguan untuk self-assessment',
    enabled: true
  },
  {
    key: 'article_recommendations',
    title: 'Rekomendasi Artikel',
    description: 'Artikel baru berdasarkan preferensi Anda',
    enabled: false
  },
  {
    key: 'community_activity',
    title: 'Aktivitas Komunitas',
    description: 'Balasan dan dukungan dari komunitas',
    enabled: true
  },
  {
    key: 'emergency_alerts',
    title: 'Peringatan Darurat',
    description: 'Notifikasi penting terkait kesehatan mental',
    enabled: true
  }
])

const recentAssessments = ref([
  {
    id: 1,
    type: 'Tes Kecemasan (GAD-7)',
    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    severity: 'Mild',
    score: 6,
    maxScore: 21
  },
  {
    id: 2,
    type: 'Tes Depresi (PHQ-9)',
    date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    severity: 'Minimal',
    score: 3,
    maxScore: 27
  },
  {
    id: 3,
    type: 'Tes Kecemasan (GAD-7)',
    date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    severity: 'Moderate',
    score: 12,
    maxScore: 21
  }
])

const recentBookmarks = ref([
  {
    id: 1,
    title: 'Mengelola Kecemasan di Tempat Kerja',
    category: 'Kecemasan',
    readTime: 5,
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    id: 2,
    title: 'Teknik Grounding untuk Serangan Panik',
    category: 'Kecemasan',
    readTime: 4,
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    id: 3,
    title: 'Mindfulness untuk Pemula',
    category: 'Relaksasi',
    readTime: 4,
    icon: Smile,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  }
])

const journalStats = ref({
  totalEntries: 0,
  currentStreak: 0,
  averageWords: 0
})

const recentMoods = ref([
  { emoji: '😊', day: 'Kamis' },
  { emoji: '😄', day: 'Jumat' },
  { emoji: '🙂', day: 'Sabtu' },
  { emoji: '😌', day: 'Minggu' },
  { emoji: '😊', day: 'Senin' },
  { emoji: '😇', day: 'Selasa' },
  { emoji: '😇', day: 'Rabu' }
])

const recentJournalEntries = ref([
  {
    id: 1,
    mood: { emoji: '😊' },
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    excerpt: 'Mencoba mengelola kecemasan dengan teknik grounding...',
    wordCount: 120,
    bookmarked: true
  },
  {
    id: 2,
    mood: { emoji: '😄' },
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    excerpt: 'Mencoba mengelola kecemasan dengan teknik grounding...',
    wordCount: 120,
    bookmarked: false
  },
  {
    id: 3,
    mood: { emoji: '🙂' },
    createdAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
    excerpt: 'Mencoba mengelola kecemasan dengan teknik grounding...',
    wordCount: 120,
    bookmarked: true
  }
])

const journalPrompts = ref([
  {
    id: 1,
    title: 'Refleksi Harian',
    question: 'Apa tiga hal yang membuat Anda bersyukur hari ini?',
    icon: Heart,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600'
  },
  {
    id: 2,
    title: 'Perasaan Saat Ini',
    question: 'Bagaimana perasaan Anda sekarang dan mengapa?',
    icon: Smile,
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600'
  },
  {
    id: 3,
    title: 'Tantangan Hari Ini',
    question: 'Tantangan apa yang Anda hadapi dan bagaimana mengatasinya?',
    icon: AlertCircle,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    id: 4,
    title: 'Momen Bahagia',
    question: 'Ceritakan momen kecil yang membuat Anda tersenyum hari ini',
    icon: Heart,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    id: 5,
    title: 'Refleksi Malam',
    question: 'Apa yang ingin Anda lakukan berbeda besok?',
    icon: Moon,
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  },
  {
    id: 6,
    title: 'Tujuan & Harapan',
    question: 'Apa tujuan kecil yang ingin Anda capai minggu ini?',
    icon: Target,
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600'
  }
])

// Methods
const saveName = () => {
  if (tempName.value.trim()) {
    userProfile.value.name = tempName.value.trim()
    showSuccessMessage('Nama berhasil diperbarui')
  }
  editName.value = false
  tempName.value = ''
}

const cancelEditName = () => {
  editName.value = false
  tempName.value = ''
}

const selectEmoji = (emoji) => {
  userProfile.value.emoji = emoji
  showEmojiPicker.value = false
  showSuccessMessage('Avatar berhasil diperbarui')
}

const showSuccessMessage = (message) => {
  successMessage.value = message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)
}

const readArticle = (article) => {
  navigateTo(`/application/learn/article/${article.id}`)
}

const exportData = () => {
  confirmationData.value = {
    title: 'Ekspor Data',
    message: 'Kami akan mengirimkan file berisi semua data Anda ke email terdaftar.',
    icon: Download,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    confirmText: 'Ekspor',
    dangerous: false,
    requiresInput: false
  }
  showConfirmation.value = true
}

const clearChatData = () => {
  confirmationData.value = {
    title: 'Hapus Data Chat',
    message: 'Semua riwayat percakapan dengan AI akan dihapus permanen. Data dapat dipulihkan dalam 30 hari.',
    icon: MessageCircle,
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    confirmText: 'Hapus Chat',
    dangerous: true,
    requiresInput: false
  }
  showConfirmation.value = true
}

const requestDataRestore = () => {
  confirmationData.value = {
    title: 'Pulihkan Data',
    message: 'Kami akan memproses permintaan pemulihan data Anda. Proses ini membutuhkan waktu 1-3 hari kerja.',
    icon: RotateCcw,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    confirmText: 'Kirim Permintaan',
    dangerous: false,
    requiresInput: false
  }
  showConfirmation.value = true
}

const deleteAccount = () => {
  confirmationData.value = {
    title: 'Hapus Akun',
    message: 'Ketik "HAPUS AKUN" untuk mengkonfirmasi penghapusan akun permanen.',
    icon: Trash2,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    confirmText: 'Hapus Akun',
    dangerous: true,
    requiresInput: true,
    inputPlaceholder: 'Ketik "HAPUS AKUN"'
  }
  showConfirmation.value = true
}

const confirmAction = () => {
  if (confirmationData.value.requiresInput && confirmationInput.value !== 'HAPUS AKUN') {
    return
  }

  // Execute the action based on the confirmation type
  if (confirmationData.value.title === 'Ekspor Data') {
    showSuccessMessage('Permintaan ekspor data telah dikirim ke email Anda')
  } else if (confirmationData.value.title === 'Hapus Data Chat') {
    showSuccessMessage('Data chat berhasil dihapus')
  } else if (confirmationData.value.title === 'Pulihkan Data') {
    showSuccessMessage('Permintaan pemulihan data telah dikirim')
  } else if (confirmationData.value.title === 'Hapus Akun') {
    // This would typically redirect to a goodbye page or login
    showSuccessMessage('Akun akan dihapus dalam 24 jam. Email konfirmasi telah dikirim.')
  }

  showConfirmation.value = false
  confirmationInput.value = ''
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date)
}

const getAssessmentIcon = (severity) => {
  switch (severity) {
    case 'Minimal': return CheckCircle
    case 'Mild': return Shield
    case 'Moderate': return AlertCircle
    case 'Moderately Severe': return AlertOctagon
    case 'Severe': return AlertOctagon
    default: return CheckCircle
  }
}

const getAssessmentIconBg = (severity) => {
  switch (severity) {
    case 'Minimal': return 'bg-green-100'
    case 'Mild': return 'bg-yellow-100'
    case 'Moderate': return 'bg-orange-100'
    case 'Moderately Severe': return 'bg-red-100'
    case 'Severe': return 'bg-red-100'
    default: return 'bg-gray-100'
  }
}

const getAssessmentIconColor = (severity) => {
  switch (severity) {
    case 'Minimal': return 'text-green-600'
    case 'Mild': return 'text-yellow-600'
    case 'Moderate': return 'text-orange-600'
    case 'Moderately Severe': return 'text-red-600'
    case 'Severe': return 'text-red-600'
    default: return 'text-gray-600'
  }
}

const getAssessmentBadgeStyle = (severity) => {
  switch (severity) {
    case 'Minimal': return 'bg-green-100 text-green-800'
    case 'Mild': return 'bg-yellow-100 text-yellow-800'
    case 'Moderate': return 'bg-orange-100 text-orange-800'
    case 'Moderately Severe': return 'bg-red-100 text-red-800'
    case 'Severe': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const formatJournalDate = (date) => {
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date)
}

const viewJournalEntry = (entry) => {
  navigateTo(`/application/journal/view/${entry.id}`)
}

const startWithPrompt = (prompt) => {
  console.log('Starting with prompt:', prompt)
  showJournalPrompts.value = false
  
  try {
    navigateTo(`/application/journal/create?prompt=${prompt.id}`)
  } catch (error) {
    console.error('Navigation error:', error)
    // Fallback navigation
    window.location.href = `/application/journal/create?prompt=${prompt.id}`
  }
}

const testPromptClick = (prompt) => {
  console.log('Test prompt click:', prompt)
  alert(`Prompt clicked: ${prompt.title}`)
}

const loadJournalData = () => {
  try {
    // Load journal entries from localStorage
    const savedEntries = localStorage.getItem('journal-entries')
    if (savedEntries) {
      const entries = JSON.parse(savedEntries).map(entry => ({
        ...entry,
        createdAt: new Date(entry.createdAt)
      }))
      
      // Update journal stats
      journalStats.value.totalEntries = entries.filter(e => !e.draft).length
      
      // Calculate average words
      const totalWords = entries.reduce((sum, entry) => sum + (entry.wordCount || 0), 0)
      journalStats.value.averageWords = entries.length > 0 
        ? Math.round(totalWords / entries.length) 
        : 0
      
      // Calculate current streak (simplified version)
      journalStats.value.currentStreak = calculateJournalStreak(entries)
      
      // Get recent entries (last 3)
      recentJournalEntries.value = entries
        .filter(e => !e.draft)
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 3)
      
      // Update recent moods based on journal entries
      updateRecentMoods(entries)
    }
  } catch (error) {
    console.error('Failed to load journal data:', error)
  }
}

const calculateJournalStreak = (entries) => {
  if (!entries.length) return 0
  
  const today = new Date()
  const sortedEntries = entries
    .filter(e => !e.draft)
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  
  let streak = 0
  let currentDate = new Date(today)
  
  for (let i = 0; i < 30; i++) { // Check last 30 days
    const dateStr = currentDate.toDateString()
    const hasEntry = sortedEntries.some(entry => 
      new Date(entry.createdAt).toDateString() === dateStr
    )
    
    if (hasEntry) {
      streak++
      currentDate.setDate(currentDate.getDate() - 1)
    } else if (streak > 0) {
      break
    } else {
      currentDate.setDate(currentDate.getDate() - 1)
    }
  }
  
  return streak
}

const updateRecentMoods = (entries) => {
  const last7Days = []
  const today = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    
    const dayEntry = entries.find(entry => 
      new Date(entry.createdAt).toDateString() === date.toDateString() && !entry.draft
    )
    
    const dayName = new Intl.DateTimeFormat('id-ID', { weekday: 'short' }).format(date)
    
    last7Days.push({
      emoji: dayEntry?.mood?.emoji || '😐',
      day: dayName
    })
  }
  
  recentMoods.value = last7Days
}

// Lifecycle
onMounted(() => {
  // Load user profile from localStorage
  const savedProfile = localStorage.getItem('mindcare-profile')
  if (savedProfile) {
    const profile = JSON.parse(savedProfile)
    userProfile.value = { ...userProfile.value, ...profile }
  }
  
  // Load notification settings
  const savedNotifications = localStorage.getItem('mindcare-notifications')
  if (savedNotifications) {
    const notifications = JSON.parse(savedNotifications)
    notificationSettings.value = notifications
  }

  // Load journal data
  loadJournalData()
})

// Watch for changes and save to localStorage
watch(userProfile, (newProfile) => {
  localStorage.setItem('mindcare-profile', JSON.stringify(newProfile))
}, { deep: true })

watch(notificationSettings, (newSettings) => {
  localStorage.setItem('mindcare-notifications', JSON.stringify(newSettings))
}, { deep: true })
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

/* Grid scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 