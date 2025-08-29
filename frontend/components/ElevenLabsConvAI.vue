<template>
  <div class="elevenlabs-convai-container">
    <div v-if="!isLoaded" class="flex items-center justify-center py-8">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">Loading ConvAI Widget...</p>
      </div>
    </div>
    
    <elevenlabs-convai 
      v-show="isLoaded"
      :agent-id="agentId"
      @load="handleWidgetLoad"
    ></elevenlabs-convai>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  agentId: {
    type: String,
    required: true,
    default: 'agent_01jwfpv8y9e3ssvr5qh5r8rwzv'
  }
})

// Reactive data
const isLoaded = ref(false)
const scriptElement = ref(null)

// Handle widget load
const handleWidgetLoad = () => {
  isLoaded.value = true
}

// Load the ElevenLabs ConvAI script
const loadConvAIScript = () => {
  return new Promise((resolve, reject) => {
    // Check if script already exists
    const existingScript = document.querySelector('script[src*="convai-widget-embed"]')
    if (existingScript) {
      isLoaded.value = true
      resolve()
      return
    }

    // Create and load the script
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed'
    script.async = true
    script.type = 'text/javascript'
    
    script.onload = () => {
      // Wait a bit for the custom element to be defined
      setTimeout(() => {
        isLoaded.value = true
        resolve()
      }, 1000)
    }
    
    script.onerror = () => {
      console.error('Failed to load ElevenLabs ConvAI script')
      reject(new Error('Failed to load ConvAI script'))
    }

    document.head.appendChild(script)
    scriptElement.value = script
  })
}

onMounted(async () => {
  try {
    await loadConvAIScript()
  } catch (error) {
    console.error('Error loading ConvAI widget:', error)
  }
})

onUnmounted(() => {
  // Clean up script if component created it
  if (scriptElement.value && scriptElement.value.parentNode) {
    scriptElement.value.parentNode.removeChild(scriptElement.value)
  }
})
</script>

<style scoped>
.elevenlabs-convai-container {
  min-height: 400px;
  width: 100%;
}

/* Ensure the widget takes full width */
elevenlabs-convai {
  display: block;
  width: 100%;
  height: 400px;
}
</style> 