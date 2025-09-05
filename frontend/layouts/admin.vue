<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Sidebar -->
    <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0" :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'">
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between h-16 px-6 bg-blue-600">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="ml-3">
            <h1 class="text-lg font-semibold text-white">Admin Panel</h1>
          </div>
        </div>
        <button 
          @click="sidebarOpen = false" 
          class="lg:hidden p-2 text-white hover:text-gray-200 hover:bg-blue-700 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
          aria-label="Close sidebar"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Menu -->
      <nav class="mt-6 px-3">
        <div class="space-y-1">
          <!-- Dashboard -->
          <NuxtLink
            to="/admin"
            class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            :class="$route.path === '/admin' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
          >
            <svg class="mr-3 h-5 w-5 flex-shrink-0" :class="$route.path === '/admin' ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h2a2 2 0 012 2v2H8V5z" />
            </svg>
            <span class="truncate">Dataset Management</span>
          </NuxtLink>

          <!-- Data Import/Export -->
          <NuxtLink
            to="/admin/import-export"
            class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            :class="$route.path === '/admin/import-export' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
          >
            <svg class="mr-3 h-5 w-5 flex-shrink-0" :class="$route.path === '/admin/import-export' ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span class="truncate">Import/Export</span>
          </NuxtLink>

          <!-- Vector Database -->
          <NuxtLink
            to="/admin/vector-db"
            class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            :class="$route.path === '/admin/vector-db' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
          >
            <svg class="mr-3 h-5 w-5 flex-shrink-0" :class="$route.path === '/admin/vector-db' ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <span class="truncate">Vector Database</span>
          </NuxtLink>

          <!-- Analytics -->
          <NuxtLink
            to="/admin/analytics"
            class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            :class="$route.path === '/admin/analytics' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
          >
            <svg class="mr-3 h-5 w-5 flex-shrink-0" :class="$route.path === '/admin/analytics' ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="truncate">Analytics</span>
          </NuxtLink>
        </div>

        <!-- Divider -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <div class="space-y-1">
            <!-- Settings -->
            <NuxtLink
              to="/admin/settings"
              class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              :class="$route.path === '/admin/settings' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
            >
              <svg class="mr-3 h-5 w-5 flex-shrink-0" :class="$route.path === '/admin/settings' ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="truncate">Settings</span>
            </NuxtLink>

            <!-- Back to Main App -->
            <NuxtLink
              to="/"
              class="nav-link group flex items-center px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            >
              <svg class="mr-3 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span class="truncate">Back to App</span>
            </NuxtLink>
          </div>
        </div>
      </nav>
    </div>

    <!-- Main Content Area -->
    <div class="lg:pl-64">
      <!-- Top Navigation Bar -->
      <div class="sticky top-0 z-40">
        <div class="flex items-center justify-between h-16 px-4 bg-white border-b border-gray-200 sm:px-6 lg:px-8">
          <!-- Mobile menu button -->
          <button
            @click="sidebarOpen = true"
            class="lg:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200"
            aria-label="Open sidebar"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Page Title -->
          <div class="flex-1 min-w-0 mx-4">
            <h2 class="text-lg font-semibold text-gray-900 truncate">
              {{ pageTitle }}
            </h2>
          </div>

          <!-- User Menu -->
          <div class="flex items-center space-x-3">
            <!-- Notifications -->
            <button 
              class="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              aria-label="View notifications"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM10.5 3.5a6 6 0 0 1 6 6v2l1.5 3h-15l1.5-3v-2a6 6 0 0 1 6-6z" />
              </svg>
            </button>

            <!-- User Profile Dropdown -->
            <div class="relative" ref="userMenuRef">
              <button
                @click="userMenuOpen = !userMenuOpen"
                class="flex items-center px-3 py-2 text-sm rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                :aria-expanded="userMenuOpen"
                aria-haspopup="true"
              >
                <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                  <span class="text-sm font-medium text-white">A</span>
                </div>
                <span class="ml-3 text-gray-700 text-sm font-medium hidden sm:block">Admin</span>
                <svg class="ml-2 h-4 w-4 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': userMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dropdown Menu -->
              <Transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="userMenuOpen"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-50 border border-gray-200 ring-1 ring-black ring-opacity-5"
                  role="menu"
                  aria-orientation="vertical"
                >
                  <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150" role="menuitem">Profile</a>
                  <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150" role="menuitem">Settings</a>
                  <div class="border-t border-gray-100 my-1"></div>
                  <button @click="logout" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150" role="menuitem">Sign out</button>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </div>

      <!-- Page Content -->
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>

    <!-- Mobile Sidebar Overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 lg:hidden"
      @click="sidebarOpen = false"
    >
      <div class="absolute inset-0 bg-gray-600 opacity-75"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Reactive data
const sidebarOpen = ref(false)
const userMenuOpen = ref(false)
const userMenuRef = ref(null)

// Computed properties
const pageTitle = computed(() => {
  const route = useRoute()
  const titleMap = {
    '/admin': 'Dataset Management',
    '/admin/import-export': 'Import/Export Data',
    '/admin/vector-db': 'Vector Database Management',
    '/admin/analytics': 'Analytics & Reports',
    '/admin/settings': 'Settings'
  }
  return titleMap[route.path] || 'Admin Panel'
})

// Methods
const logout = () => {
  // Implement logout logic
  console.log('Logging out...')
  // Clear auth token
  const authToken = useCookie('auth-token')
  authToken.value = null
  // Redirect to login
  navigateTo('/auth/login')
}

// Handle escape key
const handleEscape = (event) => {
  if (event.key === 'Escape') {
    sidebarOpen.value = false
    userMenuOpen.value = false
  }
}

// Handle click outside for user menu
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    userMenuOpen.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Custom scrollbar for sidebar */
.sidebar-scroll::-webkit-scrollbar {
  width: 4px;
}

.sidebar-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.sidebar-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.sidebar-scroll::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Navigation link styles */
.nav-link {
  position: relative;
}

.nav-link.router-link-active {
  @apply bg-blue-50 text-blue-700;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Dropdown animation */
.rotate-180 {
  transform: rotate(180deg);
}

/* Focus visible for better accessibility */
.focus\:ring-2:focus-visible {
  @apply ring-2 ring-blue-500 ring-opacity-50;
}

/* Active link indicator */
.nav-link.router-link-active {
  position: relative;
}

.nav-link.router-link-active::before {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: theme('colors.blue.600');
  border-radius: 2px 0 0 2px;
}
</style>