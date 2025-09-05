<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <!-- Loading State -->
    <div v-if="!isClient" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col h-screen">
      <!-- Enhanced Header -->
      <header 
        class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40"
        role="banner"
        aria-label="AI Mental Health Counselor Header"
      >
        <div class="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div class="flex items-center justify-between">
            <!-- AI Counselor Info -->
            <div class="flex items-center space-x-2 sm:space-x-3 flex-1 min-w-0">
              <div class="relative flex-shrink-0">
                <div 
                  class="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center"
                  aria-hidden="true"
                >
                  <Bot class="w-4 h-4 sm:w-6 sm:h-6 text-white" />
                </div>
                <div 
                  class="absolute -bottom-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"
                  aria-label="Online status indicator"
                  role="status"
                ></div>
              </div>
              <div class="min-w-0 flex-1">
                <h1 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white truncate">{{ safeT('header.title', 'AI Mental Health Counselor') }}</h1>
                <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-300 truncate" aria-live="polite">{{ safeT('header.subtitle', 'Your compassionate AI companion') }}</p>
              </div>
            </div>

            <!-- Header Actions -->
            <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0" role="toolbar" aria-label="Header actions">
              <!-- Language Switcher -->
              <button
                @click="switchLanguage"
                class="p-1.5 sm:p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                :title="safeT('actions.switchLanguage', 'Switch Language')"
                :aria-label="safeT('actions.switchLanguage', 'Switch Language')"
                type="button"
              >
                <Globe class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" aria-hidden="true" />
              </button>

              <!-- Settings Menu -->
              <div class="relative" ref="menuContainer">
                <button
                  @click="showMenu = !showMenu"
                  class="p-1.5 sm:p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :title="safeT('actions.menu', 'Menu')"
                  :aria-label="safeT('actions.menu', 'Menu')"
                  :aria-expanded="showMenu"
                  :aria-haspopup="true"
                  type="button"
                >
                  <MoreVertical class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" aria-hidden="true" />
                </button>

                <!-- Dropdown Menu -->
                <div
                  v-if="showMenu"
                  v-motion
                  :initial="{ opacity: 0, y: -10 }"
                  :enter="{ opacity: 1, y: 0 }"
                  :leave="{ opacity: 0, y: -10 }"
                  class="absolute right-0 mt-2 w-48 sm:w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="menu-button"
                >
                  <div class="py-2">
                    <button
                      @click="clearChat"
                      class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
                      role="menuitem"
                      type="button"
                    >
                      <Trash2 class="w-4 h-4" aria-hidden="true" />
                      <span>{{ safeT('menu.clearChat', 'Clear Chat History') }}</span>
                    </button>
                    <button
                      @click="exportConversation"
                      class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
                      role="menuitem"
                      type="button"
                    >
                      <Download class="w-4 h-4" aria-hidden="true" />
                      <span>{{ safeT('menu.export', 'Export Conversation') }}</span>
                    </button>
                    <button
                      @click="showPrivacySettings = true"
                      class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700"
                      role="menuitem"
                      type="button"
                    >
                      <Settings class="w-4 h-4" aria-hidden="true" />
                      <span>{{ safeT('menu.privacy', 'Privacy Settings') }}</span>
                    </button>
                    <hr class="my-2 border-gray-200 dark:border-gray-700" role="separator" />
                    <button
                      @click="showEmergencyInfo = true"
                      class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center space-x-2 focus:outline-none focus:bg-red-50 dark:focus:bg-red-900/20"
                      role="menuitem"
                      type="button"
                    >
                      <Phone class="w-4 h-4" aria-hidden="true" />
                      <span>{{ safeT('menu.emergency', 'Emergency Help') }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Chat Container -->
      <main class="flex-1 flex flex-col max-w-4xl mx-auto w-full px-3 sm:px-4 py-4 sm:py-6" role="main" aria-label="Chat conversation">
        <!-- Assessment Progress Indicator -->
        <div
          v-if="assessmentProgress?.isActive && showProgressIndicator"
          v-motion
          :initial="{ opacity: 0, y: -20 }"
          :enter="{ opacity: 1, y: 0 }"
          class="mb-3 sm:mb-4 bg-white dark:bg-gray-800 rounded-lg p-3 sm:p-4 border border-gray-200 dark:border-gray-700 shadow-sm"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ safeT('assessment.progress', 'Assessment Progress') }}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ assessmentProgress.currentQuestion }}/{{ assessmentProgress.totalQuestions }}
            </span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              class="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
              :style="{ width: `${assessmentProgress.percentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Messages Container -->
        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto space-y-4 mb-4 scroll-container"
          role="log"
          aria-live="polite"
          aria-label="Chat messages"
          tabindex="0"
        >
          <!-- Welcome Message -->
          <div
            v-if="!hasMessages"
            v-motion
            :initial="{ opacity: 0, y: 50 }"
            :enter="{ opacity: 1, y: 0, transition: { duration: 800, ease: 'easeOut' } }"
            class="text-center py-8"
          >
            <div 
              v-motion
              :initial="{ scale: 0, rotate: -180 }"
              :enter="{ scale: 1, rotate: 0, transition: { delay: 300, duration: 600, ease: 'easeOut' } }"
              :hover="{ scale: 1.1, rotate: 5 }"
              class="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center mx-auto mb-4 cursor-pointer"
            >
              <Heart class="w-8 h-8 text-white" />
            </div>
            <h2 
              v-motion
              :initial="{ opacity: 0, y: 20 }"
              :enter="{ opacity: 1, y: 0, transition: { delay: 500, duration: 500 } }"
              class="text-xl font-semibold text-gray-900 dark:text-white mb-2"
            >
              {{ safeT('welcome.title', 'Welcome to Your Safe Space') }}
            </h2>
            <p 
              v-motion
              :initial="{ opacity: 0, y: 20 }"
              :enter="{ opacity: 1, y: 0, transition: { delay: 700, duration: 500 } }"
              class="text-gray-600 dark:text-gray-300 max-w-md mx-auto"
            >
              {{ safeT('welcome.subtitle', 'I\'m here to listen and support you. How are you feeling today?') }}
            </p>
          </div>

          <!-- Chat Messages -->
          <div
            v-for="(message, index) in ollamaMessages"
            :key="message.id"
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :enter="{ opacity: 1, y: 0, transition: { delay: index * 100 } }"
            :class="[
              'flex',
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              v-motion
              :hover="{ scale: 1.02, transition: { duration: 200 } }"
              :class="[
                'max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl rounded-2xl px-4 py-3 shadow-sm transition-all duration-200',
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
              ]"
            >
              <!-- Message Content -->
              <div class="space-y-2">
                <!-- Emotion Badge -->
                <div
                  v-if="message.emotionTone && message.sender === 'user'"
                  class="flex items-center space-x-1 mb-2"
                >
                  <span class="text-xs opacity-75">{{ getEmotionEmoji(message.emotionTone) }}</span>
                  <span class="text-xs opacity-75 capitalize">{{ message.emotionTone }}</span>
                </div>

                <!-- Message Text -->
                <div v-if="message.isStreaming" class="flex items-center space-x-2">
                  <TypewriterText :text="message.text" :speed="50" />
                  <TypingIndicator />
                </div>
                <div v-else>
                  <p class="whitespace-pre-wrap">{{ message.text }}</p>
                </div>

                <!-- Message Actions -->
                <div 
                  v-if="!message.isStreaming && message.sender === 'ai'" 
                  v-motion
                  :initial="{ opacity: 0, y: 10 }"
                  :enter="{ opacity: 1, y: 0, transition: { delay: 300 } }"
                  class="flex items-center space-x-2 mt-2"
                >
                  <button
                    @click="likeMessage(message.id)"
                    v-motion
                    :hover="{ scale: 1.1, rotate: 5 }"
                    :tap="{ scale: 0.9 }"
                    class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    :class="{ 'text-red-500': message.liked }"
                  >
                    <Heart class="w-4 h-4" :fill="message.liked ? 'currentColor' : 'none'" />
                  </button>
                  <button
                    @click="copyMessage(message.text)"
                    v-motion
                    :hover="{ scale: 1.1, rotate: -5 }"
                    :tap="{ scale: 0.9 }"
                    class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Copy class="w-4 h-4" />
                  </button>
                </div>

                <!-- Timestamp -->
                <div class="text-xs opacity-60 mt-1">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Typing Indicator for AI -->
          <div
            v-if="ollamaIsProcessing || ollamaIsStreaming"
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :enter="{ opacity: 1, y: 0 }"
            class="flex justify-start"
          >
            <div class="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 shadow-sm border border-gray-200 dark:border-gray-700">
              <TypingIndicator />
            </div>
          </div>
        </div>

        <!-- Quick Response Options -->
        <div
          v-if="showQuickResponses && quickResponseOptions.length > 0"
          v-motion
          :initial="{ opacity: 0, scale: 0.9, y: 20 }"
          :enter="{ opacity: 1, scale: 1, y: 0, transition: { duration: 300, ease: 'easeOut' } }"
          :leave="{ opacity: 0, scale: 0.9, y: -20, transition: { duration: 200 } }"
          class="mb-3 sm:mb-4"
        >
          <div class="flex flex-wrap gap-1.5 sm:gap-2">
            <button
              v-for="(option, index) in quickResponseOptions"
              :key="option.id"
              @click="selectQuickResponse(option)"
              v-motion
              :initial="{ opacity: 0, x: -30 }"
              :enter="{ opacity: 1, x: 0, transition: { delay: index * 100 + 200 } }"
              :hover="{ scale: 1.05, y: -2 }"
              :tap="{ scale: 0.95 }"
              class="px-2.5 sm:px-3 py-1.5 sm:py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-xs sm:text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm"
            >
              {{ option.text }}
            </button>
          </div>
        </div>

        <!-- Emotion Wheel -->
        <div
          v-if="showEmotionWheel"
          v-motion
          :initial="{ opacity: 0, scale: 0.9 }"
          :enter="{ opacity: 1, scale: 1 }"
          class="mb-3 sm:mb-4 bg-white dark:bg-gray-800 rounded-lg p-3 sm:p-4 border border-gray-200 dark:border-gray-700"
          role="region"
          aria-labelledby="emotion-wheel-title"
        >
          <h3 id="emotion-wheel-title" class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 sm:mb-3">
            {{ safeT('emotions.title', 'How are you feeling?') }}
          </h3>
          <div class="grid grid-cols-3 sm:grid-cols-4 gap-1.5 sm:gap-2" role="radiogroup" aria-labelledby="emotion-wheel-title">
            <button
              v-for="emotion in emotionOptions"
              :key="emotion.id"
              @click="selectEmotion(emotion)"
              v-motion
              :initial="{ scale: 0.8, opacity: 0 }"
              :enter="{ scale: 1, opacity: 1, transition: { delay: emotion.id.length * 50 } }"
              :hover="{ scale: 1.05 }"
              :tap="{ scale: 0.95 }"
              :class="[
                'p-2 sm:p-3 rounded-lg border-2 transition-all duration-200 text-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                selectedEmotion === emotion.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              ]"
              :aria-label="`Select ${emotion.label} emotion`"
              :aria-pressed="selectedEmotion === emotion.id"
              role="radio"
              :aria-checked="selectedEmotion === emotion.id"
              type="button"
            >
              <div class="text-xl sm:text-2xl mb-0.5 sm:mb-1" aria-hidden="true">{{ emotion.emoji }}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">{{ emotion.label }}</div>
            </button>
          </div>
          
          <!-- Emotion Intensity Slider -->
          <div v-if="selectedEmotion" class="mt-4">
            <label for="emotion-intensity" class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              {{ safeT('emotions.intensity', 'How intense is this feeling?') }} ({{ emotionIntensity }}/10)
            </label>
            <input
              id="emotion-intensity"
              v-model="emotionIntensity"
              type="range"
              min="1"
              max="10"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              :aria-label="`Emotion intensity: ${emotionIntensity} out of 10`"
              :aria-valuemin="1"
              :aria-valuemax="10"
              :aria-valuenow="emotionIntensity"
              :aria-valuetext="`${emotionIntensity} out of 10`"
            />
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>{{ safeT('emotions.mild', 'Mild') }}</span>
              <span>{{ safeT('emotions.intense', 'Intense') }}</span>
            </div>
          </div>
        </div>

        <!-- Self-Assessment Panel -->
        <div
          v-if="showAssessment"
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :enter="{ opacity: 1, y: 0 }"
          class="mb-4 bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 shadow-sm"
          role="region"
          aria-labelledby="assessment-title"
        >
          <div class="mb-4">
            <h3 id="assessment-title" class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ safeT('assessment.title', 'Quick Self-Assessment') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">
              {{ safeT('assessment.subtitle', 'Help us understand how you\'re feeling today') }}
            </p>
          </div>

          <!-- Likert Scale Questions -->
          <div class="space-y-6">
            <div
              v-for="(question, index) in assessmentQuestions"
              :key="question.id"
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0, transition: { delay: index * 200 } }"
              class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0"
            >
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">
                {{ question.text }}
              </h4>
              
              <!-- Likert Scale -->
              <div class="flex items-center justify-between space-x-2">
                <span class="text-xs text-gray-500 dark:text-gray-400 w-16 text-center">
                  {{ safeT('scale.strongly_disagree', 'Strongly Disagree') }}
                </span>
                <div class="flex space-x-2 flex-1 justify-center" role="radiogroup" :aria-labelledby="`question-${question.id}`">
                  <button
                    v-for="value in [1, 2, 3, 4, 5]"
                    :key="value"
                    @click="setAssessmentAnswer(question.id, value)"
                    v-motion
                    :hover="{ scale: 1.1 }"
                    :tap="{ scale: 0.9 }"
                    :class="[
                      'w-10 h-10 rounded-full border-2 flex items-center justify-center text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                      assessmentAnswers[question.id] === value
                        ? 'border-blue-500 bg-blue-500 text-white'
                        : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20'
                    ]"
                    :aria-label="`Rate ${value} out of 5`"
                    :aria-pressed="assessmentAnswers[question.id] === value"
                    role="radio"
                    :aria-checked="assessmentAnswers[question.id] === value"
                    type="button"
                  >
                    {{ value }}
                  </button>
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 w-16 text-center">
                  {{ safeT('scale.strongly_agree', 'Strongly Agree') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Visual Mood Selector -->
          <div class="mt-6">
            <h4 id="mood-selector-title" class="text-sm font-medium text-gray-900 dark:text-white mb-3">
              {{ safeT('mood.title', 'Overall, how would you describe your mood today?') }}
            </h4>
            <div class="grid grid-cols-5 gap-3" role="radiogroup" aria-labelledby="mood-selector-title">
              <button
                v-for="mood in moodOptions"
                :key="mood.id"
                @click="setMoodSelection(mood.id)"
                v-motion
                :initial="{ scale: 0.8, opacity: 0 }"
                :enter="{ scale: 1, opacity: 1, transition: { delay: mood.id * 100 } }"
                :hover="{ scale: 1.1, rotate: 5 }"
                :tap="{ scale: 0.9 }"
                :class="[
                  'p-3 rounded-lg border-2 transition-all duration-200 text-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  selectedMood === mood.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                ]"
                :aria-label="`Select ${mood.label} mood`"
                :aria-pressed="selectedMood === mood.id"
                role="radio"
                :aria-checked="selectedMood === mood.id"
                type="button"
              >
                <div class="text-3xl mb-1" aria-hidden="true">{{ mood.emoji }}</div>
                <div class="text-xs text-gray-600 dark:text-gray-400">{{ mood.label }}</div>
              </button>
            </div>
          </div>

          <!-- Assessment Actions -->
          <div class="flex space-x-3 mt-6" role="group" aria-label="Assessment actions">
            <button
              @click="submitAssessment"
              :disabled="!canSubmitAssessment"
              class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              :aria-label="safeT('assessment.submit', 'Submit Assessment')"
              type="button"
            >
              {{ safeT('assessment.submit', 'Submit Assessment') }}
            </button>
            <button
              @click="showAssessment = false"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              :aria-label="safeT('assessment.cancel', 'Cancel')"
              type="button"
            >
              {{ safeT('assessment.cancel', 'Cancel') }}
            </button>
          </div>
        </div>

        <!-- Input Area -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm" role="region" aria-label="Message input area">
          <!-- Input Controls -->
          <div class="flex items-center p-1.5 sm:p-2 border-b border-gray-200 dark:border-gray-700 space-x-1 sm:space-x-2" role="toolbar" aria-label="Message input tools">
            <button
              @click="toggleEmotionWheel"
              :class="[
                'p-1.5 sm:p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                showEmotionWheel
                  ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              ]"
              :title="safeT('actions.emotions', 'Select Emotion')"
              :aria-label="safeT('actions.emotions', 'Select Emotion')"
              :aria-pressed="showEmotionWheel"
              type="button"
            >
              <Smile class="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
            </button>
            <button
              @click="toggleQuickResponses"
              :class="[
                'p-1.5 sm:p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                showQuickResponses
                  ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              ]"
              :title="safeT('actions.quickResponses', 'Quick Responses')"
              :aria-label="safeT('actions.quickResponses', 'Quick Responses')"
              :aria-pressed="showQuickResponses"
              type="button"
            >
              <Lightbulb class="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
            </button>
            <button
              @click="showAssessment = !showAssessment"
              :class="[
                'p-1.5 sm:p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                showAssessment
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              ]"
              :title="safeT('actions.assessment', 'Self Assessment')"
              :aria-label="safeT('actions.assessment', 'Self Assessment')"
              :aria-pressed="showAssessment"
              type="button"
            >
              <HelpCircle class="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
            </button>
          </div>

          <!-- Text Input -->
          <div class="flex items-end p-3 sm:p-4">
            <div class="flex-1 mr-2 sm:mr-3">
              <label for="message-input" class="sr-only">
                {{ safeT('input.label', 'Type your message') }}
              </label>
              <textarea
                id="message-input"
                v-model="currentMessage"
                @keydown.enter.prevent="handleSendMessage"
                @keydown.escape="currentMessage = ''"
                @input="detectEmotion"
                :placeholder="safeT('input.placeholder', 'Type your message here...')"
                class="w-full resize-none border-0 focus:ring-0 bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm sm:text-base"
                rows="1"
                :disabled="isSending"
                :aria-describedby="isSending ? 'sending-status' : undefined"
              ></textarea>
              <div id="sending-status" class="sr-only" aria-live="polite">
                {{ isSending ? safeT('status.sending', 'Sending message...') : '' }}
              </div>
            </div>
            <button
              @click="handleSendMessage"
              :disabled="!currentMessage.trim() || isSending"
              v-motion
              :hover="{ scale: 1.05 }"
              :tap="{ scale: 0.95 }"
              class="p-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              :aria-label="safeT('actions.send', 'Send message')"
              type="button"
            >
              <Send 
                v-motion
                :initial="{ rotate: 0 }"
                :hover="{ rotate: 15 }"
                class="w-5 h-5" 
                aria-hidden="true"
              />
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- Crisis Alert Modal -->
    <div
      v-if="showCrisisAlert"
      v-motion
      :initial="{ opacity: 0 }"
      :enter="{ opacity: 1, transition: { duration: 300 } }"
      :leave="{ opacity: 0, transition: { duration: 200 } }"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="crisis-alert-title"
      aria-describedby="crisis-alert-description"
    >
      <div
        v-motion
        :initial="{ scale: 0.8, opacity: 0, y: 50 }"
        :enter="{ scale: 1, opacity: 1, y: 0, transition: { delay: 100, duration: 400, ease: 'easeOut' } }"
        :leave="{ scale: 0.8, opacity: 0, y: 50, transition: { duration: 200 } }"
        class="bg-white dark:bg-gray-800 rounded-lg p-4 sm:p-6 max-w-sm sm:max-w-md w-full shadow-2xl"
      >
        <div class="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
          <AlertTriangle class="w-6 h-6 sm:w-8 sm:h-8 text-red-500" aria-hidden="true" />
          <h3 id="crisis-alert-title" class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            {{ safeT('crisis.title', 'Immediate Support Available') }}
          </h3>
        </div>
        <p id="crisis-alert-description" class="text-sm sm:text-base text-gray-600 dark:text-gray-300 mb-4 sm:mb-6">
          {{ safeT('crisis.message', 'I notice you might be going through a difficult time. Please consider reaching out to a mental health professional or crisis helpline.') }}
        </p>
        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3" role="group" aria-label="Crisis alert actions">
          <button
            @click="showEmergencyInfo = true; showCrisisAlert = false"
            class="flex-1 bg-red-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 text-sm sm:text-base"
            :aria-label="safeT('crisis.getHelp', 'Get Help Now')"
            type="button"
          >
            {{ safeT('crisis.getHelp', 'Get Help Now') }}
          </button>
          <button
            @click="showCrisisAlert = false"
            class="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 sm:px-4 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 text-sm sm:text-base"
            :aria-label="safeT('crisis.continue', 'Continue Chat')"
            type="button"
          >
            {{ safeT('crisis.continue', 'Continue Chat') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Emergency Info Modal -->
    <div
      v-if="showEmergencyInfo"
      v-motion
      :initial="{ opacity: 0 }"
      :enter="{ opacity: 1, transition: { duration: 300 } }"
      :leave="{ opacity: 0, transition: { duration: 200 } }"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="emergency-info-title"
    >
      <div
        v-motion
        :initial="{ scale: 0.8, opacity: 0, rotate: -5 }"
        :enter="{ scale: 1, opacity: 1, rotate: 0, transition: { delay: 100, duration: 400, ease: 'easeOut' } }"
        :leave="{ scale: 0.8, opacity: 0, rotate: 5, transition: { duration: 200 } }"
        class="bg-white dark:bg-gray-800 rounded-lg p-4 sm:p-6 max-w-sm sm:max-w-md w-full shadow-2xl"
      >
        <div class="flex items-center justify-between mb-3 sm:mb-4">
          <h3 id="emergency-info-title" class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            {{ safeT('emergency.title', 'Emergency Resources') }}
          </h3>
          <button
            @click="showEmergencyInfo = false"
            class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            :aria-label="safeT('actions.close', 'Close modal')"
            type="button"
          >
            <X class="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
          </button>
        </div>
        <div class="space-y-4" role="list" aria-label="Emergency contact information">
          <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg" role="listitem">
            <h4 class="font-medium text-red-800 dark:text-red-200 mb-2">
              {{ safeT('emergency.crisis', 'Crisis Hotline') }}
            </h4>
            <p class="text-red-700 dark:text-red-300 text-sm mb-2">
              {{ safeT('emergency.crisisDesc', '24/7 crisis support') }}
            </p>
            <a 
              href="tel:119" 
              class="text-red-600 dark:text-red-400 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded"
              :aria-label="safeT('emergency.callCrisis', 'Call crisis hotline at 119')"
            >119</a>
          </div>
          <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg" role="listitem">
            <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">
              {{ safeT('emergency.mental', 'Mental Health Support') }}
            </h4>
            <p class="text-blue-700 dark:text-blue-300 text-sm mb-2">
              {{ safeT('emergency.mentalDesc', 'Professional mental health support') }}
            </p>
            <a 
              href="tel:021-500-454" 
              class="text-blue-600 dark:text-blue-400 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              :aria-label="safeT('emergency.callMental', 'Call mental health support at 021-500-454')"
            >021-500-454</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Privacy Settings Modal -->
    <div
      v-if="showPrivacySettings"
      v-motion
      :initial="{ opacity: 0 }"
      :enter="{ opacity: 1, transition: { duration: 300 } }"
      :leave="{ opacity: 0, transition: { duration: 200 } }"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="privacy-settings-title"
    >
      <div
        v-motion
        :initial="{ scale: 0.9, opacity: 0, y: -30 }"
        :enter="{ scale: 1, opacity: 1, y: 0, transition: { delay: 100, duration: 400, ease: 'easeOut' } }"
        :leave="{ scale: 0.9, opacity: 0, y: 30, transition: { duration: 200 } }"
        class="bg-white dark:bg-gray-800 rounded-lg p-4 sm:p-6 max-w-sm sm:max-w-md w-full shadow-2xl"
      >
        <div class="flex items-center justify-between mb-3 sm:mb-4">
          <h3 id="privacy-settings-title" class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            {{ safeT('privacy.title', 'Privacy Settings') }}
          </h3>
          <button
            @click="showPrivacySettings = false"
            class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            :aria-label="safeT('actions.close', 'Close modal')"
            type="button"
          >
            <X class="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
          </button>
        </div>
        <div class="space-y-3 sm:space-y-4" role="group" aria-labelledby="privacy-settings-title">
          <div class="flex items-center justify-between">
            <div>
              <label for="save-history-checkbox" class="font-medium text-gray-900 dark:text-white">
                {{ safeT('privacy.saveHistory', 'Save Chat History') }}
              </label>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                {{ safeT('privacy.saveHistoryDesc', 'Store conversations for continuity') }}
              </p>
            </div>
            <input
              id="save-history-checkbox"
              v-model="privacySettings.saveHistory"
              type="checkbox"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-offset-2"
              :aria-describedby="safeT('privacy.saveHistoryDesc', 'Store conversations for continuity')"
            />
          </div>
          <div class="flex items-center justify-between">
            <div>
              <label for="emotion-analysis-checkbox" class="font-medium text-gray-900 dark:text-white">
                {{ safeT('privacy.emotionAnalysis', 'Emotion Analysis') }}
              </label>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                {{ safeT('privacy.emotionAnalysisDesc', 'Analyze emotions for better support') }}
              </p>
            </div>
            <input
              id="emotion-analysis-checkbox"
              v-model="privacySettings.emotionAnalysis"
              type="checkbox"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-offset-2"
              :aria-describedby="safeT('privacy.emotionAnalysisDesc', 'Analyze emotions for better support')"
            />
          </div>
          <div class="flex items-center justify-between">
            <div>
              <label for="crisis-detection-checkbox" class="font-medium text-gray-900 dark:text-white">
                {{ safeT('privacy.crisisDetection', 'Crisis Detection') }}
              </label>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                {{ safeT('privacy.crisisDetectionDesc', 'Alert for crisis situations') }}
              </p>
            </div>
            <input
              id="crisis-detection-checkbox"
              v-model="privacySettings.crisisDetection"
              type="checkbox"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-offset-2"
              :aria-describedby="safeT('privacy.crisisDetectionDesc', 'Alert for crisis situations')"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed, watch } from "vue";
import {
  Bot,
  Heart,
  MoreVertical,
  Mic,
  MicOff,
  Smile,
  Send,
  X,
  AlertTriangle,
  Volume2,
  Zap,
  Eye,
  Globe,
  Pause,
  ArrowLeft,
  Check,
  ChevronDown,
  Settings,
  Menu,
  Download,
  Copy,
  Trash2,
  Phone,
  MessageCircle,
  HelpCircle,
  MessageSquare,
  Lightbulb,
  User,
} from "lucide-vue-next";

// Import VueUse Motion
import { useMotion } from '@vueuse/motion';

// I18n composable with safe initialization for SSR
const { t, locale, locales, setLocale } = useI18n();

// Safe translation function
const safeT = (key, fallback = '', options = {}) => {
  if (process.server || typeof t !== 'function') {
    return fallback;
  }
  try {
    const result = t(key, options);
    if (result === key && fallback) {
      return fallback;
    }
    return result;
  } catch (error) {
    console.warn(`Translation error for key "${key}":`, error);
    return fallback;
  }
};

// Ensure component is mounted on client side
const isClient = ref(false);
onMounted(() => {
  isClient.value = true;
});

// Set layout and disable SSR for this page
definePageMeta({
  layout: "app",
  ssr: false
});

// Enhanced Ollama Chat integration
const {
  sendMessage,
  sendMessageStream,
  isProcessing: ollamaIsProcessing,
  isStreaming: ollamaIsStreaming,
  error: ollamaError,
  isConnected,
  sessionId,
  messages: ollamaMessages,
  addMessage: addOllamaMessage,
  clearMessages: clearOllamaMessages,
  hasMessages,
  lastMessage,
  isAssessmentActive,
  assessmentProgressPercentage,
  searchMentalHealthContext,
  getProblemCategories,
  getAssessmentQuestions,
  getTherapeuticSuggestions,
  startAssessment,
  continueAssessment,
  acceptAssessmentSuggestion,
  declineAssessmentSuggestion,
  detectedProblemCategory,
  shouldShowAssessmentSuggestion,
} = useOllamaChat();

// Refs
const messagesContainer = ref(null);
const menuContainer = ref(null);
const currentMessage = ref("");
const isSending = ref(false);
const showMenu = ref(false);
const showCrisisAlert = ref(false);
const showPrivacySettings = ref(false);
const showEmergencyInfo = ref(false);
const detectedEmotion = ref(null);
const windowWidth = ref(
  typeof window !== "undefined" ? window.innerWidth : 1024
);

// Enhanced UI State Variables
const showSupportivePrompts = ref(true);
const showEmotionWheel = ref(false);
const selectedEmotion = ref(null);
const emotionIntensity = ref(5);
const showQuickResponses = ref(false);
const showRealTimeFeedback = ref(true);
const showEmpathyValidation = ref(false);
const isTypingPositive = ref(false);
const isTypingNegative = ref(false);
const potentialCrisisDetected = ref(false);
const conversationMode = ref('guided');
const assessmentPaused = ref(false);
const canNavigateBack = ref(false);
const showProgressIndicator = ref(true);

// Assessment State Variables
const showAssessment = ref(false);
const assessmentAnswers = ref({});
const selectedMood = ref(null);
const assessmentCompleted = ref(false);

// Computed Properties
const isMobile = computed(() => windowWidth.value < 768);
const isExtraSmall = computed(() => windowWidth.value < 480);

const privacySettings = ref({
  saveHistory: true,
  emotionAnalysis: true,
  crisisDetection: true,
});

// Emotion options
const emotionOptions = computed(() => [
  { id: 'happy', emoji: '😊', label: safeT('emotions.happy', 'Happy'), color: 'text-yellow-500' },
  { id: 'sad', emoji: '😢', label: safeT('emotions.sad', 'Sad'), color: 'text-blue-500' },
  { id: 'angry', emoji: '😠', label: safeT('emotions.angry', 'Angry'), color: 'text-red-500' },
  { id: 'anxious', emoji: '😰', label: safeT('emotions.anxious', 'Anxious'), color: 'text-purple-500' },
  { id: 'calm', emoji: '😌', label: safeT('emotions.calm', 'Calm'), color: 'text-green-500' },
  { id: 'confused', emoji: '😕', label: safeT('emotions.confused', 'Confused'), color: 'text-gray-500' },
  { id: 'excited', emoji: '🤗', label: safeT('emotions.excited', 'Excited'), color: 'text-orange-500' },
  { id: 'tired', emoji: '😴', label: safeT('emotions.tired', 'Tired'), color: 'text-indigo-500' }
]);

// Quick response options
const quickResponseOptions = computed(() => {
  const defaultResponses = [
    { id: 'default1', text: safeT('responses.default1', 'I need someone to talk to') },
    { id: 'default2', text: safeT('responses.default2', 'Can you help me?') },
    { id: 'default3', text: safeT('responses.default3', 'I\'m not sure what to say') },
    { id: 'assessment', text: safeT('responses.assessment', 'I\'d like to do a quick assessment') }
  ];

  if (selectedEmotion.value) {
    const emotionResponses = {
      happy: [
        { id: 'happy1', text: safeT('responses.happy1', 'I\'m feeling really good today!') },
        { id: 'happy2', text: safeT('responses.happy2', 'Something wonderful happened.') },
        { id: 'happy3', text: safeT('responses.happy3', 'I want to share my joy.') }
      ],
      sad: [
        { id: 'sad1', text: safeT('responses.sad1', 'I\'ve been feeling down lately.') },
        { id: 'sad2', text: safeT('responses.sad2', 'Everything seems overwhelming.') },
        { id: 'sad3', text: safeT('responses.sad3', 'I need someone to talk to.') }
      ],
      anxious: [
        { id: 'anxious1', text: safeT('responses.anxious1', 'I can\'t stop worrying about things.') },
        { id: 'anxious2', text: safeT('responses.anxious2', 'My mind is racing with thoughts.') },
        { id: 'anxious3', text: safeT('responses.anxious3', 'I feel like something bad will happen.') }
      ]
    };
    return emotionResponses[selectedEmotion.value] || defaultResponses;
  }
  return defaultResponses;
});

// Assessment questions
const assessmentQuestions = computed(() => [
  {
    id: 'stress_level',
    text: safeT('assessment.questions.stress', 'I have been feeling stressed or overwhelmed lately')
  },
  {
    id: 'sleep_quality',
    text: safeT('assessment.questions.sleep', 'I have been sleeping well and feeling rested')
  },
  {
    id: 'social_connection',
    text: safeT('assessment.questions.social', 'I feel connected to friends and family')
  },
  {
    id: 'mood_stability',
    text: safeT('assessment.questions.mood', 'My mood has been stable and positive')
  }
]);

// Mood options for visual selector
const moodOptions = computed(() => [
  { id: 1, emoji: '😢', label: safeT('mood.very_sad', 'Very Sad'), value: 'very_sad' },
  { id: 2, emoji: '😕', label: safeT('mood.sad', 'Sad'), value: 'sad' },
  { id: 3, emoji: '😐', label: safeT('mood.neutral', 'Neutral'), value: 'neutral' },
  { id: 4, emoji: '🙂', label: safeT('mood.happy', 'Happy'), value: 'happy' },
  { id: 5, emoji: '😊', label: safeT('mood.very_happy', 'Very Happy'), value: 'very_happy' }
]);

// Assessment completion check
const canSubmitAssessment = computed(() => {
  const requiredQuestions = assessmentQuestions.value.length;
  const answeredQuestions = Object.keys(assessmentAnswers.value).length;
  return answeredQuestions === requiredQuestions && selectedMood.value !== null;
});

// Assessment progress
const assessmentProgress = computed(() => {
  if (!isAssessmentActive.value) return null;
  return {
    isActive: isAssessmentActive.value,
    percentage: assessmentProgressPercentage.value,
    currentQuestion: Math.floor(assessmentProgressPercentage.value / 10) + 1,
    totalQuestions: 10
  };
});

// Crisis keywords for detection
const crisisKeywords = [
  "bunuh diri",
  "mengakhiri hidup",
  "tidak ingin hidup",
  "menyakiti diri",
  "suicide",
  "self harm",
  "hurt myself",
  "end my life",
  "kill myself",
];

// Methods
const getEmotionEmoji = (emotion) => {
  const emotionMap = {
    sad: "😢",
    anxious: "😰",
    angry: "😠",
    happy: "😊",
    neutral: "😐",
    stressed: "😵",
    hopeful: "🙂",
  };
  return emotionMap[emotion] || "😐";
};

const detectEmotion = () => {
  if (!privacySettings.value.emotionAnalysis) return;
  const message = currentMessage.value.toLowerCase();
  
  if (message.includes("sedih") || message.includes("sad") || message.includes("down")) {
    detectedEmotion.value = "sad";
  } else if (message.includes("cemas") || message.includes("anxious") || message.includes("worry")) {
    detectedEmotion.value = "anxious";
  } else if (message.includes("marah") || message.includes("angry") || message.includes("frustasi")) {
    detectedEmotion.value = "angry";
  } else if (message.includes("bahagia") || message.includes("happy") || message.includes("senang")) {
    detectedEmotion.value = "happy";
  } else if (message.includes("stress") || message.includes("overwhelmed") || message.includes("capek")) {
    detectedEmotion.value = "stressed";
  } else {
    detectedEmotion.value = "neutral";
  }
};

const checkForCrisis = (message) => {
  if (!privacySettings.value.crisisDetection) return false;
  const lowerMessage = message.toLowerCase();
  return crisisKeywords.some((keyword) => lowerMessage.includes(keyword));
};

const handleSendMessage = async () => {
  if (!currentMessage.value.trim() || isSending.value) return;

  const userMessage = {
    id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    text: currentMessage.value.trim(),
    sender: "user",
    timestamp: new Date(),
    emotionTone: detectedEmotion.value,
  };

  if (checkForCrisis(userMessage.text)) {
    showCrisisAlert.value = true;
  }

  addOllamaMessage(userMessage);
  const messageText = currentMessage.value;
  const messageEmotion = detectedEmotion.value;
  currentMessage.value = "";
  detectedEmotion.value = null;

  await scrollToBottom();
  isSending.value = true;

  try {
    const aiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const aiMessage = {
      id: aiMessageId,
      text: "",
      sender: "ai",
      timestamp: new Date(),
      detectedEmotion: messageEmotion,
      isStreaming: true,
    };
    addOllamaMessage(aiMessage);
    await scrollToBottom();

    await sendMessageStream(
      messageText,
      {
        emotion: messageEmotion,
        mode: 'help',
        sessionId: sessionId.value,
        preferredLanguage: locale.value,
      },
      (chunk) => {
        const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
        if (messageIndex !== -1) {
          ollamaMessages.value[messageIndex].text += chunk;
          scrollToBottom();
        }
      },
      (finalResponse) => {
        const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
        if (messageIndex !== -1) {
          ollamaMessages.value[messageIndex].isStreaming = false;
          if (finalResponse?.message && ollamaMessages.value[messageIndex].text.length === 0) {
            ollamaMessages.value[messageIndex].text = finalResponse.message;
          }
        }
      }
    );
  } catch (error) {
    console.error('Error sending message:', error);
  } finally {
    isSending.value = false;
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const switchLanguage = () => {
  const newLocale = locale.value === 'id' ? 'en' : 'id';
  setLocale(newLocale);
};

const toggleEmotionWheel = () => {
  showEmotionWheel.value = !showEmotionWheel.value;
  if (showEmotionWheel.value) {
    showQuickResponses.value = false;
  }
};

const toggleQuickResponses = () => {
  showQuickResponses.value = !showQuickResponses.value;
  if (showQuickResponses.value) {
    showEmotionWheel.value = false;
  }
};

const selectEmotion = (emotion) => {
  selectedEmotion.value = emotion.id;
  detectedEmotion.value = emotion.id;
  showEmotionWheel.value = false;
  showQuickResponses.value = true;
};

const selectQuickResponse = (option) => {
  if (option.id === 'assessment') {
    showAssessment.value = true;
    showQuickResponses.value = false;
    return;
  }
  currentMessage.value = option.text;
  showQuickResponses.value = false;
  handleSendMessage();
};

const setAssessmentAnswer = (questionId, value) => {
  assessmentAnswers.value[questionId] = value;
};

const setMoodSelection = (moodId) => {
  selectedMood.value = moodId;
};

const submitAssessment = async () => {
  if (!canSubmitAssessment.value) return;
  
  const assessmentData = {
    answers: assessmentAnswers.value,
    mood: selectedMood.value,
    emotion: selectedEmotion.value,
    emotionIntensity: emotionIntensity.value,
    timestamp: new Date().toISOString()
  };
  
  // Create assessment summary message
  const summaryText = generateAssessmentSummary(assessmentData);
  
  const assessmentMessage = {
    id: `assessment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    text: summaryText,
    sender: "user",
    timestamp: new Date(),
    type: "assessment",
    data: assessmentData
  };
  
  addOllamaMessage(assessmentMessage);
  
  // Reset assessment state
  showAssessment.value = false;
  assessmentAnswers.value = {};
  selectedMood.value = null;
  assessmentCompleted.value = true;
  
  await scrollToBottom();
  
  // Send assessment to AI for analysis
  try {
    const aiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const aiMessage = {
      id: aiMessageId,
      text: "",
      sender: "ai",
      timestamp: new Date(),
      isStreaming: true,
    };
    addOllamaMessage(aiMessage);
    await scrollToBottom();

    await sendMessageStream(
      `Assessment completed: ${summaryText}`,
      {
        type: 'assessment',
        data: assessmentData,
        sessionId: sessionId.value,
        preferredLanguage: locale.value,
      },
      (chunk) => {
        const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
        if (messageIndex !== -1) {
          ollamaMessages.value[messageIndex].text += chunk;
          scrollToBottom();
        }
      },
      (finalResponse) => {
        const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
        if (messageIndex !== -1) {
          ollamaMessages.value[messageIndex].isStreaming = false;
          if (finalResponse?.message && ollamaMessages.value[messageIndex].text.length === 0) {
            ollamaMessages.value[messageIndex].text = finalResponse.message;
          }
        }
      }
    );
  } catch (error) {
    console.error('Error sending assessment:', error);
  }
};

const generateAssessmentSummary = (data) => {
  const moodLabel = moodOptions.value.find(m => m.id === data.mood)?.label || 'Unknown';
  const avgScore = Object.values(data.answers).reduce((sum, val) => sum + val, 0) / Object.values(data.answers).length;
  
  return safeT('assessment.summary', 
    `Assessment completed: Overall mood is ${moodLabel}, average wellbeing score: ${avgScore.toFixed(1)}/5. ${data.emotion ? `Current emotion: ${data.emotion} (intensity: ${data.emotionIntensity}/10)` : ''}`
  );
};

const clearChat = () => {
  if (confirm(safeT('confirm.clearChat', 'Are you sure you want to clear the chat history?'))) {
    clearOllamaMessages();
    showMenu.value = false;
  }
};

const exportConversation = () => {
  const conversation = ollamaMessages.value.map(msg => ({
    sender: msg.sender,
    text: msg.text,
    timestamp: msg.timestamp,
    emotion: msg.emotionTone
  }));
  
  const blob = new Blob([JSON.stringify(conversation, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mental-health-conversation-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showMenu.value = false;
};

const likeMessage = (messageId) => {
  const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === messageId);
  if (messageIndex !== -1) {
    ollamaMessages.value[messageIndex].liked = !ollamaMessages.value[messageIndex].liked;
  }
};

const copyMessage = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    // You could add a toast notification here
  } catch (error) {
    console.error('Failed to copy message:', error);
  }
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Component imports for animations
const TypewriterText = {
  props: {
    text: String,
    speed: { type: Number, default: 50 }
  },
  setup(props) {
    const displayText = ref('');
    const currentIndex = ref(0);
    
    watch(() => props.text, (newText) => {
      displayText.value = '';
      currentIndex.value = 0;
      
      const interval = setInterval(() => {
        if (currentIndex.value < newText.length) {
          displayText.value += newText[currentIndex.value];
          currentIndex.value++;
        } else {
          clearInterval(interval);
        }
      }, props.speed);
    }, { immediate: true });
    
    return { displayText };
  },
  template: '<span>{{ displayText }}</span>'
};

const TypingIndicator = {
  template: `
    <div class="flex items-center space-x-1">
      <div class="flex space-x-1">
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
      </div>
      <span class="text-sm text-gray-500 ml-2">{{ safeT('status.typing', 'AI is typing...') }}</span>
    </div>
  `,
  setup() {
    return { safeT };
  }
};

// Lifecycle
onMounted(() => {
  if (typeof window !== "undefined") {
    const handleResize = () => {
      windowWidth.value = window.innerWidth;
    };
    window.addEventListener("resize", handleResize);
    
    // Close menu when clicking outside
    document.addEventListener("click", (e) => {
      if (showMenu.value && menuContainer.value && !menuContainer.value.contains(e.target)) {
        showMenu.value = false;
      }
    });
    
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }
});
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 4px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.scroll-container {
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f8fafc;
}

/* Animation classes */
.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0,0,0);
  }
  40%, 43% {
    transform: translate3d(0,-30px,0);
  }
  70% {
    transform: translate3d(0,-15px,0);
  }
  90% {
    transform: translate3d(0,-4px,0);
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  textarea, input, select {
    font-size: 16px !important;
  }
}

/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {
  .overflow-y-auto {
    -webkit-overflow-scrolling: touch;
  }
}
</style>