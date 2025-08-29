import { ref, watch } from 'vue'

export const useVoiceConversation = () => {
  const { generateResponse } = useOpenAI()
  const { generateSpeech, playAudio, cleanup: cleanupTTS, isGenerating: isTTSGenerating } = useElevenLabs()
  const { 
    isSupported: isSpeechSupported, 
    isListening, 
    transcript, 
    error: speechError, 
    startListening, 
    stopListening 
  } = useSpeechRecognition()

  const isVoiceConversationActive = ref(false)
  const isProcessingVoice = ref(false)
  const voiceMessages = ref<Array<{ text: string; sender: string; time: string; audioUrl?: string }>>([])
  const currentAudioUrl = ref<string | null>(null)
  
  // New fluid mode features
  const isFluidMode = ref(false)
  const isMuted = ref(false)
  const isTestScriptMode = ref(false)
  const testScriptMessages = ref<Array<{ text: string; sender: string; time: string }>>([])
  const conversationCount = ref(0)
  const maxFluidConversations = ref(5) // Limit for demo
  
  // Test script questions for after conversation
  const testQuestions = ref([
    "Bagaimana perasaanmu setelah berbicara dengan AI?",
    "Apakah AI membantu kamu merasa lebih baik?", 
    "Apa yang paling kamu suka dari percakapan ini?",
    "Seberapa mudah berkomunikasi dengan AI ini?",
    "Apakah ada yang ingin kamu sampaikan untuk perbaikan?"
  ])
  const currentQuestionIndex = ref(0)

  // Function to strip HTML tags from AI response for TTS
  const stripHtmlTags = (html: string) => {
    return html.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
  }

  // Watch for transcript changes to process voice input
  watch(transcript, async (newTranscript) => {
    if (newTranscript && isVoiceConversationActive.value) {
      if (isTestScriptMode.value) {
        await processTestScriptInput(newTranscript)
      } else {
        await processVoiceInput(newTranscript)
      }
    }
  })

  const startVoiceConversation = () => {
    isVoiceConversationActive.value = true
    voiceMessages.value = []
    conversationCount.value = 0
    isTestScriptMode.value = false
    currentQuestionIndex.value = 0
    testScriptMessages.value = []
    
    // Add welcome message
    const welcomeMessage = isFluidMode.value 
      ? 'Halo! Mode percakapan fluid aktif. Kamu bisa langsung bicara dan aku akan otomatis merespons. Mulai bicara saja!'
      : 'Halo! Sekarang kita bisa berbicara langsung. Tekan tombol mikrofon dan mulai bicara denganku!'
    
    addVoiceMessage(welcomeMessage, 'ai')
    if (!isMuted.value) {
      speakMessage(welcomeMessage)
    }
    
    // If fluid mode, automatically start listening after welcome message
    if (isFluidMode.value && !isMuted.value) {
      setTimeout(() => {
        if (!isMuted.value) {
          startVoiceInput()
        }
      }, 3000) // Give time for welcome message to finish
    }
  }

  const stopVoiceConversation = () => {
    isVoiceConversationActive.value = false
    isTestScriptMode.value = false
    stopListening()
    cleanupTTS()
    if (currentAudioUrl.value) {
      URL.revokeObjectURL(currentAudioUrl.value)
      currentAudioUrl.value = null
    }
  }

  const toggleFluidMode = () => {
    isFluidMode.value = !isFluidMode.value
    if (isVoiceConversationActive.value) {
      // Restart conversation with new mode
      startVoiceConversation()
    }
  }

  const toggleMute = () => {
    const wasMuted = isMuted.value
    isMuted.value = !isMuted.value
    
    if (isMuted.value) {
      // When muting: stop audio and speech recognition
      cleanupTTS()
      if (isListening.value) {
        stopListening()
      }
    } else {
      // When unmuting: restart listening if in fluid mode and conversation is active
      if (isFluidMode.value && isVoiceConversationActive.value && !isProcessingVoice.value) {
        setTimeout(() => {
          if (!isListening.value && !isProcessingVoice.value) {
            startVoiceInput()
          }
        }, 500) // Small delay to ensure proper restart
      }
    }
  }

  const addVoiceMessage = (text: string, sender: string, audioUrl?: string) => {
    voiceMessages.value.push({
      text,
      sender,
      time: getCurrentTime(),
      audioUrl
    })
  }

  const addTestScriptMessage = (text: string, sender: string) => {
    testScriptMessages.value.push({
      text,
      sender,
      time: getCurrentTime()
    })
  }

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('id-ID', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const processVoiceInput = async (userInput: string) => {
    if (!userInput.trim() || isProcessingVoice.value) return

    isProcessingVoice.value = true
    conversationCount.value++
    
    // Add user message
    addVoiceMessage(userInput, 'user')

    try {
      // Check if we've reached the conversation limit for fluid mode
      if (isFluidMode.value && conversationCount.value >= maxFluidConversations.value) {
        const endMessage = 'Terima kasih sudah mengobrol denganku! Sekarang aku akan mengajukan beberapa pertanyaan untuk evaluasi. Siap?'
        addVoiceMessage(endMessage, 'ai')
        if (!isMuted.value) {
          await speakMessage(endMessage)
        }
        
        // Start test script mode
        setTimeout(() => {
          startTestScript()
        }, 2000)
        return
      }

      // Prepare message history for AI
      const messageHistory = voiceMessages.value.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }))

      // Get AI response
      const aiResponse = await generateResponse(messageHistory)
      
      if (aiResponse) {
        const cleanText = stripHtmlTags(aiResponse)
        addVoiceMessage(cleanText, 'ai')
        if (!isMuted.value) {
          await speakMessage(cleanText)
        }
        
        // In fluid mode, automatically start listening again after AI response
        if (isFluidMode.value && !isMuted.value) {
          setTimeout(() => {
            if (!isProcessingVoice.value && !isListening.value && !isMuted.value) {
              startVoiceInput()
            }
          }, 1000)
        }
      }
    } catch (error) {
      const errorMessage = 'Maaf, terjadi kesalahan. Silakan coba lagi.'
      addVoiceMessage(errorMessage, 'ai')
      if (!isMuted.value) {
        await speakMessage(errorMessage)
      }
    } finally {
      isProcessingVoice.value = false
    }
  }

  const startTestScript = async () => {
    isTestScriptMode.value = true
    testScriptMessages.value = []
    currentQuestionIndex.value = 0
    
    const introMessage = 'Bagus! Sekarang aku akan mengajukan beberapa pertanyaan evaluasi. Jawab saja dengan jujur ya!'
    addTestScriptMessage(introMessage, 'ai')
    if (!isMuted.value) {
      await speakMessage(introMessage)
    }
    
    setTimeout(() => {
      askNextQuestion()
    }, 2000)
  }

  const askNextQuestion = async () => {
    if (currentQuestionIndex.value < testQuestions.value.length) {
      const question = testQuestions.value[currentQuestionIndex.value]
      addTestScriptMessage(question, 'ai')
      if (!isMuted.value) {
        await speakMessage(question)
      }
      
      // Auto start listening for answer
      setTimeout(() => {
        if (!isListening.value && !isMuted.value) {
          startVoiceInput()
        }
      }, 1000)
    } else {
      // All questions completed
      const completionMessage = 'Terima kasih sudah menjawab semua pertanyaan! Feedback kamu sangat berharga untuk kami. Semoga hari-harimu menyenangkan! 💙'
      addTestScriptMessage(completionMessage, 'ai')
      if (!isMuted.value) {
        await speakMessage(completionMessage)
      }
      
      // End test script mode
      setTimeout(() => {
        isTestScriptMode.value = false
      }, 3000)
    }
  }

  const processTestScriptInput = async (userInput: string) => {
    if (!userInput.trim() || isProcessingVoice.value) return

    isProcessingVoice.value = true
    
    // Add user answer
    addTestScriptMessage(userInput, 'user')
    
    // Move to next question
    currentQuestionIndex.value++
    
    try {
      // Simple acknowledgment before next question
      const acknowledgments = [
        'Terima kasih atas jawabannya!',
        'Baik, saya catat.',
        'Okay, mengerti.',
        'Bagus sekali!',
        'Terima kasih!'
      ]
      
      const ack = acknowledgments[Math.floor(Math.random() * acknowledgments.length)]
      addTestScriptMessage(ack, 'ai')
      if (!isMuted.value) {
        await speakMessage(ack)
      }
      
      // Ask next question
      setTimeout(() => {
        askNextQuestion()
      }, 1500)
      
    } catch (error) {
      console.error('Error in test script:', error)
    } finally {
      isProcessingVoice.value = false
    }
  }

  const speakMessage = async (text: string) => {
    if (isMuted.value) return
    
    try {
      const audioUrl = await generateSpeech(text)
      if (audioUrl) {
        currentAudioUrl.value = audioUrl
        await playAudio(audioUrl)
      }
    } catch (error) {
      console.error('Failed to speak message:', error)
    }
  }

  const startVoiceInput = async (manual = false) => {
    if (!isSpeechSupported.value) {
      alert('Speech recognition tidak didukung di browser ini.')
      return
    }

    if (!isVoiceConversationActive.value && !isTestScriptMode.value) {
      alert('Silakan mulai percakapan suara terlebih dahulu.')
      return
    }

    // Don't start listening if muted, unless it's a manual button click
    if (isMuted.value && !manual) {
      return
    }

    await startListening()
  }

  return {
    // State
    isVoiceConversationActive,
    isProcessingVoice,
    voiceMessages,
    isSpeechSupported,
    isListening,
    isTTSGenerating,
    speechError,
    
    // New fluid mode states
    isFluidMode,
    isMuted,
    isTestScriptMode,
    testScriptMessages,
    conversationCount,
    maxFluidConversations,
    currentQuestionIndex,
    testQuestions,
    
    // Methods
    startVoiceConversation,
    stopVoiceConversation,
    startVoiceInput,
    stopListening,
    toggleFluidMode,
    toggleMute,
    startTestScript
  }
} 