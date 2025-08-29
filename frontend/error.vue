<template>
  <div class="min-h-screen flex flex-col items-center justify-center">
    <div class="text-center px-4 py-10 max-w-md">
      <h1 class="text-4xl font-bold mb-4">{{ error?.statusCode === 404 ? 'Page not found' : 'Something went wrong' }}</h1>
      
      <p class="text-gray-600 mb-8">
        {{ error?.statusMessage || error?.message || 'Sorry, an unexpected error has occurred.' }}
      </p>
      
      <div class="flex gap-4 justify-center">
        <Button 
          @click="handleError"
          variant="default"
        >
          {{ error?.statusCode === 404 ? 'Go Home' : 'Try again' }}
        </Button>
        
        <Button 
          v-if="error?.statusCode !== 404"
          @click="clearError"
          variant="outline"
        >
          Go Home
        </Button>
      </div>
      
      <div v-if="isDevelopment" class="mt-8 text-left">
        <details class="bg-gray-100 p-4 rounded-md">
          <summary class="cursor-pointer font-medium">Error Details</summary>
          <pre class="mt-2 text-xs overflow-auto">{{ error }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'

const { error } = defineProps(['error'])
const config = useRuntimeConfig()

// Check if we're in development mode using runtime config and/or compile-time flag
const isDevelopment = computed(() => config.public.isDev || import.meta.dev)

const handleError = () => {
  if (error?.statusCode === 404) {
    // Go to homepage if page not found
    clearError({ redirect: '/' })
  } else {
    // Refresh the page for other errors
    clearError()
  }
}
</script> 