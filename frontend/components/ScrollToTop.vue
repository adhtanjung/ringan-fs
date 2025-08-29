<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 scale-90 translate-y-4"
    enter-to-class="opacity-100 scale-100 translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 scale-100 translate-y-0"
    leave-to-class="opacity-0 scale-90 translate-y-4"
  >
    <button
      v-show="showButton"
      @click="scrollToTop"
      class="fixed bottom-6 left-6 z-40 w-12 h-12 bg-white border-2 border-gray-200 text-gray-600 rounded-full shadow-lg hover:shadow-xl hover:border-purple-300 hover:text-purple-600 transition-all duration-300 flex items-center justify-center group"
    >
      <ArrowUp class="w-5 h-5 transition-transform group-hover:-translate-y-0.5" />
    </button>
  </Transition>
</template>

<script setup>
import { ArrowUp } from 'lucide-vue-next'

const showButton = ref(false)

const checkScrollPosition = () => {
  showButton.value = window.pageYOffset > 300
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

onMounted(() => {
  window.addEventListener('scroll', checkScrollPosition, { passive: true })
  checkScrollPosition()
  
  onUnmounted(() => {
    window.removeEventListener('scroll', checkScrollPosition)
  })
})
</script> 