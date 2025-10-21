<template>
  <div
    class="message-bubble-container"
    :class="[
      'flex',
      message.sender === 'user' ? 'justify-end' : 'justify-start'
    ]"
    v-motion
    :initial="message.sender === 'user' ?
      { opacity: 0, x: 50, scale: 0.9 } :
      { opacity: 0, x: -50, scale: 0.9 }
    "
    :enter="{
      opacity: 1,
      x: 0,
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
        delay: index * 100
      }
    }"
  >
    <div
      class="message-bubble max-w-xs sm:max-w-md lg:max-w-lg"
      :class="[
        message.sender === 'user'
          ? 'user-message'
          : 'ai-message',
        { 'message-error': message.error }
      ]"
      v-motion
      :hover="{
        scale: 1.02,
        y: -2,
        transition: { duration: 0.2 }
      }"
    >
      <!-- AI Message -->
      <div v-if="message.sender === 'ai'" class="flex items-start space-x-2">
        <div
          class="ai-avatar flex-shrink-0"
          v-motion
          :initial="{ scale: 0, rotate: -180 }"
          :enter="{
            scale: 1,
            rotate: 0,
            transition: {
              type: 'spring',
              stiffness: 400,
              damping: 25,
              delay: (index * 100) + 200
            }
          }"
        >
          <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <Bot class="w-4 h-4 text-white" />
          </div>
        </div>

        <div class="flex-1">
          <div class="bg-white dark:bg-gray-700 rounded-2xl rounded-tl-md p-4 shadow-sm border border-gray-200 dark:border-gray-600">
            <!-- Message content with markdown rendering -->
            <div class="message-content">
              <div v-if="message.isStreaming" class="text-gray-800 dark:text-gray-200 leading-relaxed markdown-content">
                <!-- Show placeholder text if no content yet -->
                <div v-if="!message.text || message.text.trim() === ''" class="flex items-center space-x-2 text-gray-500 dark:text-gray-400 italic">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                  <span>{{ $t('chat.thinking', 'AI is thinking...') }}</span>
                </div>
                <!-- Show actual content with cursor when streaming -->
                <div v-else>
                  <span v-html="renderedMarkdown"></span><span class="cursor-blink">|</span>
                </div>
              </div>
              <div v-else class="text-gray-800 dark:text-gray-200 leading-relaxed markdown-content">
                <span v-html="renderedMarkdown"></span>
              </div>
            </div>


            <!-- Sentiment Analysis Visualization -->
            <div v-if="message.sentiment && !message.isStreaming" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Analysis</span>
                <div class="flex items-center space-x-2">
                  <!-- Sentiment Badge -->
                  <Badge
                    :variant="getSentimentBadgeVariant(message.sentiment)"
                    class="text-xs"
                  >
                    {{ getSentimentText(message.sentiment) }}
                  </Badge>

                  <!-- Emotion Badge -->
                  <Badge
                    v-if="getEmotion(message.sentiment)"
                    variant="outline"
                    class="text-xs text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800"
                  >
                    {{ getEmotion(message.sentiment) }}
                  </Badge>
                </div>
              </div>

              <!-- Interactive Details with Tooltip -->
              <div class="group relative">
                <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 cursor-help hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
                  <span>Hover for details</span>
                  <div class="flex items-center space-x-3">
                    <!-- Confidence Progress -->
                    <div v-if="getConfidence(message.sentiment)" class="flex items-center space-x-2">
                      <Progress
                        :value="getConfidence(message.sentiment) * 100"
                        class="w-12 h-1"
                      />
                      <span class="text-xs font-medium">{{ Math.round(getConfidence(message.sentiment) * 100) }}%</span>
                    </div>

                    <!-- Crisis Risk Badge -->
                    <Badge
                      v-if="getCrisisRisk(message.sentiment)"
                      :variant="getCrisisRiskBadgeVariant(getCrisisRisk(message.sentiment))"
                      class="text-xs"
                    >
                      {{ getCrisisRisk(message.sentiment) }}
                    </Badge>
                  </div>
                </div>

                <!-- Detailed Tooltip -->
                <div class="absolute bottom-full left-0 mb-2 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 min-w-48">
                  <div class="space-y-2 text-xs">
                    <div class="flex justify-between items-center">
                      <span class="text-gray-600 dark:text-gray-400">Sentiment:</span>
                      <Badge :variant="getSentimentBadgeVariant(message.sentiment)" class="text-xs">
                        {{ getSentimentText(message.sentiment) }}
                      </Badge>
                    </div>
                    <div v-if="getEmotion(message.sentiment)" class="flex justify-between items-center">
                      <span class="text-gray-600 dark:text-gray-400">Emotion:</span>
                      <Badge variant="outline" class="text-xs text-purple-600 dark:text-purple-400">
                        {{ getEmotion(message.sentiment) }}
                      </Badge>
                    </div>
                    <div v-if="getConfidence(message.sentiment)" class="flex justify-between items-center">
                      <span class="text-gray-600 dark:text-gray-400">Confidence:</span>
                      <span class="font-medium text-green-600 dark:text-green-400">
                        {{ Math.round(getConfidence(message.sentiment) * 100) }}%
                      </span>
                    </div>
                    <div v-if="getCrisisRisk(message.sentiment)" class="flex justify-between items-center">
                      <span class="text-gray-600 dark:text-gray-400">Crisis Risk:</span>
                      <Badge :variant="getCrisisRiskBadgeVariant(getCrisisRisk(message.sentiment))" class="text-xs">
                        {{ getCrisisRisk(message.sentiment) }}
                      </Badge>
                    </div>
                    <div v-if="message.isCrisis !== undefined" class="flex justify-between items-center">
                      <span class="text-gray-600 dark:text-gray-400">Is Crisis:</span>
                      <Badge :variant="message.isCrisis ? 'destructive' : 'default'" class="text-xs">
                        {{ message.isCrisis ? 'Yes' : 'No' }}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Message actions -->
            <div
              v-if="!message.isStreaming && !message.error"
              class="flex items-center justify-between mt-3"
              v-motion
              :initial="{ opacity: 0, y: 10 }"
              :enter="{
                opacity: 1,
                y: 0,
                transition: {
                  delay: 500,
                  duration: 300
                }
              }"
            >
              <div class="flex items-center space-x-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button
                        variant="ghost"
                        size="sm"
                        @click="likeMessage"
                        class="h-7 w-7 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600"
                        :class="{ 'text-red-500': message.liked }"
                      >
                        <Heart class="w-3 h-3" :fill="message.liked ? 'currentColor' : 'none'" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{{ message.liked ? 'Unlike' : 'Like' }} message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Button
                        variant="ghost"
                        size="sm"
                        @click="copyMessage"
                        class="h-7 w-7 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600"
                      >
                        <Copy class="w-3 h-3" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Copy message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>

              <Badge variant="outline" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatTime(message.timestamp) }}
              </Badge>
            </div>

            <!-- Error state -->
            <div v-if="message.error" class="mt-2">
              <Badge variant="destructive" class="text-xs">
                {{ message.error }}
              </Badge>
            </div>

            <!-- Assessment Questions -->
            <div v-if="message.assessmentQuestions && message.assessmentQuestions.length > 0 && !message.isStreaming" class="mt-4">
              <AssessmentQuestion
                v-for="(question, index) in message.assessmentQuestions"
                :key="`${message.id}-question-${index}`"
                :question="question"
                :progress="message.assessmentProgress"
                :show-skip-button="index === 0"
                @answer="handleAssessmentAnswer"
                @skip="handleAssessmentSkip"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- User Message -->
      <div v-else class="flex justify-end">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-tr-md p-4 shadow-sm max-w-full">
          <div class="text-sm leading-relaxed break-words">
            {{ message.text }}
          </div>

          <div class="flex items-center justify-between mt-2">
            <div class="flex items-center space-x-1">
              <Check v-if="message.status === 'sent'" class="w-3 h-3 text-blue-200" />
              <CheckCheck v-if="message.status === 'delivered'" class="w-3 h-3 text-blue-200" />
              <Loader2 v-if="message.status === 'sending'" class="w-3 h-3 text-blue-200 animate-spin" />
            </div>
            <span class="text-xs text-blue-100">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from '@/components/ui/tooltip'
import { Bot, Heart, Copy, Check, CheckCheck, Loader2 } from 'lucide-vue-next'
import TypewriterText from './TypewriterText.vue'
import AssessmentQuestion from './AssessmentQuestion.vue'

interface Message {
  id: string
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered'
  liked?: boolean
  isStreaming?: boolean
  error?: string
  sentiment?: any
  isCrisis?: boolean
  problemCategory?: string
  suggestions?: any
  assessmentQuestions?: any[]
  showAssessmentTransition?: boolean
  contextAnalysis?: any
  assessmentProgress?: {
    current: number
    total: number
  }
}

interface Props {
  message: Message
  index: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  like: [messageId: string]
  copy: [text: string]
  typingComplete: [messageId: string]
  assessmentAnswer: [questionId: string, answer: any]
  assessmentSkip: [questionId: string]
}>()

// I18n
const { t } = useI18n()

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true,
})

// Computed property to render markdown to HTML
const renderedMarkdown = computed(() => {
  if (!props.message.text) return ''

  try {
    // For streaming messages, we might want to handle incomplete markdown differently
    if (props.message.isStreaming) {
      // For streaming, we'll render what we have and let it update as more content arrives
      return marked(props.message.text)
    } else {
      // For complete messages, render the full markdown
      return marked(props.message.text)
    }
  } catch (error) {
    console.error('Error rendering markdown:', error)
    return props.message.text // Fallback to plain text
  }
})

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const likeMessage = () => {
  emit('like', props.message.id)
}

const copyMessage = () => {
  emit('copy', props.message.text)
}

const onTypingComplete = () => {
  emit('typingComplete', props.message.id)
}

const handleAssessmentAnswer = (questionId: string, answer: any) => {
  emit('assessmentAnswer', questionId, answer)
}

const handleAssessmentSkip = (questionId: string) => {
  emit('assessmentSkip', questionId)
}

// Helper functions for sentiment analysis display
const getSentimentColor = (sentiment: any): string => {
  const sentimentValue = typeof sentiment === 'string' ? sentiment : sentiment?.sentiment || sentiment;

  if (!sentimentValue || typeof sentimentValue !== 'string') {
    return 'bg-blue-500 text-blue-600 dark:text-blue-400';
  }

  switch (sentimentValue.toLowerCase()) {
    case 'positive':
      return 'bg-green-500 text-green-600 dark:text-green-400';
    case 'negative':
      return 'bg-red-500 text-red-600 dark:text-red-400';
    case 'neutral':
      return 'bg-gray-500 text-gray-600 dark:text-gray-400';
    default:
      return 'bg-blue-500 text-blue-600 dark:text-blue-400';
  }
};

const getSentimentText = (sentiment: any): string => {
  const sentimentValue = typeof sentiment === 'string' ? sentiment : sentiment?.sentiment || sentiment;
  return sentimentValue || 'unknown';
};

const getEmotion = (sentiment: any): string => {
  return sentiment?.emotion || null;
};

const getConfidence = (sentiment: any): number => {
  return sentiment?.confidence || null;
};

const getCrisisRisk = (sentiment: any): string => {
  return sentiment?.crisis_risk || null;
};

const getCrisisRiskColor = (risk: string): string => {
  if (!risk || typeof risk !== 'string') {
    return 'bg-gray-500 text-gray-600 dark:text-gray-400';
  }

  switch (risk.toLowerCase()) {
    case 'high':
      return 'bg-red-500 text-red-600 dark:text-red-400';
    case 'medium':
      return 'bg-yellow-500 text-yellow-600 dark:text-yellow-400';
    case 'low':
      return 'bg-green-500 text-green-600 dark:text-green-400';
    default:
      return 'bg-gray-500 text-gray-600 dark:text-gray-400';
  }
};

// New helper functions for shadcn/vue badge variants
const getSentimentBadgeVariant = (sentiment: any): 'default' | 'secondary' | 'destructive' | 'outline' => {
  const sentimentValue = typeof sentiment === 'string' ? sentiment : sentiment?.sentiment || sentiment;

  if (!sentimentValue || typeof sentimentValue !== 'string') {
    return 'secondary';
  }

  switch (sentimentValue.toLowerCase()) {
    case 'positive':
      return 'default';
    case 'negative':
      return 'destructive';
    case 'neutral':
      return 'secondary';
    default:
      return 'outline';
  }
};

const getCrisisRiskBadgeVariant = (risk: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  if (!risk || typeof risk !== 'string') {
    return 'secondary';
  }

  switch (risk.toLowerCase()) {
    case 'high':
      return 'destructive';
    case 'medium':
      return 'default';
    case 'low':
      return 'secondary';
    default:
      return 'outline';
  }
};
</script>

<style scoped>
.message-bubble-container {
  @apply mb-4;
}

.message-bubble {
  @apply transition-all duration-200;
}

.user-message {
  @apply flex justify-end;
}

.ai-message {
  @apply flex items-start space-x-2;
}

.message-error {
  @apply border-red-200 dark:border-red-800;
}

/* Enhanced hover effects */
.message-bubble:hover {
  @apply shadow-md;
}

/* Smooth transitions for all interactive elements */
.message-bubble * {
  transition: all 0.2s ease;
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .message-bubble {
    transition: none;
  }

  .message-bubble:hover {
    transform: none;
  }
}

/* Focus states for accessibility */
.message-bubble:focus-within {
  @apply ring-2 ring-blue-500 ring-offset-2 rounded-lg;
}

/* Blinking cursor for streaming text */
.cursor-blink {
  animation: blink 1s infinite;
  color: #3b82f6;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Markdown content styling */
.markdown-content {
  /* Headings */
  h1, h2, h3, h4, h5, h6 {
    @apply font-semibold mt-4 mb-2;
  }

  h1 { @apply text-xl; }
  h2 { @apply text-lg; }
  h3 { @apply text-base; }

  /* Paragraphs */
  p {
    @apply mb-2;
  }

  /* Lists */
  ul, ol {
    @apply ml-4 mb-2;
  }

  li {
    @apply mb-1;
  }

  /* Code */
  code {
    @apply bg-gray-100 dark:bg-gray-600 px-1 py-0.5 rounded text-sm font-mono;
  }

  pre {
    @apply bg-gray-100 dark:bg-gray-600 p-3 rounded-lg overflow-x-auto mb-2;
  }

  pre code {
    @apply bg-transparent p-0;
  }

  /* Blockquotes */
  blockquote {
    @apply border-l-4 border-gray-300 dark:border-gray-500 pl-4 italic mb-2;
  }

  /* Links */
  a {
    @apply text-blue-600 dark:text-blue-400 hover:underline;
  }

  /* Strong and emphasis */
  strong {
    @apply font-semibold;
  }

  em {
    @apply italic;
  }

  /* Tables */
  table {
    @apply border-collapse border border-gray-300 dark:border-gray-600 mb-2;
  }

  th, td {
    @apply border border-gray-300 dark:border-gray-600 px-2 py-1;
  }

  th {
    @apply bg-gray-100 dark:bg-gray-700 font-semibold;
  }

  /* Horizontal rules */
  hr {
    @apply border-t border-gray-300 dark:border-gray-600 my-4;
  }
}
</style>
