<template>
  <NuxtLayout name="admin">
    <div class="min-h-screen bg-gray-50">
      <!-- Main Container -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2 sm:py-3 lg:py-4">
        <!-- Header -->
        <div class="bg-white sticky top-0 z-10 shadow-sm border-b border-gray-200">
          <div class="px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex items-center justify-between">
              <h1 class="text-xl font-semibold text-gray-900">{{ dataTypeLabel }}</h1>
              <div class="flex items-center gap-2 flex-wrap gap-x-2 gap-y-2">
                <Button
                  @click="refreshData"
                  :disabled="loading"
                  variant="outline"
                  size="icon"
                  title="Refresh"
                >
                  <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </Button>
                <Button
                  @click="openImportModal"
                  variant="outline"
                  size="sm"
                >
                  Import
                </Button>
                <Button
                  @click="openExportModal"
                  variant="outline"
                  size="sm"
                >
                  Export
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Dataset Table Container -->
        <div class="mt-6">
          <DatasetTable
            :title="dataTypeLabel"
            :data="data"
            :columns="columns"
            :loading="loading"
            :error="error"
            :pagination="pagination"
            :current-page="currentPage"
            :total-pages="totalPages"
            @create="openCreateModal"
            @edit="openEditModal"
            @delete="deleteItem"
            @bulk-delete="bulkDeleteItems"
            @refresh="refreshData"
            @page-change="goToPage"
            @page-size-change="changePageSize"
            @next-page="nextPage"
            @prev-page="prevPage"
          />
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <ImportModal
      :is-open="showImportModal"
      :data-type="'feedback_prompts'"
      @close="closeImportModal"
      @import-success="handleImportSuccess"
    />

    <!-- Export Modal -->
    <ExportModal
      :is-open="showExportModal"
      :data-type="'feedback_prompts'"
      @close="closeExportModal"
    />

    <!-- Edit Modal -->
    <DatasetEditModalShadcn
      :is-open="showEditModal"
      :data-type="'feedback_prompts'"
      :item="editingItem"
      :loading="actionLoading"
      @close="closeEditModal"
      @save="handleSave"
    />

    <!-- Toast Notifications -->
    <Toaster />
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue'

// Define page meta
definePageMeta({
  layout: false
  // TEMPORARILY DISABLED: Admin authentication middleware
  // middleware: 'auth-admin'  // Uncomment to restore authentication
})

// Components
import DatasetTable from '~/components/admin/DatasetTable.vue'
import ImportModal from '~/components/admin/ImportModal.vue'
import ExportModal from '~/components/admin/ExportModal.vue'
import DatasetEditModalShadcn from '~/components/admin/DatasetEditModalShadcn.vue'

// shadcn-vue components
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast/use-toast'
import { Toaster } from '@/components/ui/toast'

// Use the shared composable
const {
  loading,
  error,
  data,
  actionLoading,
  showImportModal,
  showExportModal,
  showEditModal,
  editingItem,
  pagination,
  columns,
  dataTypeLabel,
  currentPage,
  totalPages,
  refreshData,
  openCreateModal,
  openEditModal,
  closeEditModal,
  handleSave,
  deleteItem,
  bulkDeleteItems,
  openImportModal,
  closeImportModal,
  openExportModal,
  closeExportModal,
  handleImportSuccess,
  goToPage,
  changePageSize,
  nextPage,
  prevPage
} = useDatasetManagement('feedback_prompts')

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>
