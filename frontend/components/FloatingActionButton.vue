<template>
  <div class="fixed bottom-6 right-6 z-40">
    <!-- Main FAB Button -->
    <button
      @click="toggleMenu"
      class="w-14 h-14 bg-gradient-purple text-white rounded-full shadow-glow hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
      :class="{ 'rotate-45': isOpen }"
    >
      <Plus class="w-6 h-6 transition-transform duration-300" />
    </button>
    
    <!-- Sub Menu Items -->
    <div 
      v-show="isOpen"
      class="absolute bottom-16 right-0 space-y-3 transition-all duration-300"
    >
      <!-- Quick Assessment -->
      <div class="flex items-center space-x-3">
        <span class="bg-gray-900 text-white text-xs px-3 py-1 rounded-lg whitespace-nowrap">
          Cek Kesehatan Mental
        </span>
        <button
          @click="startAssessment"
          class="w-12 h-12 bg-blue-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center animate-fade-in"
          style="animation-delay: 0.1s"
        >
          <Brain class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Chat with AI -->
      <div class="flex items-center space-x-3">
        <span class="bg-gray-900 text-white text-xs px-3 py-1 rounded-lg whitespace-nowrap">
          Chat dengan AI
        </span>
        <button
          @click="startChat"
          class="w-12 h-12 bg-green-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center animate-fade-in"
          style="animation-delay: 0.2s"
        >
          <MessageCircleHeart class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Emergency Help -->
      <div class="flex items-center space-x-3">
        <span class="bg-gray-900 text-white text-xs px-3 py-1 rounded-lg whitespace-nowrap">
          Bantuan Darurat
        </span>
        <button
          @click="emergencyHelp"
          class="w-12 h-12 bg-red-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center animate-fade-in"
          style="animation-delay: 0.3s"
        >
          <Phone class="w-5 h-5" />
        </button>
      </div>
    </div>
    
    <!-- Background overlay when menu is open -->
    <div 
      v-show="isOpen"
      @click="closeMenu"
      class="fixed inset-0 bg-black/20 backdrop-blur-sm -z-10"
    ></div>
  </div>
</template>

<script setup>
import { Plus, Brain, MessageCircleHeart, Phone } from 'lucide-vue-next'

const isOpen = ref(false)

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

const startAssessment = () => {
  // Placeholder for assessment functionality
  alert('Mulai Self-Assessment - Coming Soon!')
  closeMenu()
}

const startChat = () => {
  // Placeholder for chat functionality
  alert('Chat dengan Ringan AI - Coming Soon!')
  closeMenu()
}

const emergencyHelp = () => {
  // Emergency contacts
  const emergencyMessage = `Jika kamu dalam keadaan darurat, segera hubungi:

🚨 Hotline Bunuh Diri: 119 ext 8
🏥 IGD Terdekat: 112
💬 Crisis Text Line: kirim "RINGAN" ke 081234567890

Kamu tidak sendirian. Bantuan tersedia 24/7.`
  
  alert(emergencyMessage)
  closeMenu()
}

// Close menu when clicking outside
onMounted(() => {
  const handleClickOutside = (event) => {
    if (!event.target.closest('.fixed.bottom-6.right-6')) {
      closeMenu()
    }
  }
  
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})
</script>

<style scoped>
/* Smooth animations for FAB menu */
.animate-fade-in {
  animation: fadeInUp 0.3s ease-out forwards;
  opacity: 0;
  transform: translateY(10px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 