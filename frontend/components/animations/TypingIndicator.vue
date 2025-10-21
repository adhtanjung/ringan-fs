<template>
  <div class="typing-indicator flex items-center space-x-2">
    <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">
      {{ $t('chat.typing', 'AI is thinking') }}
    </span>
    <div class="flex space-x-1">
      <div
        v-for="i in 3"
        :key="i"
        class="typing-dot w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full"
        :style="{ animationDelay: `${(i - 1) * 0.2}s` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const isVisible = ref(false)

// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

onMounted(() => {
  isVisible.value = true
})

onUnmounted(() => {
  isVisible.value = false
})
</script>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
}

.typing-dot {
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0s;
}

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Alternative breathing animation for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .typing-dot {
    animation: typing-breathe 2s infinite ease-in-out;
  }

  @keyframes typing-breathe {
    0%, 100% {
      opacity: 0.4;
    }
    50% {
      opacity: 1;
    }
  }
}

/* Enhanced breathing animation for a more calming effect */
.typing-dot {
  transition: all 0.3s ease;
}

.typing-dot:hover {
  transform: scale(1.2);
  background-color: #3b82f6;
}
</style>





