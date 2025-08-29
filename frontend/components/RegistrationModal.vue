<template>
  <BaseModal v-model="isOpen" @update:modelValue="$emit('update:modelValue', $event)">
    <!-- Step 1: Marketing Hooks -->
    <div v-if="currentStep === 1" class="space-y-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 mb-2">
          Sebelum Bergabung, Bantu Kami Memahami Anda
        </h2>
        <p class="text-sm text-gray-600">
          Darimana kamu mengetahui Ringan? Informasi ini membantu kami meningkatkan layanan.
        </p>
      </div>

      <div class="space-y-4">
        <label class="text-sm font-medium text-gray-900">
          Darimana kamu mengetahui kami?
        </label>
        
        <div class="space-y-3">
          <label
            v-for="option in sourceOptions"
            :key="option.value"
            class="flex items-center space-x-3 cursor-pointer group"
          >
            <input
              v-model="marketingData.source"
              :value="option.value"
              type="radio"
              class="w-4 h-4 text-green-500 border-gray-300 focus:ring-green-500 focus:ring-2"
            />
            <span class="text-sm text-gray-700 group-hover:text-gray-900">
              {{ option.label }}
            </span>
          </label>
          
          <!-- Custom input for "Lainnya" -->
          <div v-if="marketingData.source === 'other'" class="ml-7 mt-2">
            <input
              v-model="marketingData.customSource"
              type="text"
              placeholder="Sebutkan..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            />
          </div>
        </div>
      </div>

      <button
        @click="nextStep"
        :disabled="!isStep1Valid"
        :class="[
          'w-full h-11 rounded-md font-bold transition-all',
          isStep1Valid
            ? 'bg-green-500 hover:bg-green-600 text-white'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50'
        ]"
      >
        Lanjut ke Registrasi
      </button>
    </div>

    <!-- Step 2: Registration Form -->
    <div v-else-if="currentStep === 2" class="space-y-6">
      <div>
        <h2 class="text-base font-bold text-gray-900 mb-4">
          Isi Data Akun
        </h2>
      </div>

      <form @submit.prevent="submitRegistration" class="space-y-4">
        <!-- Nama Lengkap -->
        <div>
          <input
            v-model="form.name"
            type="text"
            placeholder="Nama Lengkap"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.name }"
          />
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>

        <!-- Email -->
        <div>
          <input
            v-model="form.email"
            type="email"
            placeholder="Email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              placeholder="Password (min 6 karakter)"
              required
              class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
          
          <!-- Password Strength Meter -->
          <div v-if="form.password" class="mt-2">
            <div class="flex space-x-1">
              <div
                v-for="i in 4"
                :key="i"
                :class="[
                  'h-1 rounded-full flex-1',
                  i <= passwordStrength ? getStrengthColor(passwordStrength) : 'bg-gray-200'
                ]"
              ></div>
            </div>
            <p class="text-xs mt-1" :class="getStrengthTextColor(passwordStrength)">
              {{ getStrengthText(passwordStrength) }}
            </p>
          </div>
        </div>

        <!-- Konfirmasi Password -->
        <div>
          <input
            v-model="form.confirmPassword"
            type="password"
            placeholder="Konfirmasi Password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.confirmPassword }"
          />
          <p v-if="errors.confirmPassword" class="text-red-500 text-xs mt-1">{{ errors.confirmPassword }}</p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="!isFormValid || isLoading"
          :class="[
            'w-full h-11 rounded-md font-bold transition-all flex items-center justify-center',
            isFormValid && !isLoading
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-50'
          ]"
        >
          <div v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          {{ isLoading ? 'Mendaftar...' : 'Daftar Sekarang' }}
        </button>

        <!-- Back Button and Login Link -->
        <div class="flex items-center justify-between pt-2">
          <button
            type="button"
            @click="prevStep"
            class="text-sm text-gray-600 hover:text-gray-900"
          >
            ← Kembali ke Pertanyaan Awal
          </button>
          
          <button
            type="button"
            @click="openLoginModal"
            class="text-sm text-green-500 hover:text-green-600"
          >
            Sudah punya akun? Masuk
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

const emit = defineEmits(['update:modelValue', 'openLogin'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Steps
const currentStep = ref(1)

// Marketing data
const marketingData = ref({
  source: '',
  customSource: ''
})

const sourceOptions = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'friends_family', label: 'Teman / Keluarga' },
  { value: 'google_search', label: 'Google Search' },
  { value: 'other', label: 'Lainnya' }
]

// Registration form
const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const errors = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

// Validation
const isStep1Valid = computed(() => {
  if (marketingData.value.source === 'other') {
    return marketingData.value.customSource.trim().length > 0
  }
  return marketingData.value.source.length > 0
})

const passwordStrength = computed(() => {
  const password = form.value.password
  if (!password) return 0
  
  let strength = 0
  if (password.length >= 6) strength++
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++
  if (password.match(/[0-9]/)) strength++
  if (password.match(/[^a-zA-Z0-9]/)) strength++
  
  return strength
})

const isFormValid = computed(() => {
  return (
    form.value.name.trim().length >= 3 &&
    isValidEmail(form.value.email) &&
    form.value.password.length >= 6 &&
    form.value.password === form.value.confirmPassword &&
    !Object.values(errors.value).some(error => error !== '')
  )
})

// Helper functions
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const getStrengthColor = (strength) => {
  const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500']
  return colors[strength - 1] || 'bg-gray-200'
}

const getStrengthTextColor = (strength) => {
  const colors = ['text-red-500', 'text-orange-500', 'text-yellow-500', 'text-green-500']
  return colors[strength - 1] || 'text-gray-400'
}

const getStrengthText = (strength) => {
  const texts = ['Lemah', 'Sedang', 'Kuat', 'Sangat Kuat']
  return texts[strength - 1] || ''
}

// Validation watchers
watch(() => form.value.name, (newName) => {
  if (newName && newName.trim().length < 3) {
    errors.value.name = 'Nama minimal 3 karakter'
  } else {
    errors.value.name = ''
  }
})

watch(() => form.value.email, (newEmail) => {
  if (newEmail && !isValidEmail(newEmail)) {
    errors.value.email = 'Format email tidak valid'
  } else {
    errors.value.email = ''
  }
})

watch(() => form.value.password, (newPassword) => {
  if (newPassword && newPassword.length < 6) {
    errors.value.password = 'Password minimal 6 karakter'
  } else {
    errors.value.password = ''
  }
})

watch(() => form.value.confirmPassword, (newConfirmPassword) => {
  if (newConfirmPassword && newConfirmPassword !== form.value.password) {
    errors.value.confirmPassword = 'Konfirmasi password tidak sama'
  } else {
    errors.value.confirmPassword = ''
  }
})

// Step navigation
const nextStep = () => {
  if (isStep1Valid.value) {
    currentStep.value = 2
  }
}

const prevStep = () => {
  currentStep.value = 1
  errorMessage.value = ''
}

const openLoginModal = () => {
  emit('openLogin')
  isOpen.value = false
}

// Registration submission
const submitRegistration = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    // Prepare registration data
    const registrationData = {
      name: form.value.name.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      marketing_source: marketingData.value.source,
      marketing_source_custom: marketingData.value.source === 'other' ? marketingData.value.customSource : null
    }

    // Make API call to register
    const response = await $fetch('/api/register', {
      method: 'POST',
      body: registrationData
    })

    // Success - close modal and redirect or show success message
    isOpen.value = false
    
    // Reset form
    resetForm()
    
    // Show success notification (you can implement toast notification)
    console.log('Registration successful:', response)
    
    // Redirect to dashboard or show welcome message
    // navigateTo('/dashboard')
    alert(`Registrasi berhasil! Selamat datang, ${form.value.name}!`)

  } catch (error) {
    console.error('Registration error:', error)
    
    if (error.data?.message) {
      if (error.data.message.includes('email')) {
        errors.value.email = 'Email sudah digunakan'
      } else {
        errorMessage.value = error.data.message
      }
    } else {
      errorMessage.value = 'Terjadi kesalahan. Silakan coba lagi.'
    }
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  currentStep.value = 1
  marketingData.value = { source: '', customSource: '' }
  form.value = { name: '', email: '', password: '', confirmPassword: '' }
  errors.value = { name: '', email: '', password: '', confirmPassword: '' }
  errorMessage.value = ''
}

// Reset form when modal is closed
watch(isOpen, (newValue) => {
  if (!newValue) {
    setTimeout(resetForm, 300) // Delay to allow for closing animation
  }
})
</script> 