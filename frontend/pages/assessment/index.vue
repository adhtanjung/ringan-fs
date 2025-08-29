<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <NuxtLink to="/" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center">
                <Heart class="w-4 h-4 text-white" />
              </div>
              <span class="text-xl font-bold text-gray-900">Ringan</span>
            </NuxtLink>
            <div class="hidden md:block w-px h-6 bg-gray-300"></div>
            <span class="hidden md:block text-sm text-gray-600">Assessment Kesehatan Mental</span>
          </div>
          <NuxtLink to="/" class="text-sm text-gray-600 hover:text-gray-900 flex items-center">
            <ArrowLeft class="w-4 h-4 mr-1" />
            Kembali ke Beranda
          </NuxtLink>
        </div>
      </div>
    </header>

    <div class="container-custom section-padding">
      <div class="max-w-2xl mx-auto">
        <!-- Header Section -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <ClipboardCheck class="w-8 h-8 text-white" />
          </div>
          <h1 class="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            Assessment <span class="gradient-text">Kesehatan Mental</span>
          </h1>
          <p class="text-lg text-gray-600 max-w-xl mx-auto">
            Jawab 10 pertanyaan untuk mendapatkan gambaran komprehensif kondisi kesehatan mentalmu
          </p>
        </div>

        <!-- Assessment Card -->
        <div class="bg-white rounded-2xl shadow-soft overflow-hidden">
          <!-- Question Phase -->
          <div v-if="!showFinalResults && !assessmentProgress.isActive" class="p-6 md:p-8">
            <!-- Start Assessment Button -->
            <div class="text-center">
              <button
                @click="startNewAssessment"
                :disabled="isLoading"
                class="py-4 px-8 bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                {{ isLoading ? 'Memulai Assessment...' : 'Mulai Assessment' }}
              </button>
            </div>
          </div>

          <!-- Active Assessment Phase -->
          <div v-if="!showFinalResults && assessmentProgress.isActive" class="p-6 md:p-8">
            <!-- Progress Indicator -->
            <div class="mb-6">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-gray-600">Pertanyaan {{ assessmentProgress.currentStep }} dari {{ assessmentProgress.totalQuestions }}</span>
                <span class="text-sm text-gray-500">{{ Math.round((assessmentProgress.currentStep / assessmentProgress.totalQuestions) * 100) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-500" 
                     :style="{ width: `${(assessmentProgress.currentStep / assessmentProgress.totalQuestions) * 100}%` }"></div>
              </div>
            </div>

            <!-- Question -->
            <div class="mb-8" v-if="assessmentProgress.currentQuestion">
              <div class="mb-4">
                <span class="text-sm font-medium text-green-600 bg-green-100 px-3 py-1 rounded-full">
                  {{ assessmentProgress.currentQuestion.category || 'Assessment' }}
                </span>
              </div>
              <h2 class="text-xl md:text-2xl font-bold text-gray-900 mb-4">
                {{ assessmentProgress.currentQuestion.question_text }}
              </h2>
              <p class="text-gray-600 text-sm mb-6">
                Pilih jawaban yang paling sesuai dengan kondisimu dalam 2 minggu terakhir
              </p>

              <!-- Answer Options -->
              <div class="space-y-3">
                <label 
                  v-for="(option, index) in answerOptions" 
                  :key="index"
                  :class="[
                    'flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:bg-gray-50',
                    currentAnswer === option.text 
                      ? 'border-green-500 bg-green-50' 
                      : 'border-gray-200'
                  ]"
                >
                  <input 
                    type="radio" 
                    :value="option.text" 
                    v-model="currentAnswer"
                    class="w-5 h-5 text-green-500 border-gray-300 focus:ring-green-500"
                  />
                  <span class="ml-3 text-gray-900 font-medium">{{ option.text }}</span>
                </label>
              </div>
            </div>

            <!-- Navigation Buttons -->
            <div class="flex gap-4">
              <button
                @click="handleCancelAssessment"
                class="flex-1 py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all"
              >
                <ArrowLeft class="w-4 h-4 mr-2 inline" />
                Batal
              </button>
              
              <button
                @click="submitAnswer"
                :disabled="!currentAnswer || isLoading"
                :class="[
                  'flex-1 py-4 px-6 rounded-lg font-semibold text-white transition-all',
                  currentAnswer && !isLoading
                    ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:shadow-lg'
                    : 'bg-gray-300 cursor-not-allowed opacity-50'
                ]"
              >
                {{ isLoading ? 'Mengirim...' : 'Selanjutnya' }}
                <ArrowRight class="w-4 h-4 ml-2 inline" />
              </button>
            </div>
          </div>

          <!-- Final Results Phase -->
          <div v-if="showFinalResults && assessmentResults" class="p-6 md:p-8">
            <!-- Results Header -->
            <div class="text-center mb-6">
              <div class="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp class="w-8 h-8 text-white" />
              </div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Hasil Assessment Kamu</h2>
              <div class="inline-flex items-center px-4 py-2 bg-green-100 rounded-full" v-if="assessmentResults.score">
                <span class="text-green-800 font-bold text-lg">Skor: {{ assessmentResults.score }}</span>
              </div>
            </div>

            <!-- Assessment Summary -->
            <div class="bg-gray-50 rounded-xl p-6 mb-6" v-if="assessmentResults.summary">
              <h3 class="font-semibold text-gray-900 mb-3">Ringkasan Assessment</h3>
              <p class="text-gray-700 leading-relaxed">{{ assessmentResults.summary }}</p>
            </div>

            <!-- Assessment Analysis -->
            <div class="bg-blue-50 rounded-xl p-6 mb-6 border border-blue-200" v-if="assessmentResults.analysis">
              <h3 class="font-semibold text-blue-900 mb-3">📊 Analisis Hasil</h3>
              <p class="text-blue-800 leading-relaxed">{{ assessmentResults.analysis }}</p>
            </div>

            <!-- Assessment Insights -->
            <div class="bg-gray-50 rounded-xl p-6 mb-6" v-if="assessmentResults.insights && assessmentResults.insights.length > 0">
              <h3 class="font-semibold text-gray-900 mb-4">💡 Insight dari Assessment</h3>
              <div class="space-y-3">
                <div v-for="(insight, index) in assessmentResults.insights" :key="index" class="flex items-start space-x-3">
                  <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p class="text-gray-700 text-sm">{{ insight }}</p>
                </div>
              </div>
            </div>

            <!-- Recommendations -->
            <div class="bg-green-50 rounded-xl p-6 mb-6 border border-green-200" v-if="assessmentResults.recommendations && assessmentResults.recommendations.length > 0">
              <h3 class="font-semibold text-green-900 mb-3">🎯 Rekomendasi untuk Kamu</h3>
              <ul class="text-sm text-green-800 space-y-2">
                <li v-for="recommendation in assessmentResults.recommendations" :key="recommendation" class="flex items-start">
                  <CheckCircle class="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  {{ recommendation }}
                </li>
              </ul>
            </div>

            <!-- CTA Buttons -->
            <div class="space-y-3">
              <button
                @click="showRegistrationModal = true"
                class="w-full py-4 px-6 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
              >
                📊 Daftar untuk Laporan Detail & Rekomendasi Personal
              </button>
              
              <button
                @click="showRegistrationModal = true"
                class="w-full py-3 px-6 text-green-600 hover:text-green-700 font-medium transition-colors"
              >
                Akses Konseling AI & Tracking Progress
              </button>
            </div>

            <!-- Restart Button -->
            <div class="text-center mt-6">
              <button
                @click="restartAssessment"
                class="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors"
              >
                🔄 Ulang Assessment
              </button>
            </div>
          </div>
        </div>

        <!-- Benefits Section -->
        <div class="mt-12 grid md:grid-cols-3 gap-6">
          <div class="text-center p-6 bg-white rounded-xl shadow-soft">
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield class="w-6 h-6 text-green-600" />
            </div>
            <h3 class="font-semibold text-gray-900 mb-2">100% Anonim</h3>
            <p class="text-gray-600 text-sm">Data kamu aman dan privat</p>
          </div>
          
          <div class="text-center p-6 bg-white rounded-xl shadow-soft">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock class="w-6 h-6 text-blue-600" />
            </div>
            <h3 class="font-semibold text-gray-900 mb-2">Hasil Akurat</h3>
            <p class="text-gray-600 text-sm">Berdasarkan standar psikologi</p>
          </div>
          
          <div class="text-center p-6 bg-white rounded-xl shadow-soft">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserCheck class="w-6 h-6 text-purple-600" />
            </div>
            <h3 class="font-semibold text-gray-900 mb-2">Rekomendasi Personal</h3>
            <p class="text-gray-600 text-sm">Sesuai dengan kondisi kamu</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Registration Modal -->
    <div v-if="showRegistrationModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-90vh overflow-y-auto">
        <div class="p-6">
          <!-- Modal Header -->
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-bold text-gray-900">Daftar untuk Akses Lengkap</h3>
            <button 
              @click="showRegistrationModal = false"
              class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors"
            >
              <X class="w-4 h-4 text-gray-600" />
            </button>
          </div>

          <!-- Modal Content -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                v-model="registrationForm.email"
                type="email"
                placeholder="email@domain.com"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Kata Sandi</label>
              <input
                v-model="registrationForm.password"
                type="password"
                placeholder="Minimal 6 karakter"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <button
              @click="handleRegistration"
              :disabled="!isRegistrationFormValid"
              :class="[
                'w-full py-3 px-4 rounded-lg font-semibold text-white transition-all',
                isRegistrationFormValid
                  ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:shadow-lg'
                  : 'bg-gray-300 cursor-not-allowed'
              ]"
            >
              Daftar Sekarang
            </button>

            <div class="text-center">
              <button 
                @click="showLoginForm = true"
                class="text-green-600 hover:text-green-700 font-medium text-sm transition-colors"
              >
                Sudah punya akun? Masuk di sini
              </button>
            </div>
          </div>

          <!-- Benefits Preview -->
          <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="font-semibold text-gray-900 mb-2">Yang kamu dapatkan:</h4>
            <ul class="text-sm text-gray-700 space-y-1">
              <li class="flex items-center">
                <CheckCircle class="w-4 h-4 text-green-500 mr-2" />
                Laporan assessment lengkap dengan grafik
              </li>
              <li class="flex items-center">
                <CheckCircle class="w-4 h-4 text-green-500 mr-2" />
                Rekomendasi terapi & aktivitas personal
              </li>
              <li class="flex items-center">
                <CheckCircle class="w-4 h-4 text-green-500 mr-2" />
                Akses ke AI counselor 24/7
              </li>
              <li class="flex items-center">
                <CheckCircle class="w-4 h-4 text-green-500 mr-2" />
                Tracking progress & mood harian
              </li>
              <li class="flex items-center">
                <CheckCircle class="w-4 h-4 text-green-500 mr-2" />
                Koneksi dengan psikolog professional
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Heart, 
  ArrowLeft, 
  ArrowRight,
  ClipboardCheck, 
  TrendingUp, 
  Info, 
  Shield, 
  Clock, 
  UserCheck, 
  CheckCircle, 
  X,
  Smile,
  AlertTriangle,
  AlertCircle
} from 'lucide-vue-next'
import { useOllamaChat } from '~/composables/useOllamaChat'

// Layout
definePageMeta({
  layout: false,
})

// Meta tags
useSeoMeta({
  title: 'Assessment Kesehatan Mental - Evaluasi Kondisi Mental Kamu | Ringan',
  description: 'Lakukan assessment kesehatan mental komprehensif dengan 10 pertanyaan. Dapatkan hasil akurat dan rekomendasi personal.',
})

// Use chat composable for assessment functionality
const { 
  startAssessment, 
  continueAssessment, 
  getAssessmentStatus,
  cancelAssessment,
  assessmentProgress,
  error 
} = useOllamaChat()

// Assessment state
const isLoading = ref(false)
const currentAnswer = ref('')
const assessmentResults = ref(null)
const problemCategory = ref('Mental Health Assessment')
const showFinalResults = ref(false)
const showRegistrationModal = ref(false)
const showLoginForm = ref(false)

// Check for existing assessment on mount
onMounted(async () => {
  try {
    const status = await getAssessmentStatus()
    if (status.active) {
      // Resume existing assessment
      console.log('Resuming existing assessment')
    }
  } catch (err) {
    console.error('Error checking assessment status:', err)
  }
})

// Start new assessment
const startNewAssessment = async () => {
  try {
    isLoading.value = true
    const result = await startAssessment(problemCategory.value)
    
    if (result && result.type === 'assessment_question') {
      console.log('Assessment started successfully')
    } else if (result && result.type === 'error') {
      console.error('Error starting assessment:', result.message)
    }
  } catch (err) {
    console.error('Error starting assessment:', err)
  } finally {
    isLoading.value = false
  }
}

// Submit answer and get next question
const submitAnswer = async () => {
  if (!currentAnswer.value.trim()) return
  
  try {
    isLoading.value = true
    const currentQuestion = assessmentProgress.value.currentQuestion
    
    if (!currentQuestion) {
      console.error('No current question found')
      return
    }
    
    const result = await continueAssessment(currentAnswer.value, currentQuestion.question_id)
    
    if (result && result.type === 'assessment_question') {
      // Continue with next question
      currentAnswer.value = ''
    } else if (result && result.type === 'assessment_complete') {
      // Assessment completed
      assessmentResults.value = result
      showFinalResults.value = true
    } else if (result && result.type === 'error') {
      console.error('Error submitting answer:', result.message)
    }
  } catch (err) {
    console.error('Error submitting answer:', err)
  } finally {
    isLoading.value = false
  }
}

// Cancel current assessment
const handleCancelAssessment = async () => {
  try {
    await cancelAssessment()
    showFinalResults.value = false
    currentAnswer.value = ''
  } catch (err) {
    console.error('Error canceling assessment:', err)
  }
}

// Answer options (1-5 scale) with updated text
const answerOptions = ref([
  { text: 'Tidak Pernah', value: 1 },
  { text: 'Jarang', value: 2 },
  { text: 'Kadang-kadang', value: 3 },
  { text: 'Sering', value: 4 },
  { text: 'Sangat Sering', value: 5 }
])

// Registration form
const registrationForm = ref({
  email: '',
  password: ''
})

// Computed properties
const isRegistrationFormValid = computed(() => {
  return registrationForm.value.email && 
         registrationForm.value.password && 
         registrationForm.value.password.length >= 6
})

// Methods
const restartAssessment = () => {
  showFinalResults.value = false
  assessmentResults.value = null
  currentAnswer.value = ''
}

const handleRegistration = () => {
  if (isRegistrationFormValid.value) {
    // TODO: Implement actual registration logic
    console.log('Registration:', registrationForm.value)
    
    // For now, just show success message
    alert('Pendaftaran berhasil! Kamu akan mendapatkan akses penuh ke laporan detail dan fitur konseling AI.')
    
    // Reset form
    registrationForm.value = { email: '', password: '' }
    showRegistrationModal.value = false
    
    // In real implementation, redirect to dashboard
    // navigateTo('/dashboard')
  }
}
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.section-padding {
  @apply py-12 lg:py-20;
}

.gradient-text {
  @apply bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent;
}

.shadow-soft {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Custom radio button styling */
input[type="radio"]:checked {
  background-color: #10b981;
  border-color: #10b981;
}

/* Modal animations */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>