<template>
  <div class="min-h-screen">
    <!-- Header Navigation -->
    <header class="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-200/50 shadow-sm">
      <nav class="container-custom">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-2">
            <NuxtImg src="/image.png" alt="Ringan Logo" class="w-full h-8" />
            <!-- <NuxtImg src="/image.png" alt="Ringan Logo" class="w-8 h-8" /> -->
            <!-- <span class="text-xl font-bold text-gray-900">Ringan</span> -->
          </div>
          
          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <a href="#home" class="nav-link" :class="{ 'nav-link-active': activeSection === 'home' }">Beranda</a>
            <a href="#about" class="nav-link" :class="{ 'nav-link-active': activeSection === 'about' }">Tentang</a>
            <a href="#why" class="nav-link" :class="{ 'nav-link-active': activeSection === 'why' }">Mengapa</a>
            <a href="#how" class="nav-link" :class="{ 'nav-link-active': activeSection === 'how' }">Cara Kerja</a>
            <a href="#testimonials" class="nav-link" :class="{ 'nav-link-active': activeSection === 'testimonials' }">Testimoni</a>
            <a href="#features" class="nav-link" :class="{ 'nav-link-active': activeSection === 'features' }">Fitur</a>
          </div>
          
          <!-- CTA Buttons -->
          <div class="hidden md:flex items-center space-x-4">
            <Button 
              variant="outline" 
              size="sm" 
              class="border-purple-300 text-purple-700 hover:bg-purple-50"
              @click="openLoginModal"
            >
              Masuk
            </Button>
            <Button 
              size="sm" 
              class="btn-primary text-white"
              @click="openRegisterModal"
            >
              Mulai Gratis
            </Button>
          </div>
          
          <!-- Mobile Menu Button -->
          <button 
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X v-if="mobileMenuOpen" class="w-6 h-6 text-gray-600" />
            <Menu v-else class="w-6 h-6 text-gray-600" />
          </button>
        </div>
        
        <!-- Mobile Navigation -->
        <div 
          v-show="mobileMenuOpen" 
          class="md:hidden absolute top-16 left-0 right-0 bg-white border-b border-gray-200 shadow-lg"
        >
          <div class="p-4 space-y-4">
            <a href="#home" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'home' }">Beranda</a>
            <a href="#about" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'about' }">Tentang</a>
            <a href="#why" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'why' }">Mengapa</a>
            <a href="#how" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'how' }">Cara Kerja</a>
            <a href="#testimonials" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'testimonials' }">Testimoni</a>
            <a href="#features" @click="mobileMenuOpen = false" class="block nav-link" :class="{ 'nav-link-active': activeSection === 'features' }">Fitur</a>
            <div class="pt-4 border-t border-gray-200 space-y-2">
              <Button 
                variant="outline" 
                size="sm" 
                class="w-full border-purple-300 text-purple-700 hover:bg-purple-50"
                @click="openLoginModal"
              >
                Masuk
              </Button>
              <Button 
                size="sm" 
                class="w-full btn-primary text-white"
                @click="openRegisterModal"
              >
                Mulai Gratis
              </Button>
            </div>
          </div>
        </div>
      </nav>
    </header>
    
    <!-- Scroll Progress Indicator -->
    <ScrollProgress />
    
    <!-- Main Content with top padding for fixed header -->
    <main class="pt-16">
      <slot />
    </main>
    
    <!-- Floating Action Button -->
    <FloatingActionButton />
    
    <!-- Scroll to Top Button -->
    <ScrollToTop />

    <!-- Registration Modal -->
    <RegistrationModal 
      v-model="showRegisterModal" 
      @openLogin="openLoginModal"
    />

    <!-- Login Modal -->
    <LoginModal 
      v-model="showLoginModal" 
      @openRegister="openRegisterModal"
    />
  </div>
</template>

<script setup>
import { Menu, X } from 'lucide-vue-next'

// Mobile menu state
const mobileMenuOpen = ref(false)
// Active section tracking
const activeSection = ref('home')

// Modal states
const showRegisterModal = ref(false)
const showLoginModal = ref(false)

// Modal functions
const openRegisterModal = () => {
  showLoginModal.value = false
  showRegisterModal.value = true
  mobileMenuOpen.value = false // Close mobile menu if open
}

const openLoginModal = () => {
  showRegisterModal.value = false
  showLoginModal.value = true
  mobileMenuOpen.value = false // Close mobile menu if open
}

// Close mobile menu when clicking outside
onMounted(() => {
  const handleClickOutside = (event) => {
    if (!event.target.closest('header')) {
      mobileMenuOpen.value = false
    }
  }
  
  document.addEventListener('click', handleClickOutside)
  
  // Active section tracking
  const sections = ['home', 'about', 'why', 'how', 'testimonials', 'features']
  
  const handleScroll = () => {
    const scrollPosition = window.scrollY + 100 // Offset for header
    
    for (const sectionId of sections) {
      const element = document.getElementById(sectionId)
      if (element) {
        const { offsetTop, offsetHeight } = element
        if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
          activeSection.value = sectionId
          break
        }
      }
    }
  }
  
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll() // Initial check
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
    window.removeEventListener('scroll', handleScroll)
  })
})

// Smooth scroll behavior
onMounted(() => {
  // Add smooth scroll behavior to anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]')
  
  anchorLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      const targetId = link.getAttribute('href').substring(1)
      const targetElement = document.getElementById(targetId)
      
      if (targetElement) {
        const headerHeight = 64 // 16 * 4 = 64px (h-16)
        const targetPosition = targetElement.offsetTop - headerHeight
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        })
      }
    })
  })
})
</script>

<style scoped>
.nav-link {
  @apply text-gray-600 hover:text-gray-900 font-medium transition-colors duration-200 relative;
}

.nav-link-active {
  @apply text-purple-600 font-semibold;
}

.nav-link:hover::after,
.nav-link-active::after {
  content: '';
  @apply absolute -bottom-1 left-0 right-0 h-0.5 rounded-full;
  background: linear-gradient(135deg, #a855f7 0%, #8b5cf6 100%);
}

/* Header backdrop blur support */
@supports (backdrop-filter: blur(12px)) {
  header {
    backdrop-filter: blur(12px);
  }
}
</style> 