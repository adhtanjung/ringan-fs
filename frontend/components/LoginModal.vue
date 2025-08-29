<template>
  <BaseModal v-model="isOpen" @update:modelValue="$emit('update:modelValue', $event)">
    <div class="space-y-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 mb-2">
          Masuk ke Akun Anda
        </h2>
        <p class="text-sm text-gray-600">
          Selamat datang kembali! Silakan masukkan kredensial Anda.
        </p>
      </div>

      <form @submit.prevent="submitLogin" class="space-y-4">
        <!-- Email -->
        <div>
          <input
            v-model="form.email"
            type="email"
            placeholder="Email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.email }"
          />
          <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
        </div>

        <!-- Password -->
        <div>
          <div class="relative">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Password"
              required
              class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.password }"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              <Eye v-if="!showPassword" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
          <p v-if="errors.password" class="text-red-500 text-xs mt-1">{{ errors.password }}</p>
        </div>

        <!-- Forgot Password Link -->
        <div class="text-right">
          <button
            type="button"
            @click="forgotPassword"
            class="text-sm text-purple-500 hover:text-purple-600"
          >
            Lupa Password?
          </button>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="!isFormValid || isLoading"
          :class="[
            'w-full h-11 rounded-md font-bold transition-all flex items-center justify-center',
            isFormValid && !isLoading
              ? 'bg-purple-600 hover:bg-purple-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50'
          ]"
        >
          <div v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          {{ isLoading ? 'Memproses...' : 'Masuk' }}
        </button>

        <!-- Register Link -->
        <div class="text-center pt-2">
          <button
            type="button"
            @click="openRegisterModal"
            class="text-sm text-green-500 hover:text-green-600"
          >
            Belum punya akun? Daftar sekarang
          </button>
        </div>
      </form>
    </div>

    <!-- Error Toast -->
    <div
      v-if="errorMessage"
      class="absolute top-4 left-4 right-4 bg-red-50 border border-red-200 rounded-md p-3"
    >
      <p class="text-red-700 text-sm">{{ errorMessage }}</p>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'openRegister'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Form data
const form = ref({
  email: '',
  password: ''
})

const errors = ref({
  email: '',
  password: ''
})

const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

// Validation
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const isFormValid = computed(() => {
  return (
    isValidEmail(form.value.email) &&
    form.value.password.length > 0 &&
    !Object.values(errors.value).some(error => error !== '')
  )
})

// Validation watchers
watch(() => form.value.email, (newEmail) => {
  if (newEmail && !isValidEmail(newEmail)) {
    errors.value.email = 'Format email tidak valid'
  } else {
    errors.value.email = ''
  }
})

watch(() => form.value.password, (newPassword) => {
  if (newPassword && newPassword.length === 0) {
    errors.value.password = 'Password tidak boleh kosong'
  } else {
    errors.value.password = ''
  }
})

// Methods
const submitLogin = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    // Make API call to login
    const response = await $fetch('/api/login', {
      method: 'POST',
      body: {
        email: form.value.email.trim(),
        password: form.value.password
      }
    })

    // Success - close modal and redirect
    isOpen.value = false
    resetForm()
    
    console.log('Login successful:', response)
    alert(`Selamat datang kembali, ${response.user.name}!`)
    
    // Redirect to dashboard
    // navigateTo('/dashboard')

  } catch (error) {
    console.error('Login error:', error)
    
    if (error.data?.message) {
      errorMessage.value = error.data.message
    } else {
      errorMessage.value = 'Email atau password salah.'
    }
  } finally {
    isLoading.value = false
  }
}

const forgotPassword = () => {
  alert('Fitur reset password akan segera hadir!')
}

const openRegisterModal = () => {
  emit('openRegister')
  isOpen.value = false
}

const resetForm = () => {
  form.value = { email: '', password: '' }
  errors.value = { email: '', password: '' }
  errorMessage.value = ''
}

// Reset form when modal is closed
watch(isOpen, (newValue) => {
  if (!newValue) {
    setTimeout(resetForm, 300)
  }
})
</script> 