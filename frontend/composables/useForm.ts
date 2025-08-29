import { ref, computed } from 'vue'

export function useForm<T extends Record<string, any>>(initialValues: T) {
  const values = ref({ ...initialValues }) as Ref<T>
  const errors = ref<Partial<Record<keyof T, string>>>({})
  const isSubmitting = ref(false)
  
  const resetForm = () => {
    values.value = { ...initialValues }
    errors.value = {}
  }
  
  const setFieldValue = <K extends keyof T>(field: K, value: T[K]) => {
    values.value[field] = value
    // Clear error when field is modified
    if (errors.value[field]) {
      const newErrors = { ...errors.value }
      delete newErrors[field]
      errors.value = newErrors
    }
  }
  
  const setFieldError = <K extends keyof T>(field: K, message: string) => {
    errors.value = { ...errors.value, [field]: message }
  }
  
  const hasErrors = computed(() => Object.keys(errors.value).length > 0)
  
  return {
    values,
    errors,
    isSubmitting,
    hasErrors,
    resetForm,
    setFieldValue,
    setFieldError
  }
} 