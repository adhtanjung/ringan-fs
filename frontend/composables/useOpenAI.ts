import { ref } from 'vue'
import { marked } from 'marked'

export const useOpenAI = () => {
  const config = useRuntimeConfig()
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  // Configure marked options
  marked.setOptions({
    breaks: true, // Convert line breaks to <br>
    gfm: true // GitHub Flavored Markdown
  })

  const convertMarkdownToHtml = (text: string) => {
    return marked(text)
  }

  // System message for Ringan AI
  const systemMessage = {
    role: 'system',
    content: `Kamu adalah Ringan AI, asisten kesehatan mental yang ramah dan empatik. Kamu selalu merespons dengan bahasa yang santai dan mudah dipahami, bertata kata seperi halnya seorang psikolog. Kamu fokus pada menganalisa permasalahan pengguna dan memberika saran saran yang membantu untuk kesehatan mental.

    Gunakan format markdown untuk merapikan responsmu:
    - Gunakan **bold** untuk penekanan
    - Gunakan *italic* untuk kata-kata penting
    - Gunakan list dengan bullet points (-) atau nomor (1. 2. 3.)
    - Gunakan > untuk kutipan
    - Gunakan \`\`\` untuk kode atau contoh
    - Gunakan --- untuk pemisah
    - Gunakan emoji yang sesuai dengan konteks`
  }

  // Custom API endpoint function
  const generateResponseCustom = async (messages: { role: string; content: string }[]) => {
    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token') || config.public.customChatApiKey
      
      const response = await fetch(config.public.customChatApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          messages: [systemMessage, ...messages],
          stream: false
        })
      })

      if (!response.ok) {
        throw new Error(`Custom API error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Adapt response format based on your API structure
      const content = data.message || data.response || data.content || data.choices?.[0]?.message?.content
      
      if (!content) {
        throw new Error('No content in custom API response')
      }
      
      return convertMarkdownToHtml(content)
    } catch (err) {
      console.error('Custom API Error:', err)
      throw err
    }
  }

  // Original OpenAI function as fallback
  const generateResponseOpenAI = async (messages: { role: string; content: string }[]) => {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.public.openaiApiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4.1-nano-2025-04-14',
          messages: [systemMessage,
            ...messages
          ],
          temperature: config.public.openaiTemperature,
          max_tokens: config.public.openaiMaxTokens
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from OpenAI')
      }

      const data = await response.json()
      const content = data.choices[0].message.content
      return convertMarkdownToHtml(content)
    } catch (err) {
      console.error('OpenAI API Error:', err)
      throw err
    }
  }

  // Main generateResponse function - tries custom API first, falls back to OpenAI
  const generateResponse = async (messages: { role: string; content: string }[]) => {
    isProcessing.value = true
    error.value = null

    try {
      // Try custom API first
      try {
        const customResponse = await generateResponseCustom(messages)
        return customResponse
      } catch (customError) {
        console.warn('Custom API failed, falling back to OpenAI:', customError)
        
        // Fallback to OpenAI if custom API fails
        if (config.public.openaiApiKey && config.public.openaiApiKey !== '') {
          const openaiResponse = await generateResponseOpenAI(messages)
          return openaiResponse
        } else {
          throw new Error('Both custom API and OpenAI are unavailable')
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      return null
    } finally {
      isProcessing.value = false
    }
  }

  return {
    generateResponse,
    generateResponseCustom,
    generateResponseOpenAI,
    isProcessing,
    error,
    convertMarkdownToHtml
  }
}