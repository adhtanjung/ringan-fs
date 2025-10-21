<template>
  <div class="w-full">
    <div class="relative">
      <Input
        :placeholder="placeholder"
        v-model="searchTerm"
        class="pr-10"
        @focus="open = true"
      />
      <div class="absolute inset-y-0 right-0 flex items-center pr-3">
        <Loader2 v-if="loading" class="h-4 w-4 animate-spin text-gray-400" />
      </div>
    </div>
    <div v-if="open" class="mt-1 max-h-60 overflow-auto rounded-md border bg-white shadow">
      <div v-if="results.length === 0 && !loading" class="p-3 text-sm text-gray-500">No results</div>
      <button
        v-for="item in results"
        :key="valueExtractor(item)"
        type="button"
        class="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
        @click="selectItem(item)"
      >
        {{ labelExtractor(item) }}
      </button>
      <div v-if="hasMore" class="p-2">
        <Button variant="outline" size="sm" class="w-full" @click="loadMore" :disabled="loading">
          <Loader2 v-if="loading" class="h-4 w-4 animate-spin mr-2" /> Load more
        </Button>
      </div>
    </div>
    <div v-if="selectedLabel" class="mt-1 text-xs text-gray-600">Selected: {{ selectedLabel }}</div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Type to search...' },
  fetchUrl: { type: String, required: true },
  labelExtractor: { type: Function, default: (item) => item.label ?? String(item) },
  valueExtractor: { type: Function, default: (item) => item.value ?? String(item) },
})

const emit = defineEmits(['update:modelValue', 'select'])

const searchTerm = ref('')
const open = ref(false)
const loading = ref(false)
const results = ref([])
const page = ref(1)
const hasMore = ref(false)
const selectedLabel = computed(() => {
  const found = results.value.find(r => props.modelValue && props.modelValue === valueExtractor(r))
  return found ? labelExtractor(found) : ''
})

let debounceTimer
watch(searchTerm, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    results.value = []
    fetchResults()
  }, 300)
})

const fetchResults = async () => {
  try {
    loading.value = true
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'
    const params = new URLSearchParams()
    if (searchTerm.value) params.set('q', searchTerm.value)
    params.set('limit', '20')
    params.set('page', String(page.value))
    const url = `${adminApiUrl}${props.fetchUrl}?${params.toString()}`
    const resp = await $fetch(url)
    const items = resp?.data?.items ?? []
    const more = resp?.data?.has_more ?? false
    if (page.value === 1) results.value = items
    else results.value = [...results.value, ...items]
    hasMore.value = more
  } catch (e) {
    // noop or toast in parent
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (loading.value || !hasMore.value) return
  page.value += 1
  fetchResults()
}

const selectItem = (item) => {
  const val = valueExtractor(item)
  emit('update:modelValue', val)
  emit('select', item)
  open.value = false
}
</script>



