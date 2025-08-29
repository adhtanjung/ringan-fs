<template>
  <div class="fixed top-16 left-0 right-0 z-40">
    <div 
      class="h-1 bg-gradient-purple transition-all duration-300 ease-out"
      :style="{ width: scrollProgress + '%' }"
    ></div>
  </div>
</template>

<script setup>
const scrollProgress = ref(0)

const updateScrollProgress = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight
  const progress = (scrollTop / scrollHeight) * 100
  scrollProgress.value = Math.min(100, Math.max(0, progress))
}

onMounted(() => {
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
  updateScrollProgress()
  
  onUnmounted(() => {
    window.removeEventListener('scroll', updateScrollProgress)
  })
})
</script> 