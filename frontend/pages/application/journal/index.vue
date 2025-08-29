<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold mb-1">Jurnal Pribadi</h1>
          <p class="text-indigo-100 text-sm">Ekspresikan perasaan dan refleksi harian Anda</p>
        </div>
        <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
          <BookOpen class="w-6 h-6 text-white" />
        </div>
      </div>
      
      <!-- Journal Stats -->
      <div class="grid grid-cols-3 gap-4 mt-4 text-sm">
        <div class="text-center">
          <p class="text-2xl font-bold">{{ journalStats.totalEntries }}</p>
          <p class="text-indigo-100 text-xs">Total Entri</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ journalStats.currentStreak }}</p>
          <p class="text-indigo-100 text-xs">Hari Berturut</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold">{{ journalStats.averageWords }}</p>
          <p class="text-indigo-100 text-xs">Rata-rata Kata</p>
        </div>
      </div>
    </div>

    <!-- Privacy Lock Status -->
    <div v-if="isLocked" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 text-center">
      <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Lock class="w-8 h-8 text-purple-600" />
      </div>
      <h3 class="text-lg font-bold text-gray-900 mb-2">Jurnal Terkunci</h3>
      <p class="text-gray-600 text-sm mb-4">Masukkan PIN atau gunakan biometrik untuk mengakses jurnal</p>
      <div class="flex space-x-3 max-w-sm mx-auto">
        <button
          @click="unlockWithPIN"
          class="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
        >
          Masukkan PIN
        </button>
        <button
          @click="unlockWithBiometric"
          class="flex-1 py-2 px-4 border border-purple-600 text-purple-600 hover:bg-purple-50 rounded-lg"
        >
          Biometrik
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div v-if="!isLocked" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="grid grid-cols-2 gap-3">
        <NuxtLink
          to="/application/journal/create"
          class="flex items-center justify-center p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors group"
        >
          <div class="flex items-center space-x-2">
            <Plus class="w-5 h-5 text-purple-600" />
            <span class="text-sm font-medium text-gray-900">Entri Baru</span>
          </div>
        </NuxtLink>
        
        <button
          @click="showPrompts = true"
          class="flex items-center justify-center p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors group"
        >
          <div class="flex items-center space-x-2">
            <Lightbulb class="w-5 h-5 text-green-600" />
            <span class="text-sm font-medium text-gray-900">Prompt Harian</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Search and Filter -->
    <div v-if="!isLocked" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-3 mb-4">
        <div class="flex-1 relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            placeholder="Cari dalam jurnal..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <button
          @click="showFilters = !showFilters"
          class="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <Filter class="w-4 h-4 text-gray-600" />
        </button>
      </div>
      
      <!-- Filter Options -->
      <div v-if="showFilters" class="space-y-3">
        <!-- Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Rentang Tanggal</label>
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="dateFilter.start"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
            />
            <input
              v-model="dateFilter.end"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
            />
          </div>
        </div>
        
        <!-- Mood Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Filter Mood</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="mood in availableMoods"
              :key="mood.value"
              @click="toggleMoodFilter(mood.value)"
              :class="[
                'px-3 py-1 rounded-full text-sm transition-colors',
                selectedMoods.includes(mood.value)
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              {{ mood.emoji }} {{ mood.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Journal Timeline -->
    <div v-if="!isLocked" class="space-y-4">
      <!-- Today's Draft Notice -->
      <div v-if="todaysDraft" class="bg-yellow-50 border border-yellow-200 rounded-2xl p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <Edit class="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <h3 class="font-medium text-yellow-900">Draft Tersimpan</h3>
              <p class="text-sm text-yellow-700">{{ todaysDraft.excerpt }}</p>
            </div>
          </div>
          <NuxtLink
            :to="`/application/journal/edit/${todaysDraft.id}`"
            class="px-3 py-1 bg-yellow-200 hover:bg-yellow-300 text-yellow-800 rounded-lg text-sm"
          >
            Lanjutkan
          </NuxtLink>
        </div>
      </div>

      <!-- Journal Entries -->
      <div
        v-for="entry in filteredEntries"
        :key="entry.id"
        @click="readEntry(entry)"
        class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
      >
        <!-- Entry Header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <span class="text-lg">{{ entry.mood.emoji }}</span>
            </div>
            <div>
              <h3 class="font-medium text-gray-900">{{ formatDate(entry.createdAt) }}</h3>
              <p class="text-xs text-gray-500">{{ entry.mood.label }} • {{ entry.wordCount }} kata</p>
            </div>
          </div>
          <div class="flex items-center space-x-1">
            <button
              @click.stop="toggleBookmark(entry)"
              :class="[
                'p-1 rounded hover:bg-gray-100',
                entry.bookmarked ? 'text-purple-600' : 'text-gray-400'
              ]"
            >
              <Bookmark class="w-4 h-4" />
            </button>
            <button
              @click.stop="showEntryMenu(entry)"
              class="p-1 rounded hover:bg-gray-100 text-gray-400"
            >
              <MoreVertical class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Entry Excerpt -->
        <p class="text-gray-700 text-sm leading-relaxed line-clamp-3 mb-3">
          {{ entry.excerpt }}
        </p>

        <!-- Entry Tags -->
        <div v-if="entry.tags.length > 0" class="flex flex-wrap gap-1">
          <span
            v-for="tag in entry.tags.slice(0, 3)"
            :key="tag"
            class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
          >
            #{{ tag }}
          </span>
          <span v-if="entry.tags.length > 3" class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
            +{{ entry.tags.length - 3 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!isLocked && filteredEntries.length === 0" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <BookOpen class="w-8 h-8 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        {{ searchQuery || selectedMoods.length > 0 ? 'Tidak ada entri ditemukan' : 'Belum ada jurnal' }}
      </h3>
      <p class="text-gray-500 text-sm mb-4">
        {{ searchQuery || selectedMoods.length > 0 ? 'Coba ubah kata kunci atau filter' : 'Mulai menulis jurnal pertama Anda' }}
      </p>
      <NuxtLink
        v-if="!searchQuery && selectedMoods.length === 0"
        to="/application/journal/create"
        class="inline-flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
      >
        <Plus class="w-4 h-4" />
        <span>Tulis Jurnal</span>
      </NuxtLink>
    </div>

    <!-- Writing Prompts Modal -->
    <div v-if="showPrompts" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Prompt Jurnal Hari Ini</h3>
          <button @click="showPrompts = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div class="space-y-4">
          <div
            v-for="prompt in dailyPrompts"
            :key="prompt.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="startWithPrompt(prompt)"
          >
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="prompt.iconBg">
                <component :is="prompt.icon" class="w-4 h-4" :class="prompt.iconColor" />
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 mb-1">{{ prompt.title }}</h4>
                <p class="text-sm text-gray-600">{{ prompt.question }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Entry Menu Modal -->
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
            @click="editEntry(selectedEntry)"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Edit class="w-5 h-5 text-blue-600" />
            <span class="text-gray-900">Edit Jurnal</span>
          </button>
          
          <button
            @click="shareEntry(selectedEntry)"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Share2 class="w-5 h-5 text-green-600" />
            <span class="text-gray-900">Bagikan</span>
          </button>
          
          <button
            @click="exportEntry(selectedEntry)"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 text-left"
          >
            <Download class="w-5 h-5 text-purple-600" />
            <span class="text-gray-900">Ekspor</span>
          </button>
          
          <button
            @click="deleteEntry(selectedEntry)"
            class="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-red-50 text-left"
          >
            <Trash2 class="w-5 h-5 text-red-600" />
            <span class="text-red-900">Hapus</span>
          </button>
        </div>
      </div>
    </div>

    <!-- PIN Entry Modal -->
    <div v-if="showPinEntry" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock class="w-8 h-8 text-purple-600" />
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Masukkan PIN</h3>
          <p class="text-gray-600 text-sm">Masukkan PIN 4 digit untuk mengakses jurnal</p>
        </div>
        
        <div class="space-y-4">
          <div class="flex justify-center space-x-2">
            <input
              v-for="(digit, index) in pinDigits"
              :key="index"
              :ref="el => pinInputs[index] = el"
              v-model="pinDigits[index]"
              type="password"
              maxlength="1"
              class="w-12 h-12 text-center text-xl font-bold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              @input="onPinInput(index)"
              @keydown="onPinKeydown(index, $event)"
            />
          </div>
          
          <div class="flex space-x-3">
            <button
              @click="showPinEntry = false"
              class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Batal
            </button>
            <button
              @click="verifyPin"
              :disabled="pinDigits.some(d => !d)"
              class="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg disabled:bg-purple-300"
            >
              Buka Kunci
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings FAB -->
    <button
      v-if="!isLocked"
      @click="showSettings = true"
      class="fixed bottom-24 right-4 w-14 h-14 bg-purple-600 hover:bg-purple-700 text-white rounded-full shadow-lg flex items-center justify-center z-40"
    >
      <Settings class="w-6 h-6" />
    </button>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Pengaturan Jurnal</h3>
          <button @click="showSettings = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- Privacy Lock -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-gray-900">Kunci Privasi</h4>
              <p class="text-sm text-gray-500">Proteksi jurnal dengan PIN</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                v-model="privacySettings.lockEnabled"
                type="checkbox" 
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <!-- Auto Backup -->
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium text-gray-900">Backup Otomatis</h4>
              <p class="text-sm text-gray-500">Sinkronisasi cloud otomatis</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                v-model="privacySettings.autoBackup"
                type="checkbox" 
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <!-- Export Options -->
          <div class="pt-4 border-t border-gray-200">
            <h4 class="font-medium text-gray-900 mb-3">Ekspor Jurnal</h4>
            <div class="grid grid-cols-2 gap-2">
              <button
                @click="exportAllEntries('pdf')"
                class="flex items-center justify-center space-x-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <FileText class="w-4 h-4 text-red-600" />
                <span class="text-sm">PDF</span>
              </button>
              <button
                @click="exportAllEntries('txt')"
                class="flex items-center justify-center space-x-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <Download class="w-4 h-4 text-blue-600" />
                <span class="text-sm">Text</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  BookOpen,
  Plus,
  Lightbulb,
  Search,
  Filter,
  Edit,
  MoreVertical,
  Bookmark,
  Share2,
  Download,
  Trash2,
  X,
  Lock,
  Settings,
  FileText,
  Heart,
  Smile,
  Frown,
  Zap,
  Coffee,
  Sunset
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Data
const searchQuery = ref('')
const showFilters = ref(false)
const showPrompts = ref(false)
const showMenu = ref(false)
const showSettings = ref(false)
const showPinEntry = ref(false)
const selectedEntry = ref(null)
const isLocked = ref(false)
const selectedMoods = ref([])
const pinDigits = ref(['', '', '', ''])
const pinInputs = ref([])

const dateFilter = ref({
  start: '',
  end: ''
})

const journalStats = ref({
  totalEntries: 24,
  currentStreak: 7,
  averageWords: 156
})

const privacySettings = ref({
  lockEnabled: false,
  autoBackup: true
})

const availableMoods = [
  { value: 'happy', label: 'Bahagia', emoji: '😊' },
  { value: 'sad', label: 'Sedih', emoji: '😢' },
  { value: 'anxious', label: 'Cemas', emoji: '😰' },
  { value: 'grateful', label: 'Bersyukur', emoji: '🙏' },
  { value: 'excited', label: 'Bersemangat', emoji: '🤩' },
  { value: 'calm', label: 'Tenang', emoji: '😌' },
  { value: 'frustrated', label: 'Frustrasi', emoji: '😤' },
  { value: 'hopeful', label: 'Berharap', emoji: '🌟' }
]

const dailyPrompts = [
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
    icon: Zap,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    id: 4,
    title: 'Momen Bahagia',
    question: 'Ceritakan momen kecil yang membuat Anda tersenyum hari ini',
    icon: Coffee,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    id: 5,
    title: 'Refleksi Malam',
    question: 'Apa yang ingin Anda lakukan berbeda besok?',
    icon: Sunset,
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  }
]

const todaysDraft = ref({
  id: 'draft-' + Date.now(),
  excerpt: 'Hari ini saya merasa...',
  lastEdited: new Date()
})

const journalEntries = ref([
  {
    id: 1,
    title: 'Hari yang Melelahkan',
    content: 'Hari ini sangat melelahkan. Banyak deadline yang harus diselesaikan di kantor. Tapi saya bersyukur bisa menyelesaikan semuanya dengan baik. Besok ingin lebih tenang dalam menghadapi masalah.',
    excerpt: 'Hari ini sangat melelahkan. Banyak deadline yang harus diselesaikan di kantor...',
    mood: { value: 'frustrated', label: 'Frustrasi', emoji: '😤' },
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    wordCount: 45,
    tags: ['kerja', 'deadline', 'stress'],
    bookmarked: false,
    draft: false
  },
  {
    id: 2,
    title: 'Momen Bersyukur',
    content: 'Sore ini saya berjalan di taman dekat rumah. Cuaca sangat indah dan saya bertemu teman lama. Kami ngobrol panjang tentang kehidupan. Saya merasa sangat bersyukur memiliki teman yang peduli.',
    excerpt: 'Sore ini saya berjalan di taman dekat rumah. Cuaca sangat indah...',
    mood: { value: 'grateful', label: 'Bersyukur', emoji: '🙏' },
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    wordCount: 52,
    tags: ['teman', 'taman', 'bersyukur'],
    bookmarked: true,
    draft: false
  },
  {
    id: 3,
    title: 'Kecemasan Berlebihan',
    content: 'Hari ini saya merasa cemas berlebihan tentang presentasi besok. Jantung berdebar dan sulit tidur. Mencoba teknik pernapasan yang dipelajari kemarin. Semoga besok berjalan lancar.',
    excerpt: 'Hari ini saya merasa cemas berlebihan tentang presentasi besok...',
    mood: { value: 'anxious', label: 'Cemas', emoji: '😰' },
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    wordCount: 38,
    tags: ['presentasi', 'cemas', 'pernapasan'],
    bookmarked: false,
    draft: false
  },
  {
    id: 4,
    title: 'Hari yang Produktif',
    content: 'Alhamdulillah hari ini sangat produktif. Berhasil menyelesaikan banyak tugas dan masih sempat olahraga sore. Merasa energi positif mengalir. Ingin mempertahankan rutinitas ini.',
    excerpt: 'Alhamdulillah hari ini sangat produktif. Berhasil menyelesaikan banyak tugas...',
    mood: { value: 'excited', label: 'Bersemangat', emoji: '🤩' },
    createdAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
    wordCount: 41,
    tags: ['produktif', 'olahraga', 'energi'],
    bookmarked: true,
    draft: false
  }
])

// Computed
const filteredEntries = computed(() => {
  let filtered = journalEntries.value.filter(entry => !entry.draft)

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(entry =>
      entry.content.toLowerCase().includes(query) ||
      entry.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // Filter by mood
  if (selectedMoods.value.length > 0) {
    filtered = filtered.filter(entry =>
      selectedMoods.value.includes(entry.mood.value)
    )
  }

  // Filter by date range
  if (dateFilter.value.start && dateFilter.value.end) {
    const startDate = new Date(dateFilter.value.start)
    const endDate = new Date(dateFilter.value.end)
    filtered = filtered.filter(entry => {
      const entryDate = new Date(entry.createdAt)
      return entryDate >= startDate && entryDate <= endDate
    })
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

// Methods
const formatDate = (date) => {
  const today = new Date()
  const entryDate = new Date(date)
  const diffTime = Math.abs(today - entryDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) {
    return 'Hari ini'
  } else if (diffDays === 2) {
    return 'Kemarin'
  } else if (diffDays <= 7) {
    return `${diffDays - 1} hari lalu`
  } else {
    return new Intl.DateTimeFormat('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(entryDate)
  }
}

const toggleMoodFilter = (mood) => {
  const index = selectedMoods.value.indexOf(mood)
  if (index > -1) {
    selectedMoods.value.splice(index, 1)
  } else {
    selectedMoods.value.push(mood)
  }
}

const toggleBookmark = (entry) => {
  entry.bookmarked = !entry.bookmarked
  // Save to localStorage
  localStorage.setItem('journal-entries', JSON.stringify(journalEntries.value))
}

const readEntry = (entry) => {
  navigateTo(`/application/journal/view/${entry.id}`)
}

const showEntryMenu = (entry) => {
  selectedEntry.value = entry
  showMenu.value = true
}

const editEntry = (entry) => {
  showMenu.value = false
  navigateTo(`/application/journal/edit/${entry.id}`)
}

const shareEntry = (entry) => {
  showMenu.value = false
  // Implement sharing functionality
  if (navigator.share) {
    navigator.share({
      title: `Jurnal: ${formatDate(entry.createdAt)}`,
      text: entry.excerpt
    })
  }
}

const exportEntry = (entry) => {
  showMenu.value = false
  const content = `# Jurnal - ${formatDate(entry.createdAt)}\n\n**Mood:** ${entry.mood.emoji} ${entry.mood.label}\n\n${entry.content}\n\n**Tags:** ${entry.tags.join(', ')}`
  
  const element = document.createElement('a')
  const file = new Blob([content], { type: 'text/plain' })
  element.href = URL.createObjectURL(file)
  element.download = `jurnal-${entry.id}.txt`
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}

const deleteEntry = (entry) => {
  showMenu.value = false
  if (confirm('Apakah Anda yakin ingin menghapus jurnal ini?')) {
    const index = journalEntries.value.findIndex(e => e.id === entry.id)
    if (index > -1) {
      journalEntries.value.splice(index, 1)
      localStorage.setItem('journal-entries', JSON.stringify(journalEntries.value))
    }
  }
}

const startWithPrompt = (prompt) => {
  showPrompts.value = false
  navigateTo(`/application/journal/create?prompt=${prompt.id}`)
}

const exportAllEntries = (format) => {
  showSettings.value = false
  
  if (format === 'pdf') {
    // In a real app, you'd use a library like jsPDF
    alert('Fitur ekspor PDF akan segera tersedia')
  } else if (format === 'txt') {
    const content = journalEntries.value
      .filter(entry => !entry.draft)
      .map(entry => `# ${formatDate(entry.createdAt)}\n\n**Mood:** ${entry.mood.emoji} ${entry.mood.label}\n\n${entry.content}\n\n**Tags:** ${entry.tags.join(', ')}\n\n---\n`)
      .join('\n')
    
    const element = document.createElement('a')
    const file = new Blob([content], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = 'semua-jurnal.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }
}

const unlockWithPIN = () => {
  showPinEntry.value = true
}

const unlockWithBiometric = () => {
  // In a real app, you'd use the Web Authentication API
  if (navigator.credentials) {
    alert('Fitur biometrik akan segera tersedia')
  } else {
    alert('Biometrik tidak didukung di browser ini')
  }
}

const onPinInput = (index) => {
  if (pinDigits.value[index] && index < 3) {
    pinInputs.value[index + 1]?.focus()
  }
}

const onPinKeydown = (index, event) => {
  if (event.key === 'Backspace' && !pinDigits.value[index] && index > 0) {
    pinInputs.value[index - 1]?.focus()
  }
}

const verifyPin = () => {
  const enteredPin = pinDigits.value.join('')
  const correctPin = '1234' // In a real app, this would be stored securely
  
  if (enteredPin === correctPin) {
    isLocked.value = false
    showPinEntry.value = false
    pinDigits.value = ['', '', '', '']
  } else {
    alert('PIN salah. Silakan coba lagi.')
    pinDigits.value = ['', '', '', '']
    pinInputs.value[0]?.focus()
  }
}

// Lifecycle
onMounted(() => {
  // Load journal entries from localStorage
  const savedEntries = localStorage.getItem('journal-entries')
  if (savedEntries) {
    journalEntries.value = JSON.parse(savedEntries).map(entry => ({
      ...entry,
      createdAt: new Date(entry.createdAt)
    }))
  }

  // Load privacy settings
  const savedSettings = localStorage.getItem('journal-privacy')
  if (savedSettings) {
    privacySettings.value = JSON.parse(savedSettings)
  }

  // Check if journal should be locked
  isLocked.value = privacySettings.value.lockEnabled

  // Check for today's draft
  const today = new Date().toDateString()
  const hasTodayEntry = journalEntries.value.some(entry => 
    new Date(entry.createdAt).toDateString() === today && !entry.draft
  )
  const hasTodayDraft = localStorage.getItem('journal-draft-today')
  
  if (!hasTodayEntry && hasTodayDraft) {
    todaysDraft.value = JSON.parse(hasTodayDraft)
  } else {
    todaysDraft.value = null
  }
})

// Watch privacy settings changes
watch(privacySettings, (newSettings) => {
  localStorage.setItem('journal-privacy', JSON.stringify(newSettings))
  if (newSettings.lockEnabled && !isLocked.value) {
    // Don't auto-lock, let user manually lock
  }
}, { deep: true })
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease;
}

.transition-shadow {
  transition: box-shadow 0.2s ease;
}

.fixed.inset-0 {
  backdrop-filter: blur(4px);
}

/* Custom toggle switch styling */
input[type="checkbox"]:checked + div {
  background-color: #9333ea;
}

/* PIN input styling */
input[type="password"]:focus {
  transform: scale(1.05);
}
</style> 