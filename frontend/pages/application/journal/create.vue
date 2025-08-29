<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
      <div class="flex items-center space-x-4">
        <button @click="goBack" class="p-2 hover:bg-white/20 rounded-full">
          <ArrowLeft class="w-5 h-5" />
        </button>
        <div class="flex-1">
          <h1 class="text-xl font-bold mb-1">{{ isEditing ? 'Edit Jurnal' : 'Tulis Jurnal' }}</h1>
          <p class="text-purple-100 text-sm">{{ getCurrentDateString() }}</p>
        </div>
        <div class="flex items-center space-x-2">
          <div v-if="autoSaveStatus" class="flex items-center space-x-1 text-purple-100 text-xs">
            <Check v-if="autoSaveStatus === 'saved'" class="w-3 h-3" />
            <Loader v-if="autoSaveStatus === 'saving'" class="w-3 h-3 animate-spin" />
            <span>{{ autoSaveStatus === 'saved' ? 'Tersimpan' : 'Menyimpan...' }}</span>
          </div>
          <button
            @click="saveDraft"
            class="px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm"
          >
            Draft
          </button>
        </div>
      </div>
    </div>

    <!-- Writing Mode Toggle -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-200">
      <div class="flex items-center space-x-4">
        <span class="text-sm font-medium text-gray-700">Mode Menulis:</span>
        <div class="flex bg-gray-100 rounded-lg p-1">
          <button
            @click="writingMode = 'free'"
            :class="[
              'px-3 py-1 rounded-md text-sm transition-colors',
              writingMode === 'free'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Bebas
          </button>
          <button
            @click="writingMode = 'prompt'"
            :class="[
              'px-3 py-1 rounded-md text-sm transition-colors',
              writingMode === 'prompt'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Dengan Prompt
          </button>
        </div>
      </div>
    </div>

    <!-- Writing Prompt (if selected) -->
    <div v-if="writingMode === 'prompt'" class="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-6 border border-green-200">
      <div class="flex items-start space-x-4">
        <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
          <Lightbulb class="w-5 h-5 text-green-600" />
        </div>
        <div class="flex-1">
          <h3 class="font-medium text-gray-900 mb-2">{{ selectedPrompt.title }}</h3>
          <p class="text-gray-700 text-sm mb-3">{{ selectedPrompt.question }}</p>
          <button
            @click="showPromptsList = true"
            class="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Ganti Prompt
          </button>
        </div>
      </div>
    </div>

    <!-- Mood Selection -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h3 class="font-medium text-gray-900 mb-3">Bagaimana perasaan Anda saat ini?</h3>
      <div class="grid grid-cols-4 sm:grid-cols-6 gap-3">
        <button
          v-for="mood in availableMoods"
          :key="mood.value"
          @click="selectedMood = mood"
          :class="[
            'p-3 rounded-xl border-2 transition-all text-center',
            selectedMood?.value === mood.value
              ? 'border-purple-500 bg-purple-50 scale-105'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          ]"
        >
          <div class="text-2xl mb-1">{{ mood.emoji }}</div>
          <div class="text-xs text-gray-600">{{ mood.label }}</div>
        </button>
      </div>
    </div>

    <!-- Main Writing Area -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200">
      <!-- Writing Tools -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <button
            @click="insertTemplate('gratitude')"
            class="text-sm text-gray-600 hover:text-purple-600 px-2 py-1 rounded hover:bg-purple-50"
          >
            📝 Gratitude
          </button>
          <button
            @click="insertTemplate('reflection')"
            class="text-sm text-gray-600 hover:text-purple-600 px-2 py-1 rounded hover:bg-purple-50"
          >
            🤔 Refleksi
          </button>
          <button
            @click="insertTemplate('goals')"
            class="text-sm text-gray-600 hover:text-purple-600 px-2 py-1 rounded hover:bg-purple-50"
          >
            🎯 Tujuan
          </button>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500">
          <span>{{ wordCount }} kata</span>
          <span>•</span>
          <span>{{ readingTime }} min baca</span>
        </div>
      </div>

      <!-- Text Area -->
      <div class="p-6">
        <textarea
          ref="textareaRef"
          v-model="content"
          :placeholder="getPlaceholderText()"
          class="w-full min-h-[300px] resize-none border-none outline-none text-gray-900 leading-relaxed"
          @input="onContentChange"
          @keydown="onKeyDown"
        ></textarea>
      </div>
    </div>

    <!-- Tags Input -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h3 class="font-medium text-gray-900 mb-3">Tag (opsional)</h3>
      <div class="flex flex-wrap gap-2 mb-3">
        <span
          v-for="tag in tags"
          :key="tag"
          class="inline-flex items-center space-x-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
        >
          <span>{{ tag }}</span>
          <button @click="removeTag(tag)" class="text-purple-500 hover:text-purple-700">
            <X class="w-3 h-3" />
          </button>
        </span>
      </div>
      <div class="flex space-x-2">
        <input
          v-model="newTag"
          placeholder="Tambah tag..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
          @keyup.enter="addTag"
        />
        <button
          @click="addTag"
          :disabled="!newTag.trim()"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm disabled:bg-purple-300"
        >
          Tambah
        </button>
      </div>
      
      <!-- Suggested Tags -->
      <div v-if="suggestedTags.length > 0" class="mt-3">
        <p class="text-sm text-gray-600 mb-2">Tag yang disarankan:</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in suggestedTags"
            :key="tag"
            @click="addSuggestedTag(tag)"
            class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-purple-100 hover:text-purple-700"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </div>

    <!-- Privacy Settings -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h3 class="font-medium text-gray-900 mb-3">Pengaturan Privasi</h3>
      <div class="space-y-3">
        <label class="flex items-center space-x-3 cursor-pointer">
          <input
            v-model="isPrivate"
            type="checkbox"
            class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
          />
          <span class="text-sm text-gray-700">Jadikan jurnal ini privat</span>
        </label>
        <label class="flex items-center space-x-3 cursor-pointer">
          <input
            v-model="allowBackup"
            type="checkbox"
            class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
          />
          <span class="text-sm text-gray-700">Izinkan backup otomatis</span>
        </label>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex space-x-3 pb-6">
      <button
        @click="saveDraft"
        class="flex-1 py-3 px-4 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 font-medium"
      >
        Simpan Draft
      </button>
      <button
        @click="saveEntry"
        :disabled="!canSave"
        class="flex-1 py-3 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium disabled:bg-purple-300"
      >
        {{ isEditing ? 'Perbarui' : 'Terbitkan' }}
      </button>
    </div>

    <!-- Writing Prompts Modal -->
    <div v-if="showPromptsList" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Pilih Prompt</h3>
          <button @click="showPromptsList = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="prompt in availablePrompts"
            :key="prompt.id"
            class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="selectPrompt(prompt)"
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

    <!-- Offline Status -->
    <div v-if="isOffline" class="fixed bottom-24 left-4 bg-orange-500 text-white px-4 py-2 rounded-lg shadow-lg">
      <div class="flex items-center space-x-2">
        <WifiOff class="w-4 h-4" />
        <span class="text-sm">Mode Offline - Akan sinkron otomatis</span>
      </div>
    </div>

    <!-- Exit Confirmation -->
    <div v-if="showExitConfirm" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Keluar Tanpa Menyimpan?</h3>
        <p class="text-gray-600 text-sm mb-6">Anda memiliki perubahan yang belum disimpan. Apa yang ingin Anda lakukan?</p>
        
        <div class="space-y-3">
          <button
            @click="saveAndExit"
            class="w-full py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            Simpan & Keluar
          </button>
          <button
            @click="saveDraftAndExit"
            class="w-full py-2 px-4 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg"
          >
            Simpan Draft & Keluar
          </button>
          <button
            @click="exitWithoutSaving"
            class="w-full py-2 px-4 text-red-600 hover:bg-red-50 rounded-lg"
          >
            Keluar Tanpa Menyimpan
          </button>
          <button
            @click="showExitConfirm = false"
            class="w-full py-2 px-4 text-gray-500 hover:bg-gray-50 rounded-lg"
          >
            Batal
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  ArrowLeft,
  Check,
  Loader,
  Lightbulb,
  X,
  WifiOff,
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

// Props and route
const route = useRoute()
const router = useRouter()
const isEditing = computed(() => !!route.params.id)

// Data
const content = ref('')
const selectedMood = ref(null)
const tags = ref([])
const newTag = ref('')
const isPrivate = ref(false)
const allowBackup = ref(true)
const writingMode = ref('free')
const selectedPrompt = ref(null)
const showPromptsList = ref(false)
const showExitConfirm = ref(false)
const autoSaveStatus = ref('')
const isOffline = ref(false)
const hasUnsavedChanges = ref(false)

// Refs
const textareaRef = ref(null)

// Auto-save timer
let autoSaveTimer = null

const availableMoods = [
  { value: 'happy', label: 'Bahagia', emoji: '😊' },
  { value: 'sad', label: 'Sedih', emoji: '😢' },
  { value: 'anxious', label: 'Cemas', emoji: '😰' },
  { value: 'grateful', label: 'Bersyukur', emoji: '🙏' },
  { value: 'excited', label: 'Bersemangat', emoji: '🤩' },
  { value: 'calm', label: 'Tenang', emoji: '😌' },
  { value: 'frustrated', label: 'Frustrasi', emoji: '😤' },
  { value: 'hopeful', label: 'Berharap', emoji: '🌟' },
  { value: 'tired', label: 'Lelah', emoji: '😴' },
  { value: 'proud', label: 'Bangga', emoji: '😌' },
  { value: 'confused', label: 'Bingung', emoji: '😕' },
  { value: 'motivated', label: 'Termotivasi', emoji: '💪' }
]

const availablePrompts = [
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
  },
  {
    id: 6,
    title: 'Tujuan & Harapan',
    question: 'Apa tujuan kecil yang ingin Anda capai minggu ini?',
    icon: Target,
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600'
  }
]

const templates = {
  gratitude: `## Hal yang saya syukuri hari ini:
1. 
2. 
3. 

## Mengapa saya bersyukur:
`,
  reflection: `## Refleksi hari ini:

**Yang berjalan baik:**
- 

**Yang bisa diperbaiki:**
- 

**Pelajaran yang didapat:**
- 
`,
  goals: `## Tujuan hari ini:
- [ ] 
- [ ] 
- [ ] 

## Evaluasi tujuan kemarin:

## Rencana untuk besok:
`
}

// Computed
const wordCount = computed(() => {
  return content.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const readingTime = computed(() => {
  return Math.max(1, Math.ceil(wordCount.value / 200))
})

const canSave = computed(() => {
  return content.value.trim().length > 10 && selectedMood.value
})

const suggestedTags = computed(() => {
  const allTags = ['kerja', 'keluarga', 'kesehatan', 'hubungan', 'belajar', 'olahraga', 'hobi', 'travel']
  return allTags.filter(tag => 
    !tags.value.includes(tag) && 
    content.value.toLowerCase().includes(tag.toLowerCase())
  ).slice(0, 5)
})

// Methods
const getCurrentDateString = () => {
  return new Intl.DateTimeFormat('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date())
}

const getPlaceholderText = () => {
  if (writingMode.value === 'prompt' && selectedPrompt.value) {
    return `Mulai menulis tentang: ${selectedPrompt.value.question}...`
  }
  return 'Tuliskan apa yang ada di pikiran Anda hari ini...'
}

const onContentChange = () => {
  hasUnsavedChanges.value = true
  clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    autoSaveDraft()
  }, 2000)
}

const onKeyDown = (event) => {
  // Expand textarea automatically
  nextTick(() => {
    const textarea = textareaRef.value
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.max(300, textarea.scrollHeight) + 'px'
    }
  })
}

const autoSaveDraft = async () => {
  if (!content.value.trim() && !selectedMood.value) return
  
  autoSaveStatus.value = 'saving'
  
  try {
    const draftData = {
      content: content.value,
      mood: selectedMood.value,
      tags: tags.value,
      isPrivate: isPrivate.value,
      allowBackup: allowBackup.value,
      prompt: selectedPrompt.value,
      lastSaved: new Date().toISOString()
    }
    
    localStorage.setItem('journal-current-draft', JSON.stringify(draftData))
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    autoSaveStatus.value = 'saved'
    setTimeout(() => {
      autoSaveStatus.value = ''
    }, 2000)
  } catch (error) {
    console.error('Auto-save failed:', error)
    autoSaveStatus.value = ''
  }
}

const saveDraft = async () => {
  try {
    const draftData = {
      id: isEditing.value ? route.params.id : 'draft-' + Date.now(),
      content: content.value,
      mood: selectedMood.value,
      tags: tags.value,
      isPrivate: isPrivate.value,
      allowBackup: allowBackup.value,
      prompt: selectedPrompt.value,
      createdAt: new Date(),
      draft: true
    }
    
    const existingDrafts = JSON.parse(localStorage.getItem('journal-drafts') || '[]')
    const draftIndex = existingDrafts.findIndex(d => d.id === draftData.id)
    
    if (draftIndex > -1) {
      existingDrafts[draftIndex] = draftData
    } else {
      existingDrafts.push(draftData)
    }
    
    localStorage.setItem('journal-drafts', JSON.stringify(existingDrafts))
    localStorage.removeItem('journal-current-draft')
    
    hasUnsavedChanges.value = false
    
    // Show success message
    alert('Draft berhasil disimpan!')
    
  } catch (error) {
    console.error('Save draft failed:', error)
    alert('Gagal menyimpan draft')
  }
}

const saveEntry = async () => {
  if (!canSave.value) return
  
  try {
    const entryData = {
      id: isEditing.value ? route.params.id : Date.now(),
      title: generateTitle(),
      content: content.value,
      excerpt: content.value.substring(0, 150) + '...',
      mood: selectedMood.value,
      tags: tags.value,
      isPrivate: isPrivate.value,
      allowBackup: allowBackup.value,
      prompt: selectedPrompt.value,
      createdAt: isEditing.value ? new Date(route.params.createdAt) : new Date(),
      updatedAt: new Date(),
      wordCount: wordCount.value,
      readingTime: readingTime.value,
      bookmarked: false,
      draft: false
    }
    
    const existingEntries = JSON.parse(localStorage.getItem('journal-entries') || '[]')
    
    if (isEditing.value) {
      const entryIndex = existingEntries.findIndex(e => e.id == route.params.id)
      if (entryIndex > -1) {
        existingEntries[entryIndex] = entryData
      }
    } else {
      existingEntries.unshift(entryData)
    }
    
    localStorage.setItem('journal-entries', JSON.stringify(existingEntries))
    localStorage.removeItem('journal-current-draft')
    
    // Remove from drafts if it was a draft
    const existingDrafts = JSON.parse(localStorage.getItem('journal-drafts') || '[]')
    const filteredDrafts = existingDrafts.filter(d => d.id !== entryData.id)
    localStorage.setItem('journal-drafts', JSON.stringify(filteredDrafts))
    
    hasUnsavedChanges.value = false
    
    // Navigate back to journal list
    navigateTo('/application/journal')
    
  } catch (error) {
    console.error('Save entry failed:', error)
    alert('Gagal menyimpan jurnal')
  }
}

const generateTitle = () => {
  const words = content.value.trim().split(' ')
  const firstSentence = content.value.split('.')[0]
  
  if (firstSentence.length <= 50) {
    return firstSentence
  }
  
  return words.slice(0, 8).join(' ') + '...'
}

const addTag = () => {
  const trimmedTag = newTag.value.trim().toLowerCase()
  if (trimmedTag && !tags.value.includes(trimmedTag)) {
    tags.value.push(trimmedTag)
    newTag.value = ''
    hasUnsavedChanges.value = true
  }
}

const addSuggestedTag = (tag) => {
  if (!tags.value.includes(tag)) {
    tags.value.push(tag)
    hasUnsavedChanges.value = true
  }
}

const removeTag = (tagToRemove) => {
  tags.value = tags.value.filter(tag => tag !== tagToRemove)
  hasUnsavedChanges.value = true
}

const insertTemplate = (templateType) => {
  const template = templates[templateType]
  const textarea = textareaRef.value
  
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const before = content.value.substring(0, start)
    const after = content.value.substring(end)
    
    content.value = before + template + after
    hasUnsavedChanges.value = true
    
    // Set cursor position after template
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + template.length
      textarea.focus()
    })
  }
}

const selectPrompt = (prompt) => {
  selectedPrompt.value = prompt
  writingMode.value = 'prompt'
  showPromptsList.value = false
  
  // Focus on textarea
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

const goBack = () => {
  if (hasUnsavedChanges.value) {
    showExitConfirm.value = true
  } else {
    navigateTo('/application/journal')
  }
}

const saveAndExit = async () => {
  await saveEntry()
  showExitConfirm.value = false
}

const saveDraftAndExit = async () => {
  await saveDraft()
  showExitConfirm.value = false
  navigateTo('/application/journal')
}

const exitWithoutSaving = () => {
  hasUnsavedChanges.value = false
  showExitConfirm.value = false
  localStorage.removeItem('journal-current-draft')
  navigateTo('/application/journal')
}

// Lifecycle
onMounted(() => {
  // Check if editing existing entry
  if (isEditing.value) {
    const existingEntries = JSON.parse(localStorage.getItem('journal-entries') || '[]')
    const entry = existingEntries.find(e => e.id == route.params.id)
    
    if (entry) {
      content.value = entry.content
      selectedMood.value = entry.mood
      tags.value = entry.tags || []
      isPrivate.value = entry.isPrivate || false
      allowBackup.value = entry.allowBackup !== false
      selectedPrompt.value = entry.prompt
      if (entry.prompt) {
        writingMode.value = 'prompt'
      }
    }
  } else {
    // Check for prompt from URL
    const promptId = route.query.prompt
    if (promptId) {
      const prompt = availablePrompts.find(p => p.id == promptId)
      if (prompt) {
        selectedPrompt.value = prompt
        writingMode.value = 'prompt'
      }
    }
    
    // Load existing draft
    const savedDraft = localStorage.getItem('journal-current-draft')
    if (savedDraft) {
      try {
        const draftData = JSON.parse(savedDraft)
        content.value = draftData.content || ''
        selectedMood.value = draftData.mood
        tags.value = draftData.tags || []
        isPrivate.value = draftData.isPrivate || false
        allowBackup.value = draftData.allowBackup !== false
        selectedPrompt.value = draftData.prompt
        if (draftData.prompt) {
          writingMode.value = 'prompt'
        }
      } catch (error) {
        console.error('Failed to load draft:', error)
      }
    }
  }
  
  // Check online status
  isOffline.value = !navigator.onLine
  
  // Focus on textarea
  nextTick(() => {
    textareaRef.value?.focus()
  })
})

onUnmounted(() => {
  clearTimeout(autoSaveTimer)
})

// Watch for online/offline status
const handleOnline = () => {
  isOffline.value = false
  // Sync any pending changes
  autoSaveDraft()
}

const handleOffline = () => {
  isOffline.value = true
}

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})

// Prevent accidental navigation
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    showExitConfirm.value = true
    next(false)
  } else {
    next()
  }
})

// Watch for content changes
watch([content, selectedMood, tags], () => {
  hasUnsavedChanges.value = true
}, { deep: true })
</script>

<style scoped>
.transition-all {
  transition: all 0.2s ease;
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

/* Custom scrollbar for modals */
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

/* Focus styles */
textarea:focus {
  outline: none;
}

/* Template button hover effects */
button:hover {
  transform: translateY(-1px);
}
</style> 