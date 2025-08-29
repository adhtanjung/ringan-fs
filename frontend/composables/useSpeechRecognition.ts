import { ref, onMounted, onUnmounted } from 'vue'

// Extend Window interface for speech recognition
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export const useSpeechRecognition = () => {
  const isSupported = ref(false)
  const isListening = ref(false)
  const transcript = ref('')
  const error = ref<string | null>(null)
  
  let recognition: any = null

  onMounted(() => {
    // Check if speech recognition is supported
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      isSupported.value = true
      
      // Create recognition instance
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition = new SpeechRecognition()
      
      // Configure recognition
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'id-ID' // Indonesian language
      
      // Set up event listeners
      recognition.onstart = () => {
        isListening.value = true
        error.value = null
      }
      
      recognition.onresult = (event: any) => {
        const result = event.results[0][0].transcript
        transcript.value = result
      }
      
      recognition.onerror = (event: any) => {
        error.value = `Speech recognition error: ${event.error}`
        isListening.value = false
      }
      
      recognition.onend = () => {
        isListening.value = false
      }
    }
  })

  onUnmounted(() => {
    if (recognition) {
      recognition.stop()
    }
  })

  const startListening = async () => {
    if (!recognition || isListening.value) return

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true })
      
      transcript.value = ''
      error.value = null
      recognition.start()
    } catch (err) {
      error.value = 'Microphone access denied'
    }
  }

  const stopListening = () => {
    if (recognition && isListening.value) {
      recognition.stop()
    }
  }

  return {
    isSupported,
    isListening,
    transcript,
    error,
    startListening,
    stopListening
  }
} 