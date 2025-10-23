<template>
  <Dialog :open="isOpen" @update:open="closeModal">
    <DialogContent class="max-w-7xl max-h-[90vh]">
      <DialogHeader>
        <DialogTitle>{{ isEditing ? 'Edit' : 'Create' }} {{ dataTypeLabel }}</DialogTitle>
        <DialogDescription>
          {{ isEditing ? 'Update the information below' : 'Fill in the details to create a new item' }}
        </DialogDescription>
      </DialogHeader>

      <!-- Form -->
      <TooltipProvider>
        <form @submit.prevent="saveItem" class="space-y-6">
        <ScrollArea class="h-[60vh] pr-4">
          <!-- Dynamic Form Fields -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <div
            v-for="field in formFields"
            :key="field.key"
            :class="field.fullWidth ? 'lg:col-span-2' : ''"
          >
            <!-- Text Input -->
            <div v-if="field.type === 'text'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div class="mt-1 flex flex-col sm:flex-row gap-2">
                <Input
                  :id="field.key"
                  v-model="formData[field.key]"
                  :placeholder="field.placeholder"
                  :required="field.required"
                  :disabled="isEditing && props.dataType === 'problems' && field.key === 'sub_category_id'"
                  class="flex-1"
                />
                <!-- Validation button for domain_code and type_name -->
                <Button
                  v-if="(dataType === 'domain_types' && field.key === 'domain_code') || (dataType === 'problem_types' && (field.key === 'type_name' || field.key === 'category_id')) || (dataType === 'problems' && field.key === 'sub_category_id') || (dataType === 'assessments' && field.key === 'question_id')"
                  type="button"
                  variant="outline"
                  size="sm"
                  @click="checkForDuplicate(field.key)"
                  :disabled="!formData[field.key] || validationStatus[field.key].loading || (isEditing && props.dataType === 'problems' && field.key === 'sub_category_id')"
                  class="whitespace-nowrap flex-shrink-0"
                >
                  <Loader2 v-if="validationStatus[field.key].loading" class="h-4 w-4 animate-spin mr-1" />
                  <CheckCircle v-else-if="validationStatus[field.key].checked && !validationStatus[field.key].exists" class="h-4 w-4 text-green-600 mr-1" />
                  <XCircle v-else-if="validationStatus[field.key].checked && validationStatus[field.key].exists" class="h-4 w-4 text-red-600 mr-1" />
                  <span class="hidden sm:inline">Check</span>
                  <span class="sm:hidden">✓</span>
                </Button>
              </div>
              <!-- Validation status message -->
              <div v-if="(dataType === 'domain_types' && field.key === 'domain_code') || (dataType === 'problem_types' && (field.key === 'type_name' || field.key === 'category_id')) || (dataType === 'problems' && field.key === 'sub_category_id') || (dataType === 'assessments' && field.key === 'question_id')" class="mt-1 text-xs">
                <span v-if="validationStatus[field.key].checked && !validationStatus[field.key].exists" class="text-green-600">
                  ✓ Available
                </span>
                <span v-else-if="validationStatus[field.key].checked && validationStatus[field.key].exists" class="text-red-600">
                  ✗ Already exists
                </span>
              </div>
            </div>

            <!-- Textarea -->
            <div v-else-if="field.type === 'textarea'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Textarea
                :id="field.key"
                v-model="formData[field.key]"
                :rows="field.rows || 3"
                :placeholder="field.placeholder"
                :required="field.required"
                class="mt-1"
              />
            </div>

            <!-- Select Dropdown -->
            <div v-else-if="field.type === 'select' && !(props.dataType === 'assessments' && field.key === 'sub_category_id')">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Select v-model="formData[field.key]" :required="field.required">
                <SelectTrigger class="mt-1">
                  <SelectValue :placeholder="field.placeholder || 'Select an option'" />
                </SelectTrigger>
                <SelectContent>
                  <template v-if="field.options && field.options.length">
                    <SelectItem
                      v-for="option in field.options"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </SelectItem>
                  </template>
                  <template v-else-if="field.key === 'sub_category_id' && dropdownOptions.sub_category_id && dropdownOptions.sub_category_id.length">
                    <SelectItem
                      v-for="option in dropdownOptions.sub_category_id"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </SelectItem>
                  </template>
                </SelectContent>
              </Select>
            </div>

            <!-- Async search select for assessments sub_category_id -->
            <div v-else-if="props.dataType === 'assessments' && field.key === 'sub_category_id'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <AsyncSearchSelect
                v-model="formData.sub_category_id"
                placeholder="Type to search subcategories by ID, category, or description"
                fetch-url="/dataset/problems/subcategories"
              />
            </div>

            <!-- Multi-select Tags -->
            <div v-else-if="field.type === 'tags'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div class="mt-1">
                <div class="flex flex-wrap gap-2 mb-2">
                  <Badge
                    v-for="(tag, index) in formData[field.key] || []"
                    :key="index"
                    variant="secondary"
                    class="flex items-center gap-1"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      @click="removeTag(field.key, index)"
                      class="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                    >
                      <X class="h-3 w-3" />
                    </button>
                  </Badge>
                </div>
                <div class="flex gap-2">
                  <Input
                    v-model="newTag[field.key]"
                    :placeholder="field.placeholder"
                    class="flex-1"
                    @keydown.enter.prevent="addTag(field.key)"
                    @keydown.comma.prevent="addTag(field.key)"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    @click="addTag(field.key)"
                  >
                    Add
                  </Button>
                </div>
              </div>
            </div>

            <!-- Number Input -->
            <div v-else-if="field.type === 'number' && !(props.dataType === 'assessments' && (field.key === 'scale_min' || field.key === 'scale_max') && !showScaleFields)">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Input
                :id="field.key"
                v-model.number="formData[field.key]"
                type="number"
                :min="field.min"
                :max="field.max"
                :step="field.step"
                :placeholder="field.placeholder"
                :required="field.required"
                class="mt-1"
              />
            </div>

            <!-- Scale fields for assessments -->
            <div v-else-if="props.dataType === 'assessments' && (field.key === 'scale_min' || field.key === 'scale_max') && showScaleFields">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Input
                :id="field.key"
                v-model.number="formData[field.key]"
                type="number"
                :min="field.min"
                :max="field.max"
                :step="field.step || 1"
                :placeholder="field.placeholder"
                :required="field.required"
                :readonly="true"
                class="mt-1 bg-gray-100"
              />
              <p class="mt-1 text-xs text-gray-500">Fixed at {{ field.key === 'scale_min' ? '1' : '4' }} for standardized 1-4 scale</p>
            </div>

            <!-- Scale label fields for assessments -->
            <div v-else-if="props.dataType === 'assessments' && field.key.startsWith('scale_label_') && showScaleFields">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Input
                :id="field.key"
                v-model="formData[field.key]"
                type="text"
                :placeholder="getDefaultScaleLabel(field.key)"
                :required="field.required"
                class="mt-1"
              />
              <p class="mt-1 text-xs text-gray-500">Label for scale value {{ field.key.split('_')[2] }}</p>
            </div>

            <!-- Options (tags) for assessments multiple_choice -->
            <div v-else-if="props.dataType === 'assessments' && field.key === 'options' && showOptionsField">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div class="mt-1">
                <div class="flex flex-wrap gap-2 mb-2">
                  <Badge
                    v-for="(tag, index) in formData[field.key] || []"
                    :key="index"
                    variant="secondary"
                    class="flex items-center gap-1"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      @click="removeTag(field.key, index)"
                      class="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                    >
                      <X class="h-3 w-3" />
                    </button>
                  </Badge>
                </div>
                <div class="flex gap-2">
                  <Input
                    v-model="newTag[field.key]"
                    :placeholder="field.placeholder || 'Add option'"
                    class="flex-1"
                    @keydown.enter.prevent="addTag(field.key)"
                    @keydown.comma.prevent="addTag(field.key)"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    @click="addTag(field.key)"
                  >
                    Add
                  </Button>
                </div>
                <p class="mt-1 text-xs text-gray-500">Add at least two distinct options</p>
              </div>
            </div>

            <!-- Switch -->
            <div v-else-if="field.type === 'switch'">
              <div class="flex items-center space-x-2">
                <Switch
                  :id="field.key"
                  v-model="formData[field.key]"
                />
                <div class="flex items-center gap-1">
                  <Tooltip>
                    <TooltipTrigger as-child>
                      <Label :for="field.key" class="text-sm font-medium cursor-help">
                        {{ field.label }}
                      </Label>
                    </TooltipTrigger>
                    <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs">
                      <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                    </TooltipContent>
                  </Tooltip>
                  <Tooltip v-if="fieldDescriptions[field.key]">
                    <TooltipTrigger as-child>
                      <Info class="h-3.5 w-3.5 text-gray-400 cursor-help" />
                    </TooltipTrigger>
                    <TooltipContent class="max-w-xs">
                      <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
              </div>
            </div>

            <!-- JSON Editor -->
            <div v-else-if="field.type === 'json'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <Textarea
                :id="field.key"
                v-model="jsonFields[field.key]"
                :rows="field.rows || 4"
                :placeholder="field.placeholder"
                class="mt-1 font-mono text-xs"
                @blur="validateJson(field.key)"
              />
              <p v-if="jsonErrors[field.key]" class="mt-1 text-sm text-red-600">
                {{ jsonErrors[field.key] }}
              </p>
            </div>

            <!-- Select with Create -->
            <div v-else-if="field.type === 'select-with-create'">
              <div class="flex items-center gap-1">
                <Tooltip>
                  <TooltipTrigger as-child>
                    <Label :for="field.key" class="text-sm font-medium cursor-help">
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500 ml-1">*</span>
                    </Label>
                  </TooltipTrigger>
                  <TooltipContent v-if="fieldDescriptions[field.key]" class="max-w-xs bg-blue-700 text-white">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip v-if="fieldDescriptions[field.key]">
                  <TooltipTrigger as-child>
                    <button
                      type="button"
                      class="inline-flex items-center justify-center w-4 h-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent class="max-w-xs">
                    <p class="text-sm">{{ fieldDescriptions[field.key] }}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div class="mt-1 flex gap-2">
                <Select v-model="formData[field.key]" class="flex-1">
                  <SelectTrigger>
                    <SelectValue :placeholder="'Select ' + field.label" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="option in dropdownOptions[field.key]"
                      :key="option[field.valueKey]"
                      :value="option[field.valueKey]"
                    >
                      {{ option[field.labelKey] }}
                    </SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  @click="openQuickCreate(field.createType, field.key)"
                  class="flex-shrink-0"
                >
                  <Plus class="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        </ScrollArea>

        <!-- Validation Errors -->
        <Alert v-if="validationErrors.length > 0" variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertTitle>Validation Errors</AlertTitle>
          <AlertDescription>
            <ul class="list-disc pl-5 space-y-1">
              <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
          </AlertDescription>
        </Alert>

        <!-- Validation Requirement Message -->
        <Alert v-if="!isValidationComplete && (dataType === 'domain_types' || dataType === 'problem_types')" variant="warning">
          <AlertCircle class="h-4 w-4" />
          <AlertTitle>Validation Required</AlertTitle>
          <AlertDescription>
            <span v-if="dataType === 'domain_types'">
              Please check for duplicate domain code before saving.
            </span>
            <span v-else-if="dataType === 'problem_types'">
              Please check for duplicate type name before saving.
            </span>
          </AlertDescription>
        </Alert>

        <Separator class="my-6" />

        <!-- Action Buttons -->
        <DialogFooter>
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
            @click="saveItem"
          >
            <Loader2 v-if="isSaving" class="mr-2 h-4 w-4 animate-spin" />
            {{ isSaving ? 'Saving...' : (isEditing ? 'Update' : 'Create') }}
          </Button>
        </DialogFooter>
        </form>
      </TooltipProvider>

    <!-- Quick Create Modal -->
    <QuickCreateModal
      :is-open="showQuickCreate"
      :type="quickCreateType"
      @close="closeQuickCreate"
      @created="handleQuickCreateSuccess"
    />
  </DialogContent>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { X, AlertCircle, Loader2, CheckCircle, XCircle, Plus } from 'lucide-vue-next'

// shadcn-vue components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import QuickCreateModal from '@/components/admin/QuickCreateModal.vue'
import AsyncSearchSelect from '@/components/admin/AsyncSearchSelect.vue'
import { columnConfigs } from '@/composables/useDatasetManagement'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  dataType: {
    type: String,
    required: true
  },
  item: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// Reactive data
const formData = reactive({})
const jsonFields = reactive({})
const jsonErrors = reactive({})
const newTag = reactive({})
const isSaving = ref(false)
const validationErrors = ref([])

// Validation state
const validationStatus = reactive({
  domain_code: { checked: false, exists: false, loading: false },
  type_name: { checked: false, exists: false, loading: false },
  category_id: { checked: false, exists: false, loading: false },
  sub_category_id: { checked: false, exists: false, loading: false },
  question_id: { checked: false, exists: false, loading: false }
})

// Dropdown options and quick create state
const dropdownOptions = reactive({
  domain: [],
  category: [],
  sub_category_id: []
})
const showQuickCreate = ref(false)
const quickCreateType = ref(null)
const quickCreateFieldKey = ref(null)

// Computed properties
const isEditing = computed(() => !!props.item)

const fieldDescriptions = computed(() => {
  const config = columnConfigs[props.dataType] || []
  const descMap = {}
  config.forEach(col => {
    descMap[col.key] = col.description
  })
  return descMap
})

const isValidationComplete = computed(() => {
  // For domain_types, check if domain_code validation is complete and passed
  if (props.dataType === 'domain_types') {
    if (!formData.domain_code) return false // No domain code entered
    if (!validationStatus.domain_code.checked) return false // Not validated yet
    if (validationStatus.domain_code.exists) return false // Duplicate exists
    return true // Validation complete and passed
  }

  // For problem_types, check if type_name validation is complete and passed
  if (props.dataType === 'problem_types') {
    if (!formData.type_name) return false // No type name entered
    if (!validationStatus.type_name.checked) return false // Not validated yet
    if (validationStatus.type_name.exists) return false // Duplicate exists
    return true // Validation complete and passed
  }

  // For other data types, no validation required
  return true
})

// Response type helpers (assessments)
const selectedResponseType = computed(() => formData.response_type)
const showScaleFields = computed(() => props.dataType === 'assessments' && selectedResponseType.value === 'scale')
const showOptionsField = computed(() => props.dataType === 'assessments' && selectedResponseType.value === 'multiple_choice')

const dataTypeLabel = computed(() => {
  const labels = {
    problems: 'Problem Category',
    assessments: 'Assessment Question',
    suggestions: 'Therapeutic Suggestion',
    feedback_prompts: 'Feedback Prompt',
    next_actions: 'Next Action',
    training_examples: 'Fine-tuning Example',
    domain_types: 'Domain Type',
    problem_types: 'Problem Type'
  }
  return labels[props.dataType] || 'Item'
})

const formFields = computed(() => {
  const fieldConfigs = {
    problems: [
      { key: 'problem_name', label: 'Problem Name', type: 'text', required: true, placeholder: 'e.g., Work Stress' },
      {
        key: 'domain',
        label: 'Domain',
        type: 'select-with-create',
        required: true,
        fetchEndpoint: '/dataset/domain_types',
        createType: 'domain',
        valueKey: 'domain_code',
        labelKey: 'domain_name'
      },
      {
        key: 'category',
        label: 'Category',
        type: 'select-with-create',
        required: true,
        fetchEndpoint: '/dataset/problem_types',
        createType: 'problem_type',
        valueKey: 'type_name',
        labelKey: 'type_name'
      },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3, fullWidth: true },
      { key: 'severity_level', label: 'Severity Level', type: 'number', min: 1, max: 5, placeholder: '1-5' },
      { key: 'sub_category_id', label: 'Subcategory ID', type: 'text', required: true, placeholder: 'e.g., STR_01_01, ANX_001_01' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    assessments: [
      { key: 'question_id', label: 'Question ID', type: 'text', required: true, placeholder: 'e.g., Q001, Q0001' },
      { key: 'sub_category_id', label: 'Subcategory ID', type: 'select', required: true, placeholder: 'Select subcategory' },
      { key: 'question_text', label: 'Question Text', type: 'textarea', required: true, rows: 2, fullWidth: true },
      { key: 'response_type', label: 'Response Type', type: 'select', required: true, options: [
        { value: 'scale', label: 'Scale' },
        { value: 'multiple_choice', label: 'Multiple Choice' },
        { value: 'text', label: 'Text' },
        { value: 'boolean', label: 'Boolean' }
      ]},
      { key: 'scale_min', label: 'Scale Min', type: 'number', min: 1, max: 4, readonly: true },
      { key: 'scale_max', label: 'Scale Max', type: 'number', min: 1, max: 4, readonly: true },
      { key: 'scale_label_1', label: 'Scale Label 1', type: 'text', placeholder: 'Not at all' },
      { key: 'scale_label_2', label: 'Scale Label 2', type: 'text', placeholder: 'A little' },
      { key: 'scale_label_3', label: 'Scale Label 3', type: 'text', placeholder: 'Quite a bit' },
      { key: 'scale_label_4', label: 'Scale Label 4', type: 'text', placeholder: 'Very much' },
      { key: 'options', label: 'Options', type: 'tags', placeholder: 'Add option' },
      { key: 'next_step', label: 'Next Step', type: 'text', placeholder: 'Next step logic' },
      { key: 'clusters', label: 'Clusters', type: 'text', placeholder: 'Question clusters' },
      { key: 'batch_id', label: 'Batch ID', type: 'text', placeholder: 'e.g., BATCH_001' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    suggestions: [
      { key: 'suggestion_id', label: 'Suggestion ID', type: 'text', required: true, placeholder: 'e.g., S_STR_001, S_ANX_001' },
      { key: 'sub_category_id', label: 'Subcategory ID', type: 'text', required: true, placeholder: 'e.g., STR_01_01, ANX_001_01' },
      { key: 'cluster', label: 'Cluster', type: 'text', placeholder: 'e.g., coping_strategies' },
      { key: 'suggestion_text', label: 'Suggestion Text', type: 'textarea', required: true, rows: 4, fullWidth: true },
      { key: 'resource_link', label: 'Resource Link', type: 'text', placeholder: 'https://example.com' },
      { key: 'evidence_base', label: 'Evidence Base', type: 'text', placeholder: 'e.g., CBT, ACT' },
      { key: 'difficulty_level', label: 'Difficulty Level', type: 'number', min: 1, max: 3 },
      { key: 'estimated_duration', label: 'Estimated Duration', type: 'text', placeholder: 'e.g., 15 minutes' },
      { key: 'tags', label: 'Tags', type: 'tags', placeholder: 'Add tag' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    feedback_prompts: [
      { key: 'prompt_id', label: 'Prompt ID', type: 'text', required: true, placeholder: 'e.g., P_STR_001, P_ANX_001' },
      { key: 'stage', label: 'Stage', type: 'select', required: true, options: [
        { value: 'post_suggestion', label: 'Post Suggestion' },
        { value: 'ongoing', label: 'Ongoing' },
        { value: 'followup', label: 'Follow-up' }
      ]},
      { key: 'prompt_text', label: 'Prompt Text', type: 'textarea', required: true, rows: 3, fullWidth: true },
      { key: 'next_action_id', label: 'Next Action ID', type: 'text', required: true, placeholder: 'e.g., ACTION_001' },
      { key: 'context', label: 'Context', type: 'textarea', rows: 2, placeholder: 'Additional context' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    next_actions: [
      { key: 'action_id', label: 'Action ID', type: 'text', required: true, placeholder: 'e.g., A_001, A_0001' },
      { key: 'action_type', label: 'Action Type', type: 'select', required: true, options: [
        { value: 'continue_same', label: 'Continue Same' },
        { value: 'show_problem_menu', label: 'Show Problem Menu' },
        { value: 'end_session', label: 'End Session' },
        { value: 'escalate', label: 'Escalate' },
        { value: 'schedule_followup', label: 'Schedule Follow-up' }
      ]},
      { key: 'action_name', label: 'Action Name', type: 'text', required: true, placeholder: 'e.g., Schedule Meeting' },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3, fullWidth: true },
      { key: 'parameters', label: 'Parameters', type: 'json', placeholder: '{"key": "value"}', rows: 3 },
      { key: 'conditions', label: 'Conditions', type: 'json', placeholder: '{"condition": "value"}', rows: 3 },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    training_examples: [
      { key: 'example_id', label: 'Example ID', type: 'text', required: true, placeholder: 'e.g., E_001, E_0001' },
      { key: 'domain', label: 'Domain', type: 'select', required: true, options: [
        { value: 'stress', label: 'Stress' },
        { value: 'anxiety', label: 'Anxiety' },
        { value: 'trauma', label: 'Trauma' },
        { value: 'general', label: 'General' }
      ]},
      { key: 'problem', label: 'Problem', type: 'text', placeholder: 'Problem description' },
      { key: 'conversation_id', label: 'Conversation ID', type: 'text', placeholder: 'e.g., CONV_001' },
      { key: 'user_intent', label: 'User Intent', type: 'select', required: true, options: [
        { value: 'problem_identification', label: 'Problem Identification' },
        { value: 'assessment_response', label: 'Assessment Response' },
        { value: 'seeking_help', label: 'Seeking Help' },
        { value: 'emotional_expression', label: 'Emotional Expression' },
        { value: 'progress_update', label: 'Progress Update' },
        { value: 'clarification', label: 'Clarification' },
        { value: 'resistance', label: 'Resistance' },
        { value: 'gratitude', label: 'Gratitude' }
      ]},
      { key: 'prompt', label: 'Prompt', type: 'textarea', required: true, rows: 3, fullWidth: true },
      { key: 'completion', label: 'Completion', type: 'textarea', required: true, rows: 4, fullWidth: true },
      { key: 'context', label: 'Context', type: 'textarea', rows: 2, placeholder: 'Additional context' },
      { key: 'quality_score', label: 'Quality Score', type: 'number', min: 0, max: 1, step: 0.1 },
      { key: 'tags', label: 'Tags', type: 'tags', placeholder: 'Add tag' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    domain_types: [
      { key: 'domain_name', label: 'Domain Name', type: 'text', required: true, placeholder: 'e.g., Stress Management' },
      { key: 'domain_code', label: 'Domain Code', type: 'text', required: true, placeholder: 'e.g., STR, ANX, TRA' },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3, fullWidth: true, placeholder: 'Detailed description of this domain' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ],
    problem_types: [
      { key: 'type_name', label: 'Type Name', type: 'text', required: true, placeholder: 'e.g., Work Stress, Social Anxiety' },
      { key: 'category_id', label: 'Category ID', type: 'text', required: true, placeholder: 'e.g., STR_01, ANX_001' },
      { key: 'description', label: 'Description', type: 'textarea', required: true, rows: 3, fullWidth: true, placeholder: 'Detailed description of this problem type' },
      { key: 'is_active', label: 'Active', type: 'switch' }
    ]
  }

  return fieldConfigs[props.dataType] || []
})

// Methods
const closeModal = () => {
  if (!isSaving.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    delete formData[key]
  })
  Object.keys(jsonFields).forEach(key => {
    delete jsonFields[key]
  })
  Object.keys(jsonErrors).forEach(key => {
    delete jsonErrors[key]
  })
  Object.keys(newTag).forEach(key => {
    delete newTag[key]
  })
  validationErrors.value = []
  isSaving.value = false

  // Reset validation status
  validationStatus.domain_code = { checked: false, exists: false, loading: false }
  validationStatus.type_name = { checked: false, exists: false, loading: false }
  validationStatus.category_id = { checked: false, exists: false, loading: false }
  validationStatus.sub_category_id = { checked: false, exists: false, loading: false }
  validationStatus.question_id = { checked: false, exists: false, loading: false }
}

const initializeForm = async () => {
  resetForm()

  // Fetch dropdown options for select-with-create fields
  formFields.value.forEach(field => {
    if (field.type === 'select-with-create') {
      fetchDropdownOptions(field.fetchEndpoint, field.key)
    }
    if (props.dataType === 'assessments' && field.key === 'sub_category_id' && field.type === 'select') {
      // initial empty fetch (no q) or first page
      fetchDropdownOptions('/dataset/problems/subcategories', 'sub_category_id')
    }
  })

  if (props.item) {
    // Edit mode - populate with existing data
    Object.assign(formData, { ...props.item })

    // Handle JSON fields
    formFields.value.forEach(field => {
      if (field.type === 'json' && props.item[field.key]) {
        jsonFields[field.key] = JSON.stringify(props.item[field.key], null, 2)
      }
    })

    // Handle scale_labels for assessments
    if (props.dataType === 'assessments' && props.item.scale_labels) {
      formData.scale_label_1 = props.item.scale_labels['1'] || 'Not at all'
      formData.scale_label_2 = props.item.scale_labels['2'] || 'A little'
      formData.scale_label_3 = props.item.scale_labels['3'] || 'Quite a bit'
      formData.scale_label_4 = props.item.scale_labels['4'] || 'Very much'
    }
  } else {
    // Create mode - set defaults
    formFields.value.forEach(field => {
      if (field.type === 'switch') {
        formData[field.key] = true
      } else if (field.type === 'tags') {
        formData[field.key] = []
      } else if (field.type === 'json') {
        jsonFields[field.key] = ''
      }
    })

    // Set default scale labels for assessments
    if (props.dataType === 'assessments') {
      formData.scale_label_1 = 'Not at all'
      formData.scale_label_2 = 'A little'
      formData.scale_label_3 = 'Quite a bit'
      formData.scale_label_4 = 'Very much'
    }
  }
}

const validateJson = (fieldKey) => {
  const value = jsonFields[fieldKey]
  if (!value) {
    delete jsonErrors[fieldKey]
    return
  }

  try {
    const parsed = JSON.parse(value)
    formData[fieldKey] = parsed
    delete jsonErrors[fieldKey]
  } catch (error) {
    jsonErrors[fieldKey] = 'Invalid JSON format'
  }
}

const addTag = (fieldKey) => {
  const value = newTag[fieldKey]?.trim()
  if (value && !formData[fieldKey]?.includes(value)) {
    if (!formData[fieldKey]) {
      formData[fieldKey] = []
    }
    formData[fieldKey].push(value)
    newTag[fieldKey] = ''
  }
}

const removeTag = (fieldKey, index) => {
  if (formData[fieldKey]) {
    formData[fieldKey].splice(index, 1)
  }
}

const checkForDuplicate = async (fieldKey) => {
  const config = useRuntimeConfig()
  const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'

  // Set loading state
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
    } else if (fieldKey === 'question_id') {
      value = formData.question_id
      if (!value) {
        validationStatus[fieldKey].loading = false
        return
      }
      url = `${adminApiUrl}/dataset/validate/assessments/question_id/${encodeURIComponent(value)}`
    } else if (fieldKey === 'category_id') {
      value = formData.category_id
      if (!value) {
        validationStatus[fieldKey].loading = false
        return
      }
      url = `${adminApiUrl}/dataset/validate/problem_types/category_id/${encodeURIComponent(value)}`
    } else if (fieldKey === 'sub_category_id') {
      value = formData.sub_category_id
      if (!value) {
        validationStatus[fieldKey].loading = false
        return
      }
      url = `${adminApiUrl}/dataset/validate/problems/sub_category_id/${encodeURIComponent(value)}`
    }

    // Add exclude_id parameter if editing
    if (props.item?.id) {
      url += `?exclude_id=${props.item.id}`
    }

    const response = await $fetch(url)

    // Update validation status
    validationStatus[fieldKey].checked = true
    validationStatus[fieldKey].exists = response.data.exists

    // Show toast notification
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

const fetchDropdownOptions = async (endpoint, key) => {
  try {
    const config = useRuntimeConfig()
    const adminApiUrl = config.public.adminApiUrl || 'http://localhost:8000/api/v1/admin'
    const url = `${adminApiUrl}${endpoint}`

    const response = await $fetch(url)
    dropdownOptions[key] = response.data?.items || []
  } catch (error) {
    console.error(`Error fetching ${key} options:`, error)
    dropdownOptions[key] = []
  }
}

const openQuickCreate = (type, fieldKey) => {
  quickCreateType.value = type
  quickCreateFieldKey.value = fieldKey
  showQuickCreate.value = true
}

const closeQuickCreate = () => {
  showQuickCreate.value = false
  quickCreateType.value = null
  quickCreateFieldKey.value = null
}

const handleQuickCreateSuccess = async (newItem) => {
  // Refresh the dropdown options
  const field = formFields.value.find(f => f.key === quickCreateFieldKey.value)
  if (field) {
    await fetchDropdownOptions(field.fetchEndpoint, field.key)

    // Auto-select the newly created item
    if (field.createType === 'domain') {
      formData[field.key] = newItem.domain_code
    } else if (field.createType === 'problem_type') {
      formData[field.key] = newItem.type_name
    }
  }

  closeQuickCreate()
}

const validateForm = () => {
  const errors = []

  formFields.value.forEach(field => {
    if (field.required && !formData[field.key]) {
      errors.push(`${field.label} is required`)
    }

    if (field.type === 'json' && jsonErrors[field.key]) {
      errors.push(`${field.label}: ${jsonErrors[field.key]}`)
    }

    // Add format validation for ID fields
    // ID format validation removed for category_id and sub_category_id
    // Users can use any format they prefer

    if (field.key === 'question_id' && formData[field.key]) {
      // Loose format; rely on duplicate check to enforce uniqueness
    }

    if (field.key === 'suggestion_id' && formData[field.key]) {
      if (!/^S_[A-Z]{2,4}_\d{3,4}$/.test(formData[field.key])) {
        errors.push(`${field.label} must be in format: S_DOMAIN_### (e.g., S_STR_001, S_ANX_001)`)
      }
    }

    if (field.key === 'prompt_id' && formData[field.key]) {
      if (!/^P_[A-Z]{2,4}_\d{3,4}$/.test(formData[field.key])) {
        errors.push(`${field.label} must be in format: P_DOMAIN_### (e.g., P_STR_001, P_ANX_001)`)
      }
    }

    if (field.key === 'action_id' && formData[field.key]) {
      if (!/^A_\d{3,4}$/.test(formData[field.key])) {
        errors.push(`${field.label} must be in format: A_### or A_#### (e.g., A_001, A_0001)`)
      }
    }

    if (field.key === 'example_id' && formData[field.key]) {
      if (!/^E_\d{3,4}$/.test(formData[field.key])) {
        errors.push(`${field.label} must be in format: E_### or E_#### (e.g., E_001, E_0001)`)
      }
    }

    // Type-specific validation for assessments
    if (props.dataType === 'assessments') {
      if (field.key === 'response_type') {
        if (formData.response_type === 'scale') {
          if (formData.scale_min !== 1 || formData.scale_max !== 4) {
            errors.push('Scale questions must use 1-4 range')
          }
          // Validate scale labels
          const requiredLabels = ['scale_label_1', 'scale_label_2', 'scale_label_3', 'scale_label_4']
          for (const labelKey of requiredLabels) {
            if (!formData[labelKey] || formData[labelKey].trim() === '') {
              errors.push(`${labelKey.replace('_', ' ')} is required for scale questions`)
            }
          }
        }
        if (formData.response_type === 'multiple_choice') {
          const opts = formData.options || []
          if (!Array.isArray(opts) || opts.length < 2) {
            errors.push('Provide at least two options for Multiple Choice')
          } else {
            const normalized = opts.map(o => String(o).trim()).filter(o => o)
            const unique = new Set(normalized)
            if (unique.size < 2) {
              errors.push('Multiple Choice options must be distinct')
            }
          }
        }
      }
    }

    // Removed strict domain code format validation - now more flexible

    // Check validation requirements for domain_code and type_name
    if (field.key === 'domain_code' && props.dataType === 'domain_types') {
      if (!validationStatus.domain_code.checked) {
        errors.push('Please check for duplicate domain code before saving')
      } else if (validationStatus.domain_code.exists) {
        errors.push('Domain code already exists. Please choose a different one.')
      }
    }

    if (field.key === 'type_name' && props.dataType === 'problem_types') {
      if (!validationStatus.type_name.checked) {
        errors.push('Please check for duplicate type name before saving')
      } else if (validationStatus.type_name.exists) {
        errors.push('Type name already exists. Please choose a different one.')
      }
    }

    if (field.key === 'question_id' && props.dataType === 'assessments') {
      if (!validationStatus.question_id.checked) {
        errors.push('Please check for duplicate question ID before saving')
      } else if (validationStatus.question_id.exists) {
        errors.push('Question ID already exists. Please choose a different one.')
      }
    }

    if (field.key === 'category_id' && props.dataType === 'problem_types') {
      if (!validationStatus.category_id.checked) {
        errors.push('Please check for duplicate category ID before saving')
      } else if (validationStatus.category_id.exists) {
        errors.push('Category ID already exists. Please choose a different one.')
      }
    }

    if (field.key === 'sub_category_id' && props.dataType === 'problems' && !isEditing) {
      if (!validationStatus.sub_category_id.checked) {
        errors.push('Please check for duplicate subcategory ID before saving')
      } else if (validationStatus.sub_category_id.exists) {
        errors.push('Subcategory ID already exists. Please choose a different one.')
      }
    }
  })

  validationErrors.value = errors
  return errors.length === 0
}

const saveItem = async () => {
  if (!validateForm()) {
    return
  }

  isSaving.value = true

  try {
    // Process JSON fields
    formFields.value.forEach(field => {
      if (field.type === 'json' && jsonFields[field.key]) {
        validateJson(field.key)
      }
    })

    // For assessments: boolean defaults
    if (props.dataType === 'assessments' && formData.response_type === 'boolean') {
      if (!Array.isArray(formData.options) || formData.options.length === 0) {
        formData.options = ['Yes', 'No']
      }
    }

    // For assessments: scale processing
    if (props.dataType === 'assessments' && formData.response_type === 'scale') {
      // Set fixed scale values
      formData.scale_min = 1
      formData.scale_max = 4

      // Construct scale_labels object from individual fields
      formData.scale_labels = {
        "1": formData.scale_label_1 || 'Not at all',
        "2": formData.scale_label_2 || 'A little',
        "3": formData.scale_label_3 || 'Quite a bit',
        "4": formData.scale_label_4 || 'Very much'
      }

      // Remove individual label fields from submission
      delete formData.scale_label_1
      delete formData.scale_label_2
      delete formData.scale_label_3
      delete formData.scale_label_4
    } else if (props.dataType === 'assessments') {
      // For non-scale questions, remove scale fields
      delete formData.scale_min
      delete formData.scale_max
      delete formData.scale_labels
      delete formData.scale_label_1
      delete formData.scale_label_2
      delete formData.scale_label_3
      delete formData.scale_label_4
    }

    // Emit save event
    emit('save', { ...formData })

    // Close modal after successful save
    setTimeout(() => {
      closeModal()
    }, 500)

  } catch (error) {
    console.error('Save error:', error)
    validationErrors.value = ['An error occurred while saving. Please try again.']
  } finally {
    isSaving.value = false
  }
}

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

watch(() => props.item, () => {
  if (props.isOpen) {
    initializeForm()
  }
})

// Clear unrelated fields when response_type changes
watch(() => formData.response_type, () => {
  if (props.dataType !== 'assessments') return
  if (formData.response_type !== 'scale') {
    delete formData.scale_min
    delete formData.scale_max
  }
  if (formData.response_type !== 'multiple_choice') {
    formData.options = []
  }
})

// Watch for changes in domain_code and type_name to reset validation
watch(() => formData.domain_code, () => {
  if (props.dataType === 'domain_types') {
    validationStatus.domain_code.checked = false
    validationStatus.domain_code.exists = false
  }
})

watch(() => formData.type_name, () => {
  if (props.dataType === 'problem_types') {
    validationStatus.type_name.checked = false
    validationStatus.type_name.exists = false
  }
})

watch(() => formData.question_id, () => {
  if (props.dataType === 'assessments') {
    validationStatus.question_id.checked = false
    validationStatus.question_id.exists = false
  }
})

watch(() => formData.category_id, () => {
  if (props.dataType === 'problem_types') {
    validationStatus.category_id.checked = false
    validationStatus.category_id.exists = false
  }
})

watch(() => formData.sub_category_id, () => {
  if (props.dataType === 'problems') {
    validationStatus.sub_category_id.checked = false
    validationStatus.sub_category_id.exists = false
  }
})

// Helper function to get default scale labels
const getDefaultScaleLabel = (fieldKey) => {
  const defaults = {
    'scale_label_1': 'Not at all',
    'scale_label_2': 'A little',
    'scale_label_3': 'Quite a bit',
    'scale_label_4': 'Very much'
  }
  return defaults[fieldKey] || ''
}
</script>
