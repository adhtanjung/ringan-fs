<template>
  <div class="chat-layout h-screen max-h-screen bg-gradient-to-br from-blue-50/30 via-white to-indigo-50/20 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <!-- Animated Background -->
    <ClientOnly>
      <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <div class="absolute -inset-10 opacity-30">
          <div class="absolute top-1/4 left-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-blue-200/20 rounded-full blur-3xl"></div>
          <div class="absolute bottom-1/4 right-1/4 w-48 h-48 sm:w-80 sm:h-80 bg-indigo-200/20 rounded-full blur-3xl"></div>
          <div class="absolute top-3/4 left-1/2 w-32 h-32 sm:w-64 sm:h-64 bg-purple-200/20 rounded-full blur-3xl"></div>
        </div>
      </div>
    </ClientOnly>

    <!-- Main Content -->
    <div class="relative z-10 flex flex-col h-full">
      <!-- Header -->
      <header class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 flex-shrink-0">
        <div class="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div class="flex items-center justify-between">
            <!-- AI Assistant Info -->
            <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
              <div class="relative flex-shrink-0">
                <div class="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                  <Bot class="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div class="absolute -bottom-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
              </div>
              <div class="min-w-0 flex-1">
                <h1 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white truncate">
                  {{ $t('chat.title', 'Mental Health Assistant') }}
                </h1>
                <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-300 flex items-center">
                  <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-green-500 rounded-full mr-1.5 sm:mr-2 animate-pulse flex-shrink-0"></div>
                  <span class="truncate">{{ $t('chat.subtitle', 'Online & Ready to Help') }}</span>
                </div>
              </div>
            </div>

            <!-- Header Actions -->
            <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
              <!-- Language Switcher -->
              <Button
                variant="ghost"
                size="sm"
                @click="switchLanguage"
                :title="$t('language.switch', 'Switch Language')"
                :aria-label="$t('language.switch', 'Switch Language')"
                class="h-8 w-8 sm:h-9 sm:w-9 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative group"
              >
                <Globe class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                <!-- Language indicator -->
                <div class="absolute -bottom-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center">
                  <span class="text-xs font-bold text-white">{{ locale === 'en' ? 'EN' : 'ID' }}</span>
                </div>
                <!-- Tooltip -->
                <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                  {{ $t('language.switch', 'Switch Language') }} ({{ locale === 'en' ? 'EN' : 'ID' }})
                </div>
              </Button>

              <!-- Settings -->
              <Button
                variant="ghost"
                size="sm"
                @click="showSettings = !showSettings"
                class="h-8 w-8 sm:h-9 sm:w-9 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <Settings class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Chat Area -->
      <main class="flex-1 flex flex-col max-w-4xl mx-auto w-full px-3 sm:px-4 py-3 sm:py-6 min-h-0">
        <slot />
      </main>
    </div>

    <!-- Settings Panel -->
    <ClientOnly>
      <div
        v-if="showSettings"
        class="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-4"
        @click="showSettings = false"
      >
        <div
          class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto p-4 sm:p-6"
          @click.stop
        >
          <div class="flex items-center justify-between mb-4 sm:mb-6">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
              {{ $t('settings.title', 'Settings') }}
            </h3>
            <Button
              variant="ghost"
              size="sm"
              @click="showSettings = false"
              class="h-7 w-7 sm:h-8 sm:w-8 p-0 rounded-full"
            >
              <X class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </Button>
          </div>

          <div class="space-y-3 sm:space-y-4">
            <!-- Language Setting -->
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div class="flex-1">
                <p class="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  {{ $t('settings.language', 'Language') }}
                </p>
                <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
                  {{ $t('settings.languageDesc', 'Choose your preferred language') }}
                </p>
              </div>
              <Select v-model="selectedLanguage">
                <SelectTrigger class="w-full sm:w-32 mt-2 sm:mt-0">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="id">Bahasa Indonesia</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- Privacy Settings -->
            <div class="space-y-2 sm:space-y-3">
              <h4 class="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                {{ $t('settings.privacy', 'Privacy') }}
              </h4>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs sm:text-sm text-gray-700 dark:text-gray-300 flex-1 mr-3">
                    {{ $t('settings.saveHistory', 'Save conversation history') }}
                  </span>
                  <Switch v-model="saveHistory" />
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-xs sm:text-sm text-gray-700 dark:text-gray-300 flex-1 mr-3">
                    {{ $t('settings.analytics', 'Anonymous usage analytics') }}
                  </span>
                  <Switch v-model="analytics" />
                </div>
              </div>
            </div>

            <!-- Emergency Resources -->
            <div class="pt-3 sm:pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 class="font-medium text-gray-900 dark:text-white mb-2 sm:mb-3 text-sm sm:text-base">
                {{ $t('settings.emergency', 'Emergency Resources') }}
              </h4>
              <div class="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  class="w-full justify-start text-xs sm:text-sm"
                  @click="openEmergencyInfo"
                >
                  <Phone class="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-2" />
                  {{ $t('settings.crisisHotline', 'Crisis Hotline') }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Bot, Globe, Settings, X, Phone } from 'lucide-vue-next'

// Keep SSR enabled but handle client-side content properly

// I18n
const { locale, setLocale } = useI18n()

// State
const showSettings = ref(false)
const saveHistory = ref(true)
const analytics = ref(true)

// Computed
const selectedLanguage = computed({
  get: () => locale.value,
  set: (value: 'en' | 'id') => setLocale(value)
})

// Methods
const switchLanguage = async () => {
  const newLocale = locale.value === 'en' ? 'id' : 'en'

  // Add visual feedback
  const button = document.querySelector('[aria-label*="Switch Language"]') as HTMLElement
  if (button) {
    button.style.transform = 'scale(0.95)'
    setTimeout(() => {
      button.style.transform = 'scale(1)'
    }, 150)
  }

  // Set the new locale
  await setLocale(newLocale)

  // Force a small delay to ensure all reactive content updates
  await nextTick()

  // Optional: Show a brief success message
  console.log(`Language switched to: ${newLocale}`)
}

const openEmergencyInfo = () => {
  // Open emergency resources modal
  showSettings.value = false
}
</script>

<style scoped>
.chat-layout {
  /* Ensure smooth animations */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* Handle mobile viewport units */
  height: 100vh;
  height: 100dvh; /* Dynamic viewport height for mobile */
  max-height: 100vh;
  max-height: 100dvh;
}

/* Mobile-specific adjustments */
@supports (height: 100dvh) {
  .chat-layout {
    height: 100dvh;
    max-height: 100dvh;
  }
}

/* Handle iOS Safari viewport issues */
@supports (-webkit-touch-callout: none) {
  .chat-layout {
    height: -webkit-fill-available;
  }
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .chat-layout * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Mobile keyboard handling */
@media (max-width: 768px) {
  .chat-layout {
    /* Ensure content doesn't get cut off when keyboard appears */
    min-height: 100vh;
    min-height: 100dvh;
  }
}
</style>