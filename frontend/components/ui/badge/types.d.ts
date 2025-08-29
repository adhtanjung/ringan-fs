declare module '@/components/ui/badge' {
  import type { DefineComponent } from 'vue'
  const Badge: DefineComponent<{
    variant?: 'default' | 'secondary' | 'destructive' | 'outline'
  }>
  export { Badge }
} 