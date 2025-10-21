import { ref, onMounted, onUnmounted } from 'vue'

export function useAccessibility() {
  const prefersReducedMotion = ref(false)
  const prefersHighContrast = ref(false)
  const prefersDarkMode = ref(false)
  const screenReaderActive = ref(false)

  // Check for reduced motion preference
  const checkReducedMotion = () => {
    if (typeof window !== 'undefined') {
      prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    }
  }

  // Check for high contrast preference
  const checkHighContrast = () => {
    if (typeof window !== 'undefined') {
      prefersHighContrast.value = window.matchMedia('(prefers-contrast: high)').matches
    }
  }

  // Check for dark mode preference
  const checkDarkMode = () => {
    if (typeof window !== 'undefined') {
      prefersDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
  }

  // Detect screen reader usage
  const detectScreenReader = () => {
    if (typeof window !== 'undefined') {
      // Check for common screen reader indicators
      const hasScreenReader =
        window.navigator.userAgent.includes('NVDA') ||
        window.navigator.userAgent.includes('JAWS') ||
        window.navigator.userAgent.includes('VoiceOver') ||
        window.navigator.userAgent.includes('TalkBack') ||
        document.querySelector('[aria-hidden="false"]') !== null

      screenReaderActive.value = hasScreenReader
    }
  }

  // Get animation duration based on preferences
  const getAnimationDuration = (baseDuration: number = 300) => {
    return prefersReducedMotion.value ? 0 : baseDuration
  }

  // Get animation easing based on preferences
  const getAnimationEasing = (baseEasing: string = 'ease-in-out') => {
    return prefersReducedMotion.value ? 'linear' : baseEasing
  }

  // Check if animations should be disabled
  const shouldAnimate = () => {
    return !prefersReducedMotion.value
  }

  // Get focus styles based on high contrast preference
  const getFocusStyles = () => {
    return prefersHighContrast.value
      ? 'ring-4 ring-blue-500 ring-offset-4'
      : 'ring-2 ring-blue-500 ring-offset-2'
  }

  // Announce message to screen readers
  const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (typeof window !== 'undefined' && screenReaderActive.value) {
      const announcement = document.createElement('div')
      announcement.setAttribute('aria-live', priority)
      announcement.setAttribute('aria-atomic', 'true')
      announcement.className = 'sr-only'
      announcement.textContent = message

      document.body.appendChild(announcement)

      // Remove after announcement
      setTimeout(() => {
        document.body.removeChild(announcement)
      }, 1000)
    }
  }

  // Setup media query listeners
  const setupMediaQueryListeners = () => {
    if (typeof window === 'undefined') return

    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleReducedMotionChange = (e: MediaQueryListEvent) => {
      prefersReducedMotion.value = e.matches
    }

    const handleHighContrastChange = (e: MediaQueryListEvent) => {
      prefersHighContrast.value = e.matches
    }

    const handleDarkModeChange = (e: MediaQueryListEvent) => {
      prefersDarkMode.value = e.matches
    }

    reducedMotionQuery.addEventListener('change', handleReducedMotionChange)
    highContrastQuery.addEventListener('change', handleHighContrastChange)
    darkModeQuery.addEventListener('change', handleDarkModeChange)

    return () => {
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange)
      highContrastQuery.removeEventListener('change', handleHighContrastChange)
      darkModeQuery.removeEventListener('change', handleDarkModeChange)
    }
  }

  onMounted(() => {
    checkReducedMotion()
    checkHighContrast()
    checkDarkMode()
    detectScreenReader()

    const cleanup = setupMediaQueryListeners()

    return cleanup
  })

  return {
    prefersReducedMotion,
    prefersHighContrast,
    prefersDarkMode,
    screenReaderActive,
    getAnimationDuration,
    getAnimationEasing,
    shouldAnimate,
    getFocusStyles,
    announceToScreenReader
  }
}





