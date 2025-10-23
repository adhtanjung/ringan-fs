<template>
  <div class="assessment-question-container bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 mt-3 border border-blue-200 dark:border-blue-700">
    <!-- Assessment Header -->
    <div class="flex items-center space-x-2 mb-3">
      <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
        <ClipboardCheck class="w-3 h-3 text-white" />
      </div>
      <span class="text-sm font-medium text-blue-800 dark:text-blue-200">
        {{ $t('assessment.title', 'Assessment Question') }}
      </span>
      <div v-if="progress" class="ml-auto text-xs text-blue-600 dark:text-blue-300">
        {{ progress.current }}/{{ progress.total }}
      </div>
    </div>

    <!-- Question Text -->
    <div class="mb-4">
      <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
        {{ question.question_text }}
      </h3>
      <p v-if="question.subtitle" class="text-xs text-gray-600 dark:text-gray-400">
        {{ question.subtitle }}
      </p>
    </div>

    <!-- Response Type: Scale (1-4) -->
    <div v-if="question.response_type === 'scale'" class="space-y-3">
      <div class="text-xs text-gray-600 dark:text-gray-400 mb-2">
        {{ $t('assessment.scale.instruction', 'Pilih jawaban yang paling sesuai:') }}
      </div>
      <div class="grid grid-cols-1 gap-2">
        <button
          v-for="(label, value) in getScaleLabels(question)"
          :key="value"
          @click="selectScaleValue(parseInt(value))"
          :class="[
            'p-3 text-left rounded-xl border-2 transition-all',
            selectedValue === parseInt(value)
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div :class="[
              'w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold',
              selectedValue === parseInt(value)
                ? 'border-blue-500 bg-blue-500 text-white'
                : 'border-gray-400 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            ]">
              {{ value }}
            </div>
            <span class="text-sm font-medium text-gray-900 dark:text-white">{{ label }}</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Response Type: Multiple Choice -->
    <div v-else-if="question.response_type === 'multiple_choice'" class="space-y-2">
      <button
        v-for="(option, index) in question.response_options"
        :key="index"
        @click="selectMultipleChoice(option)"
        :class="[
          'w-full p-3 text-left rounded-lg border-2 transition-all text-sm',
          selectedValue === option
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100'
            : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500'
        ]"
      >
        <div class="flex items-center space-x-3">
          <div :class="[
            'w-4 h-4 rounded-full border-2 transition-all',
            selectedValue === option
              ? 'border-blue-500 bg-blue-500'
              : 'border-gray-300 dark:border-gray-600'
          ]">
            <div v-if="selectedValue === option" class="w-2 h-2 bg-white rounded-full m-0.5"></div>
          </div>
          <span>{{ option }}</span>
        </div>
      </button>
    </div>

    <!-- Response Type: Yes/No -->
    <div v-else-if="question.response_type === 'yes_no'" class="flex space-x-3">
      <button
        @click="selectYesNo(true)"
        :class="[
          'flex-1 p-3 rounded-lg border-2 transition-all text-sm font-medium',
          selectedValue === true
            ? 'border-green-500 bg-green-50 dark:bg-green-900/30 text-green-900 dark:text-green-100'
            : 'border-gray-200 dark:border-gray-600 hover:border-green-300 dark:hover:border-green-500'
        ]"
      >
        <div class="flex items-center justify-center space-x-2">
          <CheckCircle class="w-4 h-4" />
          <span>{{ $t('assessment.yes', 'Yes') }}</span>
        </div>
      </button>
      <button
        @click="selectYesNo(false)"
        :class="[
          'flex-1 p-3 rounded-lg border-2 transition-all text-sm font-medium',
          selectedValue === false
            ? 'border-red-500 bg-red-50 dark:bg-red-900/30 text-red-900 dark:text-red-100'
            : 'border-gray-200 dark:border-gray-600 hover:border-red-300 dark:hover:border-red-500'
        ]"
      >
        <div class="flex items-center justify-center space-x-2">
          <XCircle class="w-4 h-4" />
          <span>{{ $t('assessment.no', 'No') }}</span>
        </div>
      </button>
    </div>

    <!-- Response Type: Text Input -->
    <div v-else-if="question.response_type === 'text'" class="space-y-3">
      <textarea
        v-model="textResponse"
        :placeholder="$t('assessment.text.placeholder', 'Please share your thoughts...')"
        class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        rows="3"
        @input="handleTextInput"
      ></textarea>
      <div class="text-xs text-gray-500 dark:text-gray-400">
        {{ $t('assessment.text.instruction', 'Share as much or as little as you feel comfortable with') }}
      </div>
    </div>

    <!-- Submit Button -->
    <div class="mt-4 flex space-x-2">
      <button
        v-if="showSkipButton"
        @click="skipQuestion"
        class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
      >
        {{ $t('assessment.skip', 'Skip') }}
      </button>
      <button
        @click="submitAnswer"
        :disabled="!hasValidAnswer"
        :class="[
          'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all',
          hasValidAnswer
            ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
        ]"
      >
        {{ $t('assessment.submit', 'Submit Answer') }}
        <ArrowRight class="w-3 h-3 ml-1 inline" />
      </button>
    </div>

    <!-- Assessment Progress Bar -->
    <div v-if="progress" class="mt-3">
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
        <div
          class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
          :style="{ width: `${(progress.current / progress.total) * 100}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ClipboardCheck,
  CheckCircle,
  XCircle,
  ArrowRight
} from 'lucide-vue-next'

interface AssessmentQuestion {
  question_id: string
  question_text: string
  response_type: 'scale' | 'multiple_choice' | 'yes_no' | 'text'
  response_options?: string[]
  subtitle?: string
  category?: string
  scale_labels?: { [key: string]: string }
}

interface AssessmentProgress {
  current: number
  total: number
}

interface Props {
  question: AssessmentQuestion
  progress?: AssessmentProgress
  showSkipButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showSkipButton: true
})

const emit = defineEmits<{
  answer: [questionId: string, answer: any]
  skip: [questionId: string]
}>()

const { t } = useI18n()

// State
const selectedValue = ref<any>(null)
const textResponse = ref('')

// Computed
const hasValidAnswer = computed(() => {
  if (props.question.response_type === 'text') {
    return textResponse.value.trim().length > 0
  }
  return selectedValue.value !== null
})

// Methods
const selectScaleValue = (value: number) => {
  selectedValue.value = value
}

const selectMultipleChoice = (option: string) => {
  selectedValue.value = option
}

const selectYesNo = (value: boolean) => {
  selectedValue.value = value
}

const getScaleLabels = (question: AssessmentQuestion) => {
  // Return scale labels from question or defaults
  if (question && (question as any).scale_labels) {
    return (question as any).scale_labels;
  }
  // Default labels
  return {
    "1": "Not at all",
    "2": "A little",
    "3": "Quite a bit",
    "4": "Very much"
  };
};

const handleTextInput = () => {
  // Text input is handled by v-model
}

const submitAnswer = () => {
  if (!hasValidAnswer.value) return

  const answer = props.question.response_type === 'text'
    ? textResponse.value.trim()
    : selectedValue.value

  console.log('🔍 AssessmentQuestion submitAnswer:', {
    question: props.question,
    questionId: props.question.question_id,
    questionKeys: Object.keys(props.question),
    allQuestionFields: props.question,
    answer: answer,
    answerType: typeof answer
  });

  // Try different possible field names for question ID
  let questionId = props.question.question_id || props.question.id || props.question.questionId || '';

  // If no question ID found, generate one based on question text or use a fallback
  if (!questionId) {
    questionId = props.question.question_text ?
      `q_${props.question.question_text.substring(0, 20).replace(/\s+/g, '_').toLowerCase()}` :
      `q_${Date.now()}`;
    console.warn('⚠️ No question ID found, generated:', questionId);
  }

  console.log('🔍 Using question ID:', questionId);

  emit('answer', questionId, answer)
}

const skipQuestion = () => {
  // Try different possible field names for question ID
  let questionId = props.question.question_id || props.question.id || props.question.questionId || '';

  // If no question ID found, generate one based on question text or use a fallback
  if (!questionId) {
    questionId = props.question.question_text ?
      `q_${props.question.question_text.substring(0, 20).replace(/\s+/g, '_').toLowerCase()}` :
      `q_${Date.now()}`;
  }

  emit('skip', questionId)
}
</script>

<style scoped>
.assessment-question-container {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
