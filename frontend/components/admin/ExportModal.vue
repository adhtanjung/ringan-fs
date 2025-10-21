<template>
  <Sheet :open="isOpen" @update:open="$emit('close')">
    <SheetContent side="right" class="w-full sm:max-w-lg md:max-w-2xl">
      <SheetHeader>
        <SheetTitle>Export Data</SheetTitle>
        <SheetDescription>
          Export data from the selected dataset in various formats
        </SheetDescription>
      </SheetHeader>

      <div class="grid gap-4 py-4">
        <!-- Data Type Selection -->
        <div v-if="!dataType" class="grid gap-2">
          <Label for="data-type">Data Type</Label>
          <Select v-model="selectedDataType">
            <SelectTrigger>
              <SelectValue placeholder="Select data type to export" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="dataType in dataTypes"
                :key="dataType.key"
                :value="dataType.key"
              >
                {{ dataType.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Show selected data type when filtered -->
        <div v-else class="grid gap-2">
          <Label for="data-type">Data Type</Label>
          <div class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md">
            <span class="text-sm text-gray-900">{{ dataTypes[0]?.label }}</span>
          </div>
        </div>

        <!-- Format Selection -->
        <div class="grid gap-2">
          <Label for="format">Export Format</Label>
          <Select v-model="selectedFormat">
            <SelectTrigger>
              <SelectValue placeholder="Select export format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="csv">CSV</SelectItem>
              <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
              <SelectItem value="json">JSON</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Optional Filters -->
        <div class="grid gap-2">
          <Label for="domain">Domain Filter (Optional)</Label>
          <Input
            id="domain"
            v-model="domainFilter"
            placeholder="e.g., anxiety, depression"
          />
        </div>

        <div class="flex items-center space-x-2">
          <Switch
            id="active-only"
            v-model:checked="activeOnly"
          />
          <Label for="active-only">Export only active items</Label>
        </div>
      </div>

      <SheetFooter>
        <Button variant="outline" @click="$emit('close')">
          Cancel
        </Button>
        <Button @click="handleExport" :disabled="!selectedDataType || !selectedFormat">
          Export Data
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Switch } from '@/components/ui/switch'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  dataType: {
    type: String,
    default: null
  }
})

// Emits
defineEmits(['close'])

// Reactive data
const selectedDataType = ref('')
const selectedFormat = ref('')
const domainFilter = ref('')
const activeOnly = ref(true)

// Data types configuration
const allDataTypes = [
  { key: 'problems', label: 'Problem Categories' },
  { key: 'assessments', label: 'Assessment Questions' },
  { key: 'suggestions', label: 'Therapeutic Suggestions' },
  { key: 'feedback_prompts', label: 'Feedback Prompts' },
  { key: 'next_actions', label: 'Next Actions' },
  { key: 'training_examples', label: 'Fine-tuning Examples' },
  { key: 'problem_types', label: 'Problem Types' },
  { key: 'domain_types', label: 'Domain Types' }
]

const dataTypes = computed(() => {
  if (props.dataType) {
    // Filter to only show the specified data type
    return allDataTypes.filter(dt => dt.key === props.dataType)
  }
  return allDataTypes
})

// Methods
const handleExport = async () => {
  try {
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

    // Build query parameters
    const params = new URLSearchParams({
      format: selectedFormat.value
    })

    if (domainFilter.value) {
      params.append('domain', domainFilter.value)
    }

    if (activeOnly.value) {
      params.append('is_active', 'true')
    }

    // Create download URL
    const downloadUrl = `${adminApiUrl}/import-export/export/${selectedDataType.value}?${params.toString()}`

    // Trigger download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${selectedDataType.value}_export.${selectedFormat.value}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Close modal
    emit('close')

  } catch (error) {
    console.error('Export failed:', error)
    alert('Export failed. Please try again.')
  }
}

// Watch for dataType prop changes and set selectedDataType
watch(() => props.dataType, (newDataType) => {
  if (newDataType) {
    selectedDataType.value = newDataType
  }
}, { immediate: true })
</script>