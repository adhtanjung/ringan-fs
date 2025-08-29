import { ref } from 'vue'

export const useElevenLabs = () => {
  const config = useRuntimeConfig()
  const isGenerating = ref(false)
  const error = ref<string | null>(null)
  const audioUrl = ref<string | null>(null)

  const generateSpeech = async (text: string) => {
    isGenerating.value = true
    error.value = null
    audioUrl.value = null

    try {
      const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${config.public.elevenlabsVoiceId}`, {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': config.public.elevenlabsApiKey as string
        },
        body: JSON.stringify({
          text: text,
          model_id: config.public.elevenlabsModel,
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.5
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate speech')
      }

      const audioBlob = await response.blob()
      const url = URL.createObjectURL(audioBlob)
      audioUrl.value = url

      return url
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      return null
    } finally {
      isGenerating.value = false
    }
  }

  const playAudio = async (url: string) => {
    return new Promise<void>((resolve, reject) => {
      const audio = new Audio(url)
      audio.onended = () => resolve()
      audio.onerror = () => reject(new Error('Failed to play audio'))
      audio.play().catch(reject)
    })
  }

  const cleanup = () => {
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = null
    }
  }

  return {
    generateSpeech,
    playAudio,
    cleanup,
    isGenerating,
    error,
    audioUrl
  }
} 