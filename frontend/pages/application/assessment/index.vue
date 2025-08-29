<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Self-Assessment</h1>
          <p class="text-sm text-gray-600">Evaluasi kesehatan mental Anda dengan panduan AI</p>
        </div>
        <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <ClipboardCheck class="w-6 h-6 text-blue-600" />
        </div>
      </div>
      
      <!-- Assessment Types -->
      <div class="grid grid-cols-2 gap-3">
        <button
          @click="startAssessment('anxiety')"
          class="flex flex-col items-center p-4 rounded-xl border-2 border-blue-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
        >
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
            <AlertCircle class="w-6 h-6 text-blue-600" />
          </div>
          <span class="text-sm font-medium text-gray-900">Tes Kecemasan</span>
          <span class="text-xs text-gray-500">7 pertanyaan</span>
        </button>
        
        <button
          @click="startAssessment('depression')"
          class="flex flex-col items-center p-4 rounded-xl border-2 border-purple-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
        >
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-2">
            <Heart class="w-6 h-6 text-purple-600" />
          </div>
          <span class="text-sm font-medium text-gray-900">Tes Depresi</span>
          <span class="text-xs text-gray-500">9 pertanyaan</span>
        </button>
      </div>
    </div>

    <!-- Assessment Progress (if in progress) -->
    <div v-if="currentAssessment" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">{{ getAssessmentTitle(currentAssessment.type) }}</h2>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">{{ currentQuestionIndex + 1 }}/{{ currentAssessment.questions.length }}</span>
          <button @click="exitAssessment" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>
      
      <!-- Progress Bar -->
      <div class="mb-6">
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${((currentQuestionIndex + 1) / currentAssessment.questions.length) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Current Question -->
      <div v-if="currentQuestion" class="space-y-4">
        <!-- AI Avatar & Question Bubble -->
        <div class="flex items-start space-x-3">
          <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <Bot class="w-5 h-5 text-white" />
          </div>
          <div class="flex-1 bg-blue-50 rounded-2xl rounded-tl-none p-4">
            <p class="text-gray-900">{{ currentQuestion.text }}</p>
            <div v-if="currentQuestion.subtitle" class="text-sm text-gray-600 mt-2">
              {{ currentQuestion.subtitle }}
            </div>
          </div>
        </div>

        <!-- Answer Options -->
        <div class="ml-13 space-y-3">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            @click="selectAnswer(option.value)"
            :class="[
              'w-full p-4 text-left rounded-xl border-2 transition-all',
              selectedAnswer === option.value
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            ]"
          >
            <div class="flex items-center space-x-3">
              <div :class="[
                'w-4 h-4 rounded-full border-2 transition-all',
                selectedAnswer === option.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300'
              ]">
                <div v-if="selectedAnswer === option.value" class="w-2 h-2 bg-white rounded-full m-0.5"></div>
              </div>
              <span class="text-gray-900">{{ option.text }}</span>
            </div>
          </button>
        </div>

        <!-- Navigation Buttons -->
        <div class="ml-13 flex space-x-3 pt-4">
          <button
            v-if="currentQuestionIndex > 0"
            @click="previousQuestion"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Sebelumnya
          </button>
          <button
            @click="nextQuestion"
            :disabled="!selectedAnswer"
            :class="[
              'flex-1 py-2 px-4 rounded-lg font-medium transition-colors',
              selectedAnswer
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            ]"
          >
            {{ isLastQuestion ? 'Selesai' : 'Lanjut' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Assessment Results -->
    <div v-if="assessmentResult" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="text-center mb-6">
        <div :class="['w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4', getResultIconBg(assessmentResult.severity)]">
          <component :is="getResultIcon(assessmentResult.severity)" class="w-8 h-8" :class="getResultIconColor(assessmentResult.severity)" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Hasil Assessment</h2>
        <div :class="['inline-block px-4 py-2 rounded-full text-sm font-medium', getResultBadgeStyle(assessmentResult.severity)]">
          {{ assessmentResult.severity }}
        </div>
      </div>

      <!-- Score Display -->
      <div class="bg-gray-50 rounded-xl p-4 mb-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600">Skor Total</span>
          <span class="text-lg font-bold text-gray-900">{{ assessmentResult.score }}/{{ assessmentResult.maxScore }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            :class="['h-2 rounded-full transition-all duration-500', getScoreBarColor(assessmentResult.severity)]"
            :style="{ width: `${(assessmentResult.score / assessmentResult.maxScore) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Feedback & Description -->
      <div class="space-y-4 mb-6">
        <div class="bg-blue-50 rounded-xl p-4">
          <h3 class="font-medium text-gray-900 mb-2">Penjelasan Hasil</h3>
          <p class="text-sm text-gray-700">{{ assessmentResult.description }}</p>
        </div>

        <!-- Recommendations -->
        <div class="space-y-3">
          <h3 class="font-medium text-gray-900">Langkah Selanjutnya</h3>
          <div class="space-y-2">
            <div v-for="(recommendation, index) in assessmentResult.recommendations" :key="index" class="flex items-start space-x-3">
              <div class="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mt-0.5">
                <Check class="w-3 h-3 text-green-600" />
              </div>
              <p class="text-sm text-gray-700">{{ recommendation }}</p>
            </div>
          </div>
        </div>

        <!-- Emergency Resources (if severe) -->
        <div v-if="assessmentResult.severity === 'Severe'" class="bg-red-50 border border-red-200 rounded-xl p-4">
          <div class="flex items-start space-x-3">
            <AlertTriangle class="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h3 class="font-medium text-red-900 mb-2">Butuh Bantuan Segera?</h3>
              <p class="text-sm text-red-700 mb-3">Jika Anda merasa dalam bahaya atau memiliki pikiran untuk menyakiti diri sendiri, segera hubungi:</p>
              <div class="space-y-1 text-sm">
                <p class="text-red-800 font-medium">• Hotline Crisis: 119 ext 8</p>
                <p class="text-red-800 font-medium">• Emergency: 112</p>
                <p class="text-red-800 font-medium">• RSJ Terdekat</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-3">
        <button
          @click="talkToAI"
          class="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
        >
          Diskusi dengan AI Counselor
        </button>
        
        <div class="grid grid-cols-2 gap-3">
          <button
            @click="saveResult"
            class="py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
          >
            Simpan Hasil
          </button>
          <button
            @click="retakeAssessment"
            class="py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
          >
            Ulangi Test
          </button>
        </div>
      </div>
    </div>

    <!-- Assessment History -->
    <div v-if="!currentAssessment && !assessmentResult" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">Riwayat Assessment</h2>
        <button class="text-sm text-blue-600 hover:text-blue-700">Lihat Semua</button>
      </div>
      
      <div class="space-y-3">
        <div v-for="history in assessmentHistory" :key="history.id" class="flex items-center justify-between p-3 rounded-lg border border-gray-100">
          <div class="flex items-center space-x-3">
            <div :class="['w-8 h-8 rounded-full flex items-center justify-center', getResultIconBg(history.severity)]">
              <component :is="getResultIcon(history.severity)" class="w-4 h-4" :class="getResultIconColor(history.severity)" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ history.type }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(history.date) }}</p>
            </div>
          </div>
          <div class="text-right">
            <span :class="['text-xs px-2 py-1 rounded-full', getResultBadgeStyle(history.severity)]">
              {{ history.severity }}
            </span>
            <p class="text-xs text-gray-500 mt-1">{{ history.score }}/{{ history.maxScore }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  ClipboardCheck,
  AlertCircle,
  Heart,
  Bot,
  X,
  Check,
  AlertTriangle,
  CheckCircle,
  AlertOctagon,
  Shield
} from 'lucide-vue-next'

// Set layout
definePageMeta({
  layout: 'app'
})

// Assessment questions data
const anxietyQuestions = [
  {
    text: "Seberapa sering Anda merasa gugup, cemas, atau tegang dalam 2 minggu terakhir?",
    subtitle: "Pilih jawaban yang paling sesuai dengan kondisi Anda",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda tidak dapat menghentikan atau mengontrol kekhawatiran?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda khawatir berlebihan tentang berbagai hal?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda mengalami kesulitan untuk rileks?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda merasa gelisah sehingga sulit untuk duduk diam?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda mudah tersinggung atau mudah marah?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda merasa takut seolah-olah sesuatu yang mengerikan akan terjadi?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  }
]

const depressionQuestions = [
  {
    text: "Seberapa sering Anda merasa kurang tertarik atau senang melakukan hal-hal yang biasa Anda lakukan dalam 2 minggu terakhir?",
    subtitle: "Pilih jawaban yang paling sesuai dengan kondisi Anda",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda merasa sedih, putus asa, atau tidak berdaya?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda mengalami kesulitan tidur, sering terbangun, atau tidur terlalu banyak?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda merasa lelah atau kehilangan energi?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda kehilangan nafsu makan atau makan berlebihan?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda merasa buruk tentang diri sendiri atau merasa gagal?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda mengalami kesulitan berkonsentrasi pada hal-hal seperti membaca atau menonton TV?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda bergerak atau berbicara sangat lambat sehingga orang lain menyadarinya?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  },
  {
    text: "Seberapa sering Anda berpikir bahwa Anda lebih baik mati atau menyakiti diri sendiri?",
    options: [
      { text: "Tidak pernah", value: 0 },
      { text: "Beberapa hari", value: 1 },
      { text: "Lebih dari setengah hari", value: 2 },
      { text: "Hampir setiap hari", value: 3 }
    ]
  }
]

// Data
const currentAssessment = ref(null)
const currentQuestionIndex = ref(0)
const selectedAnswer = ref(null)
const assessmentAnswers = ref([])
const assessmentResult = ref(null)

const assessmentHistory = ref([
  {
    id: 1,
    type: "Tes Kecemasan",
    date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    severity: "Mild",
    score: 6,
    maxScore: 21
  },
  {
    id: 2,
    type: "Tes Depresi",
    date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    severity: "Moderate",
    score: 12,
    maxScore: 27
  }
])

// Computed
const currentQuestion = computed(() => {
  if (!currentAssessment.value) return null
  return currentAssessment.value.questions[currentQuestionIndex.value]
})

const isLastQuestion = computed(() => {
  if (!currentAssessment.value) return false
  return currentQuestionIndex.value === currentAssessment.value.questions.length - 1
})

// Methods
const startAssessment = (type) => {
  currentAssessment.value = {
    type,
    questions: type === 'anxiety' ? anxietyQuestions : depressionQuestions
  }
  currentQuestionIndex.value = 0
  assessmentAnswers.value = []
  selectedAnswer.value = null
  assessmentResult.value = null
}

const getAssessmentTitle = (type) => {
  return type === 'anxiety' ? 'Tes Kecemasan (GAD-7)' : 'Tes Depresi (PHQ-9)'
}

const selectAnswer = (value) => {
  selectedAnswer.value = value
}

const nextQuestion = () => {
  if (selectedAnswer.value === null) return
  
  // Save answer
  assessmentAnswers.value[currentQuestionIndex.value] = selectedAnswer.value
  
  if (isLastQuestion.value) {
    // Calculate results
    calculateResults()
  } else {
    // Move to next question
    currentQuestionIndex.value++
    selectedAnswer.value = assessmentAnswers.value[currentQuestionIndex.value] || null
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    selectedAnswer.value = assessmentAnswers.value[currentQuestionIndex.value] || null
  }
}

const calculateResults = () => {
  const totalScore = assessmentAnswers.value.reduce((sum, answer) => sum + answer, 0)
  const maxScore = currentAssessment.value.questions.length * 3
  
  let severity, description, recommendations
  
  if (currentAssessment.value.type === 'anxiety') {
    if (totalScore >= 0 && totalScore <= 4) {
      severity = "Minimal"
      description = "Tingkat kecemasan Anda minimal. Ini adalah kondisi yang normal dan sehat. Terus jaga kesehatan mental Anda dengan pola hidup sehat."
      recommendations = [
        "Pertahankan rutinitas olahraga teratur",
        "Praktikkan teknik relaksasi seperti meditasi",
        "Jaga pola tidur yang teratur",
        "Lanjutkan aktivitas sosial yang positif"
      ]
    } else if (totalScore >= 5 && totalScore <= 9) {
      severity = "Mild"
      description = "Anda mengalami gejala kecemasan ringan. Hal ini umum terjadi dan dapat dikelola dengan perubahan gaya hidup dan teknik self-care."
      recommendations = [
        "Pelajari teknik pernapasan dan mindfulness",
        "Batasi konsumsi kafein dan alkohol",
        "Bicarakan perasaan Anda dengan orang terdekat",
        "Pertimbangkan untuk berkonsultasi dengan counselor"
      ]
    } else if (totalScore >= 10 && totalScore <= 14) {
      severity = "Moderate"
      description = "Anda mengalami gejala kecemasan sedang. Sangat disarankan untuk mencari bantuan profesional untuk mendapatkan strategi pengelolaan yang tepat."
      recommendations = [
        "Konsultasi dengan psikolog atau counselor",
        "Pertimbangkan terapi CBT (Cognitive Behavioral Therapy)",
        "Gabung dengan support group",
        "Evaluasi faktor stress dalam hidup Anda"
      ]
    } else {
      severity = "Severe"
      description = "Anda mengalami gejala kecemasan yang cukup parah. Sangat penting untuk segera mencari bantuan profesional."
      recommendations = [
        "Segera konsultasi dengan psikiater atau psikolog",
        "Pertimbangkan terapi intensif",
        "Diskusikan kemungkinan medikasi dengan dokter",
        "Libatkan keluarga dalam proses pemulihan"
      ]
    }
  } else if (currentAssessment.value.type === 'depression') {
    if (totalScore >= 0 && totalScore <= 4) {
      severity = "Minimal"
      description = "Tingkat depresi Anda minimal. Ini menunjukkan kondisi mental yang sehat. Terus jaga kesehatan mental dengan pola hidup positif."
      recommendations = [
        "Pertahankan aktivitas yang memberi Anda kegembiraan",
        "Jaga koneksi sosial dengan keluarga dan teman",
        "Lakukan aktivitas fisik teratur",
        "Praktikkan rasa syukur harian"
      ]
    } else if (totalScore >= 5 && totalScore <= 9) {
      severity = "Mild"
      description = "Anda mengalami gejala depresi ringan. Ini bisa diatasi dengan perubahan gaya hidup dan dukungan sosial yang tepat."
      recommendations = [
        "Buat jadwal harian yang terstruktur",
        "Lakukan aktivitas yang dulu Anda nikmati",
        "Berbagi perasaan dengan orang terdekat",
        "Pertimbangkan konseling untuk dukungan tambahan"
      ]
    } else if (totalScore >= 10 && totalScore <= 14) {
      severity = "Moderate"
      description = "Anda mengalami gejala depresi sedang. Sangat disarankan untuk mencari bantuan profesional untuk mendapatkan perawatan yang sesuai."
      recommendations = [
        "Konsultasi dengan psikolog atau psikiater",
        "Pertimbangkan terapi kognitif behavioral",
        "Evaluasi pola tidur dan nutrisi",
        "Pertimbangkan untuk bergabung dengan support group"
      ]
    } else if (totalScore >= 15 && totalScore <= 19) {
      severity = "Moderately Severe"
      description = "Anda mengalami gejala depresi yang cukup parah. Penting untuk segera mendapatkan bantuan profesional."
      recommendations = [
        "Segera konsultasi dengan psikiater",
        "Pertimbangkan kombinasi terapi dan medikasi",
        "Libatkan sistem dukungan keluarga",
        "Monitor gejala secara teratur dengan profesional"
      ]
    } else {
      severity = "Severe" 
      description = "Anda mengalami gejala depresi berat. Sangat penting untuk segera mendapatkan perawatan intensif dari profesional kesehatan mental."
      recommendations = [
        "Segera konsultasi dengan psikiater",
        "Pertimbangkan perawatan intensif atau rawat inap",
        "Jangan tinggalkan diri Anda sendirian",
        "Hubungi hotline krisis jika diperlukan: 119 ext 8"
      ]
    }
  }
  
  assessmentResult.value = {
    score: totalScore,
    maxScore,
    severity,
    description,
    recommendations,
    date: new Date(),
    type: currentAssessment.value.type
  }
  
  currentAssessment.value = null
}

const exitAssessment = () => {
  if (confirm('Apakah Anda yakin ingin keluar? Progress akan hilang.')) {
    currentAssessment.value = null
    assessmentResult.value = null
    currentQuestionIndex.value = 0
    selectedAnswer.value = null
    assessmentAnswers.value = []
  }
}

const getResultIcon = (severity) => {
  switch (severity) {
    case 'Minimal': return CheckCircle
    case 'Mild': return Shield
    case 'Moderate': return AlertCircle
    case 'Moderately Severe': return AlertOctagon
    case 'Severe': return AlertOctagon
    default: return CheckCircle
  }
}

const getResultIconBg = (severity) => {
  switch (severity) {
    case 'Minimal': return 'bg-green-100'
    case 'Mild': return 'bg-yellow-100'
    case 'Moderate': return 'bg-orange-100'
    case 'Moderately Severe': return 'bg-red-100'
    case 'Severe': return 'bg-red-100'
    default: return 'bg-gray-100'
  }
}

const getResultIconColor = (severity) => {
  switch (severity) {
    case 'Minimal': return 'text-green-600'
    case 'Mild': return 'text-yellow-600'
    case 'Moderate': return 'text-orange-600'
    case 'Moderately Severe': return 'text-red-600'
    case 'Severe': return 'text-red-600'
    default: return 'text-gray-600'
  }
}

const getResultBadgeStyle = (severity) => {
  switch (severity) {
    case 'Minimal': return 'bg-green-100 text-green-800'
    case 'Mild': return 'bg-yellow-100 text-yellow-800'
    case 'Moderate': return 'bg-orange-100 text-orange-800'
    case 'Moderately Severe': return 'bg-red-100 text-red-800'
    case 'Severe': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getScoreBarColor = (severity) => {
  switch (severity) {
    case 'Minimal': return 'bg-green-500'
    case 'Mild': return 'bg-yellow-500'
    case 'Moderate': return 'bg-orange-500'
    case 'Moderately Severe': return 'bg-red-500'
    case 'Severe': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
}

const talkToAI = () => {
  navigateTo('/application/chatbot?context=assessment')
}

const saveResult = () => {
  // Save to local storage or API
  const newResult = {
    id: Date.now(),
    type: getAssessmentTitle(assessmentResult.value.type),
    date: new Date(),
    severity: assessmentResult.value.severity,
    score: assessmentResult.value.score,
    maxScore: assessmentResult.value.maxScore
  }
  
  assessmentHistory.value.unshift(newResult)
  
  // Save to localStorage for persistence
  localStorage.setItem('mindcare-assessments', JSON.stringify(assessmentHistory.value))
  
  assessmentResult.value = null
}

const retakeAssessment = () => {
  assessmentResult.value = null
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date)
}
</script>

<style scoped>
.ml-13 {
  margin-left: 3.25rem;
}
</style> 