<template>
  <span
    ref="textElement"
    class="typewriter-text"
    :class="{ 'cursor-blink': showCursor && isTyping }"
  >
    {{ displayText }}<span v-if="showCursor && isTyping" class="cursor">|</span>
  </span>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'

interface Props {
  text: string
  speed?: number
  delay?: number
  showCursor?: boolean
  pauseOnPunctuation?: boolean
  onComplete?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  speed: 30,
  delay: 0,
  showCursor: true,
  pauseOnPunctuation: true,
  onComplete: () => {}
})

const displayText = ref('')
const textElement = ref<HTMLElement>()
const isTyping = ref(false)
let typeInterval: NodeJS.Timeout | null = null

// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const typeText = async () => {
  if (prefersReducedMotion) {
    // Show text immediately for users who prefer reduced motion
    displayText.value = props.text
    isTyping.value = false
    props.onComplete()
    return
  }

  displayText.value = ''
  isTyping.value = true

  if (props.delay > 0) {
    await new Promise(resolve => setTimeout(resolve, props.delay))
  }

  for (let i = 0; i <= props.text.length; i++) {
    displayText.value = props.text.slice(0, i)

    // Pause longer on punctuation for more natural feel
    let pauseDuration = props.speed
    if (props.pauseOnPunctuation && i < props.text.length) {
      const char = props.text[i]
      if (char === '.' || char === '!' || char === '?') {
        pauseDuration = props.speed * 3
      } else if (char === ',' || char === ';' || char === ':') {
        pauseDuration = props.speed * 2
      }
    }

    await new Promise(resolve => {
      typeInterval = setTimeout(resolve, pauseDuration)
    })
  }

  isTyping.value = false
  props.onComplete()
}

const stopTyping = () => {
  if (typeInterval) {
    clearTimeout(typeInterval)
    typeInterval = null
  }
}

watch(() => props.text, () => {
  stopTyping()
  typeText()
}, { immediate: true })

onMounted(() => {
  typeText()
})

onUnmounted(() => {
  stopTyping()
})
</script>

<style scoped>
.typewriter-text {
  display: inline;
}

.cursor {
  display: inline-block;
  margin-left: 2px;
  color: #3b82f6;
  font-weight: 100;
}

.cursor-blink .cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .cursor-blink .cursor {
    animation: none;
    opacity: 1;
  }
}
</style>





