<template>
  <div
    v-if="replies.length > 0"
    class="quick-replies-container"
    v-motion
    :initial="{ opacity: 0, y: 20 }"
    :enter="{
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
        delay: 200
      }
    }"
  >
    <div class="flex flex-wrap gap-2 justify-center">
      <button
        v-for="(reply, index) in replies"
        :key="reply.id"
        @click="selectReply(reply)"
        :disabled="isSelecting"
        class="quick-reply-button group relative overflow-hidden"
        v-motion
        :initial="{
          opacity: 0,
          scale: 0.8,
          y: 20,
          rotateX: -15
        }"
        :enter="{
          opacity: 1,
          scale: 1,
          y: 0,
          rotateX: 0,
          transition: {
            type: 'spring',
            stiffness: 400,
            damping: 25,
            delay: 300 + (index * 100)
          }
        }"
        :hover="{
          scale: 1.05,
          y: -2,
          transition: { duration: 0.2 }
        }"
        :tap="{
          scale: 0.95,
          transition: { duration: 0.1 }
        }"
      >
        <!-- Background with gradient -->
        <div class="absolute inset-0 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

        <!-- Border animation -->
        <div class="absolute inset-0 rounded-full border-2 border-transparent group-hover:border-blue-200 dark:group-hover:border-gray-500 transition-all duration-300"></div>

        <!-- Content -->
        <div class="relative px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors duration-200">
          {{ reply.text }}
        </div>

        <!-- Selection indicator -->
        <div
          v-if="selectedReplyId === reply.id"
          class="absolute inset-0 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center"
          v-motion
          :initial="{ scale: 0, rotate: -180 }"
          :enter="{
            scale: 1,
            rotate: 0,
            transition: {
              type: 'spring',
              stiffness: 500,
              damping: 20
            }
          }"
        >
          <Check class="w-4 h-4 text-green-600 dark:text-green-400" />
        </div>

        <!-- Ripple effect on click -->
        <div
          v-if="rippleIndex === index"
          class="absolute inset-0 rounded-full bg-blue-200 dark:bg-blue-800 opacity-30"
          v-motion
          :initial="{ scale: 0, opacity: 0.6 }"
          :enter="{
            scale: 2,
            opacity: 0,
            transition: {
              duration: 0.6,
              ease: 'easeOut'
            }
          }"
        ></div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Check } from 'lucide-vue-next'

interface QuickReply {
  id: string
  text: string
  category?: string
  emotion?: string
}

interface Props {
  replies: QuickReply[]
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  select: [reply: QuickReply]
}>()

const isSelecting = ref(false)
const selectedReplyId = ref<string | null>(null)
const rippleIndex = ref<number | null>(null)

// Check for reduced motion preference (SSR-safe)
const prefersReducedMotion = ref(false)

// Initialize reduced motion preference on client side
onMounted(() => {
  if (typeof window !== 'undefined') {
    prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }
})

const selectReply = async (reply: QuickReply) => {
  if (isSelecting.value || props.disabled) return

  isSelecting.value = true
  selectedReplyId.value = reply.id

  // Create ripple effect
  const index = props.replies.findIndex(r => r.id === reply.id)
  rippleIndex.value = index

  // Reset ripple after animation
  setTimeout(() => {
    rippleIndex.value = null
  }, 600)

  // Emit selection after a brief delay for visual feedback
  setTimeout(() => {
    emit('select', reply)
    isSelecting.value = false
    selectedReplyId.value = null
  }, prefersReducedMotion ? 100 : 300)
}
</script>

<style scoped>
.quick-replies-container {
  @apply px-4 py-3;
}

.quick-reply-button {
  @apply relative inline-flex items-center justify-center rounded-full border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
  min-height: 40px;
  backdrop-filter: blur(8px);
}

.quick-reply-button:hover {
  @apply shadow-md;
  transform: translateY(-2px) scale(1.05);
}

.quick-reply-button:active {
  transform: translateY(0) scale(0.95);
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .quick-reply-button {
    transition: none;
  }

  .quick-reply-button:hover {
    transform: none;
  }

  .quick-reply-button:active {
    transform: none;
  }
}

/* Enhanced focus states for accessibility */
.quick-reply-button:focus-visible {
  @apply ring-2 ring-blue-500 ring-offset-2;
}

/* Smooth transitions for all interactive states */
.quick-reply-button * {
  transition: all 0.2s ease;
}
</style>
