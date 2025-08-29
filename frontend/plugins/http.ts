import { initHttpInterceptor } from '~/utils/http'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  
  // Initialize HTTP interceptor
  initHttpInterceptor({
    enableLogging: config.public.appEnvironment !== 'production',
    enableToast: true
  })
}) 