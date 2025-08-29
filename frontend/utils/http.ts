import { FetchError } from 'ofetch'
import type { FetchOptions } from 'ofetch'

// Configuration options for the HTTP interceptor
interface HttpInterceptorOptions {
  enableLogging: boolean
  enableToast: boolean
}

// Initialize the HTTP interceptor
export function initHttpInterceptor(options: Partial<HttpInterceptorOptions> = {}) {
  const config = useRuntimeConfig()
  const nuxtApp = useNuxtApp()
  
  // Default options - use runtime config for isDev
  const defaultOptions: HttpInterceptorOptions = {
    enableLogging: config.public.isDev || import.meta.dev, // Use both runtime config and compile-time flag
    enableToast: true
  }
  
  const mergedConfig = { ...defaultOptions, ...options }
  
  // Set up global error handler
  nuxtApp.hook('app:created', () => {
    const originalFetch = globalThis.$fetch
    
    // @ts-ignore - Override fetch but keep the original functionality
    globalThis.$fetch = async (request, options) => {
      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token')
      
      // Create default headers with auth token
      const headers = {
        ...(options?.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
      
      try {
        return await originalFetch(request, { ...options, headers })
      } catch (error) {
        if (error instanceof FetchError) {
          // Log error in development
          if (mergedConfig.enableLogging) {
            console.error('API Error:', {
              status: error.status,
              message: error.message,
              data: error.data
            })
          }
          
          // Show toast notifications
          if (mergedConfig.enableToast && import.meta.client) {
            try {
              // Direct import from components
              const { useToast } = await import('@/components/ui/toast/use-toast')
              const { toast } = useToast()
              
              const statusCode = error.status || 500
              let title = 'Error'
              let description = 'An error occurred'
              
              if (statusCode === 401) {
                title = 'Authentication Error'
                description = 'Your session has expired. Please login again.'
                // Force logout
                const authStore = useAuthStore()
                authStore.logout()
                navigateTo('/login')
              } else if (statusCode === 403) {
                title = 'Permission Denied'
                description = 'You do not have permission to perform this action'
              } else if (statusCode === 404) {
                title = 'Not Found'
                description = 'The requested resource was not found'
              } else if (statusCode >= 500) {
                title = 'Server Error'
                description = 'Server error. Please try again later'
              } else if (error.data?.message) {
                description = error.data.message
              }
              
              toast({
                variant: 'destructive',
                title,
                description
              })
            } catch (toastError) {
              console.error('Failed to show toast:', toastError)
            }
          }
        }
        throw error
      }
    }
  })
}

// Base API function with multiple method support
export const api = {
  // GET method
  async get<T>(url: string, params?: Record<string, any>, options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    return $fetch<T>(url, {
      method: 'get',
      baseURL,
      params,
      ...options
    })
  },
  
  // POST method with JSON body
  async post<T, D = any>(url: string, data?: D, options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    return $fetch<T>(url, {
      method: 'post',
      baseURL,
      body: data as any, // Cast to any to avoid type errors
      ...options
    })
  },
  
  // PUT method with JSON body
  async put<T, D = any>(url: string, data?: D, options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    return $fetch<T>(url, {
      method: 'put',
      baseURL,
      body: data as any, // Cast to any to avoid type errors
      ...options
    })
  },
  
  // PATCH method with JSON body
  async patch<T, D = any>(url: string, data?: D, options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    return $fetch<T>(url, {
      method: 'patch',
      baseURL,
      body: data as any, // Cast to any to avoid type errors
      ...options
    })
  },
  
  // DELETE method
  async delete<T>(url: string, options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    return $fetch<T>(url, {
      method: 'delete',
      baseURL,
      ...options
    })
  },
  
  // FormData submission
  async formData<T, D extends Record<string, any>>(url: string, data: D, method: 'POST' | 'PUT' | 'PATCH' = 'POST', options?: FetchOptions): Promise<T> {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBaseUrl
    
    // Convert data to FormData
    const formData = new FormData()
    Object.entries(data).forEach(([key, value]) => {
      // Handle File objects specially
      if (value instanceof File) {
        formData.append(key, value)
      } 
      // Handle arrays
      else if (Array.isArray(value)) {
        value.forEach((item, index) => {
          formData.append(`${key}[${index}]`, item)
        })
      } 
      // Handle null/undefined
      else if (value === null || value === undefined) {
        // Skip null/undefined values
      } 
      // Handle everything else
      else {
        formData.append(key, String(value))
      }
    })
    
    // Map method string to lowercase
    const methodMap = {
      'POST': 'post',
      'PUT': 'put',
      'PATCH': 'patch'
    } as const;
    
    return $fetch<T>(url, {
      method: methodMap[method],
      baseURL,
      body: formData,
      ...options
    })
  }
} 