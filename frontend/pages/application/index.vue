<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="text-center">
      <div class="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <div class="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p class="text-gray-600">Mengarahkan ke beranda...</p>
    </div>
  </div>
</template>

<script setup>
// Redirect to home page immediately
await navigateTo('/application/home', { replace: true })
</script> 