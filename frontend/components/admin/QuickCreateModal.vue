<template>
  <BaseModal :modelValue="isOpen" @update:modelValue="closeModal">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4 pb-3 border-b">
        <h3 class="text-lg font-semibold text-gray-900">
          Create New {{ typeLabel }}
        </h3>
        <Button
          variant="ghost"
          size="icon"
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600"
        >
          <X class="h-4 w-4" />
        </Button>
      </div>

      <!-- Form -->
      <form @submit.prevent="saveItem" class="space-y-4">
        <!-- Domain Name (for domain type) -->
        <div v-if="type === 'domain'">
          <Label for="domain_name" class="text-sm font-medium">
            Domain Name
            <span class="text-red-500 ml-1">*</span>
          </Label>
          <Input
            id="domain_name"
            v-model="formData.domain_name"
            placeholder="e.g., Stress Management"
            required
            class="mt-1"
          />
        </div>

        <!-- Domain Code (for domain type) -->
        <div v-if="type === 'domain'">
          <Label for="domain_code" class="text-sm font-medium">
            Domain Code
            <span class="text-red-500 ml-1">*</span>
          </Label>
          <div class="mt-1 flex gap-2">
            <Input
              id="domain_code"
              v-model="formData.domain_code"
              placeholder="e.g., STR, ANX, TRA"
              required
              class="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              @click="checkForDuplicate('domain_code')"
              :disabled="!formData.domain_code || validationStatus.domain_code.loading"
              class="whitespace-nowrap flex-shrink-0"
            >
              <Loader2 v-if="validationStatus.domain_code.loading" class="h-4 w-4 animate-spin mr-1" />
              <CheckCircle v-else-if="validationStatus.domain_code.checked && !validationStatus.domain_code.exists" class="h-4 w-4 text-green-600 mr-1" />
              <XCircle v-else-if="validationStatus.domain_code.checked && validationStatus.domain_code.exists" class="h-4 w-4 text-red-600 mr-1" />
              <span class="hidden sm:inline">Check</span>
              <span class="sm:hidden">✓</span>
            </Button>
          </div>
          <!-- Validation status message -->
          <div class="mt-1 text-xs">
            <span v-if="validationStatus.domain_code.checked && !validationStatus.domain_code.exists" class="text-green-600">
              ✓ Available
            </span>
            <span v-else-if="validationStatus.domain_code.checked && validationStatus.domain_code.exists" class="text-red-600">
              ✗ Already exists
            </span>
          </div>
        </div>

        <!-- Type Name (for problem_type) -->
        <div v-if="type === 'problem_type'">
          <Label for="type_name" class="text-sm font-medium">
            Type Name
            <span class="text-red-500 ml-1">*</span>
          </Label>
          <div class="mt-1 flex gap-2">
            <Input
              id="type_name"
              v-model="formData.type_name"
              placeholder="e.g., Work Stress, Social Anxiety"
              required
              class="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              @click="checkForDuplicate('type_name')"
              :disabled="!formData.type_name || validationStatus.type_name.loading"
              class="whitespace-nowrap flex-shrink-0"
            >
              <Loader2 v-if="validationStatus.type_name.loading" class="h-4 w-4 animate-spin mr-1" />
              <CheckCircle v-else-if="validationStatus.type_name.checked && !validationStatus.type_name.exists" class="h-4 w-4 text-green-600 mr-1" />
              <XCircle v-else-if="validationStatus.type_name.checked && validationStatus.type_name.exists" class="h-4 w-4 text-red-600 mr-1" />
              <span class="hidden sm:inline">Check</span>
              <span class="sm:hidden">✓</span>
            </Button>
          </div>
          <!-- Validation status message -->
          <div class="mt-1 text-xs">
            <span v-if="validationStatus.type_name.checked && !validationStatus.type_name.exists" class="text-green-600">
              ✓ Available
            </span>
            <span v-else-if="validationStatus.type_name.checked && validationStatus.type_name.exists" class="text-red-600">
              ✗ Already exists
            </span>
          </div>
        </div>

        <!-- Description -->
        <div>
          <Label for="description" class="text-sm font-medium">
            Description
            <span class="text-red-500 ml-1">*</span>
          </Label>
          <Textarea
            id="description"
            v-model="formData.description"
            :placeholder="type === 'domain' ? 'Detailed description of this domain' : 'Detailed description of this problem type'"
            rows="3"
            required
            class="mt-1"
          />
        </div>

        <!-- Validation Errors -->
        <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-3">
          <div class="flex">
            <div class="flex-shrink-0">
              <AlertCircle class="h-5 w-5 text-red-400" />
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Validation Errors</h3>
              <div class="mt-2 text-sm text-red-700">
                <ul class="list-disc pl-5 space-y-1">
                  <li v-for="error in validationErrors" :key="error">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t">
          <Button
            type="button"
            variant="outline"
            @click="closeModal"
            :disabled="isSaving"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            :disabled="isSaving || validationErrors.length > 0 || !isValidationComplete"
          >
            <Loader2 v-if="isSaving" class="mr-2 h-4 w-4 animate-spin" />
            {{ isSaving ? 'Creating...' : 'Create' }}
          </Button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { X, AlertCircle, Loader2, CheckCircle, XCircle } from 'lucide-vue-next'

// shadcn-vue components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/toast/use-toast'
import BaseModal from '@/components/BaseModal.vue'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    required: true,
    validator: (value) => ['domain', 'problem_type'].includes(value)
  }
})

// Emits
const emit = defineEmits(['close', 'created'])

// Reactive data
const formData = reactive({
  domain_name: '',
  domain_code: '',
  type_name: '',
  description: '',
  is_active: true
})

const validationStatus = reactive({
  domain_code: { checked: false, exists: false, loading: false },
  type_name: { checked: false, exists: false, loading: false }
})

const isSaving = ref(false)
const validationErrors = ref([])

// Computed properties
const typeLabel = computed(() => {
  return props.type === 'domain' ? 'Domain' : 'Problem Type'
})

const isValidationComplete = computed(() => {
  if (props.type === 'domain') {
    if (!formData.domain_code) return false
    if (!validationStatus.domain_code.checked) return false
    if (validationStatus.domain_code.exists) return false
    return true
  }

  if (props.type === 'problem_type') {
    if (!formData.type_name) return false
    if (!validationStatus.type_name.checked) return false
    if (validationStatus.type_name.exists) return false
    return true
  }

  return true
})

// Methods
const closeModal = () => {
  if (!isSaving.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  formData.domain_name = ''
  formData.domain_code = ''
  formData.type_name = ''
  formData.description = ''
  formData.is_active = true

  validationStatus.domain_code = { checked: false, exists: false, loading: false }
  validationStatus.type_name = { checked: false, exists: false, loading: false }

  validationErrors.value = []
  isSaving.value = false
}

const checkForDuplicate = async (fieldKey) => {
  const config = useRuntimeConfig()
  const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

  validationStatus[fieldKey].loading = true

  try {
    let url = ''
    let value = ''

    if (fieldKey === 'domain_code') {
      value = formData.domain_code
      if (!value) {
        validationStatus[fieldKey].loading = false
        return
      }
      url = `${adminApiUrl}/dataset/validate/domain_types/${encodeURIComponent(value)}`
    } else if (fieldKey === 'type_name') {
      value = formData.type_name
      if (!value) {
        validationStatus[fieldKey].loading = false
        return
      }
      url = `${adminApiUrl}/dataset/validate/problem_types/${encodeURIComponent(value)}`
    }

    const response = await $fetch(url)

    validationStatus[fieldKey].checked = true
    validationStatus[fieldKey].exists = response.data.exists

    const { toast } = useToast()
    if (response.data.exists) {
      toast({
        title: 'Duplicate Found',
        description: `${fieldKey === 'domain_code' ? 'Domain code' : 'Type name'} already exists`,
        variant: 'destructive'
      })
    } else {
      toast({
        title: 'Validation Passed',
        description: `${fieldKey === 'domain_code' ? 'Domain code' : 'Type name'} is available`,
        variant: 'default'
      })
    }

  } catch (error) {
    console.error('Validation error:', error)
    const { toast } = useToast()
    toast({
      title: 'Validation Error',
      description: 'Failed to check for duplicates. Please try again.',
      variant: 'destructive'
    })
  } finally {
    validationStatus[fieldKey].loading = false
  }
}

const validateForm = () => {
  const errors = []

  if (props.type === 'domain') {
    if (!formData.domain_name) errors.push('Domain name is required')
    if (!formData.domain_code) errors.push('Domain code is required')
    if (!formData.description) errors.push('Description is required')

    if (!validationStatus.domain_code.checked) {
      errors.push('Please check for duplicate domain code before creating')
    } else if (validationStatus.domain_code.exists) {
      errors.push('Domain code already exists. Please choose a different one.')
    }
  }

  if (props.type === 'problem_type') {
    if (!formData.type_name) errors.push('Type name is required')
    if (!formData.description) errors.push('Description is required')

    if (!validationStatus.type_name.checked) {
      errors.push('Please check for duplicate type name before creating')
    } else if (validationStatus.type_name.exists) {
      errors.push('Type name already exists. Please choose a different one.')
    }
  }

  validationErrors.value = errors
  return errors.length === 0
}

const saveItem = async () => {
  if (!validateForm()) {
    return
  }

  isSaving.value = true

  try {
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

    let endpoint = ''
    let payload = {}

    if (props.type === 'domain') {
      endpoint = `${adminApiUrl}/dataset/domain_types`
      payload = {
        domain_name: formData.domain_name,
        domain_code: formData.domain_code,
        description: formData.description,
        is_active: formData.is_active
      }
    } else if (props.type === 'problem_type') {
      endpoint = `${adminApiUrl}/dataset/problem_types`
      payload = {
        type_name: formData.type_name,
        description: formData.description,
        is_active: formData.is_active
      }
    }

    const response = await $fetch(endpoint, {
      method: 'POST',
      body: payload
    })

    const { toast } = useToast()
    toast({
      title: 'Success',
      description: `${typeLabel.value} created successfully`,
      variant: 'default'
    })

    // Emit the created item
    emit('created', response.data)

    // Close modal
    closeModal()

  } catch (error) {
    console.error('Create error:', error)
    const { toast } = useToast()
    toast({
      title: 'Error',
      description: 'Failed to create item. Please try again.',
      variant: 'destructive'
    })
  } finally {
    isSaving.value = false
  }
}
</script>

