<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-40">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between">
          <!-- Logo/Brand -->
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">💜</span>
            </div>
            <span class="font-bold text-gray-900 text-lg">Ringan</span>
          </div>
          
          <!-- Profile & Notifications -->
          <div class="flex items-center space-x-3">
            <!-- Emergency Button -->
            <button class="p-2 rounded-lg hover:bg-red-50 text-red-600">
              <Phone class="w-5 h-5" />
            </button>
            
            <!-- Notifications -->
            <button class="p-2 rounded-lg hover:bg-gray-100 relative">
              <Bell class="w-5 h-5 text-gray-600" />
              <span class="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full"></span>
            </button>
            
            <!-- Profile -->
            <NuxtLink to="/application/profile" class="p-1 rounded-lg hover:bg-gray-100">
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <User class="w-4 h-4 text-purple-600" />
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-16 pb-20 min-h-screen">
      <div class="px-4 py-4">
        <slot />
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40">
      <div class="grid grid-cols-5 h-16">
        <NuxtLink
          to="/application/home"
          class="flex flex-col items-center justify-center space-y-1 transition-colors"
          :class="isActive('/application/home') ? 'text-purple-600' : 'text-gray-500 hover:text-gray-700'"
        >
          <Home class="w-5 h-5" />
          <span class="text-xs font-medium">Home</span>
        </NuxtLink>

        <NuxtLink
          to="/application/assessment"
          class="flex flex-col items-center justify-center space-y-1 transition-colors"
          :class="isActive('/application/assessment') ? 'text-purple-600' : 'text-gray-500 hover:text-gray-700'"
        >
          <ClipboardCheck class="w-5 h-5" />
          <span class="text-xs font-medium">Assess</span>
        </NuxtLink>

        <NuxtLink
          to="/application/chatbot"
          class="flex flex-col items-center justify-center space-y-1 transition-colors"
          :class="isActive('/application/chatbot') ? 'text-purple-600' : 'text-gray-500 hover:text-gray-700'"
        >
          <MessageCircle class="w-5 h-5" />
          <span class="text-xs font-medium">Chat</span>
        </NuxtLink>

        <NuxtLink
          to="/application/learn"
          class="flex flex-col items-center justify-center space-y-1 transition-colors"
          :class="isActive('/application/learn') ? 'text-purple-600' : 'text-gray-500 hover:text-gray-700'"
        >
          <BookOpen class="w-5 h-5" />
          <span class="text-xs font-medium">Learn</span>
        </NuxtLink>

        <NuxtLink
          to="/application/community"
          class="flex flex-col items-center justify-center space-y-1 transition-colors"
          :class="isActive('/application/community') ? 'text-purple-600' : 'text-gray-500 hover:text-gray-700'"
        >
          <Users class="w-5 h-5" />
          <span class="text-xs font-medium">Community</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { Bell, User, Home, ClipboardCheck, MessageCircle, BookOpen, Users, Phone } from 'lucide-vue-next'

const route = useRoute()

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
/* Responsive adjustments */
@media (min-width: 768px) {
  .grid-cols-5 {
    max-width: 400px;
    margin: 0 auto;
  }
}

@media (min-width: 1024px) {
  /* For larger screens, consider a sidebar layout */
  .min-h-screen {
    display: flex;
  }
}
</style> 