import { ref, computed } from "vue";
import { marked } from "marked";

export const useOllamaChat = () => {
	let config;
	try {
		config = useRuntimeConfig();
	} catch (error) {
		// Fallback for SSR
		config = {
			public: {
				customChatApiUrl: '',
				customChatApiKey: ''
			}
		};
	}
	const isProcessing = ref(false);
	const error = ref<string | null>(null);
	const isConnected = ref(false);
	const isStreaming = ref(false);

	// Chat state
	const messages = ref<
		Array<{
			id: string;
			text: string;
			sender: "user" | "ai";
			timestamp: string | Date;
			sentiment?: any;
			isCrisis?: boolean;
			problemCategory?: string;
			suggestions?: any[];
			assessmentQuestions?: any[];
			contextAnalysis?: any;
			assessmentRecommendations?: any;
			showAssessmentTransition?: boolean;
			isStreaming?: boolean;
			detectedEmotion?: any;
			emotionTone?: any;
			assessmentProgress?: {
				current: number;
				total: number;
			};
			// Assessment suggestion fields
			isAssessmentSuggestion?: boolean;
			suggestedCategory?: string;
			subCategoryId?: string;
		}>
	>([]);

	// Session state
	const sessionId = ref("");
	const conversationId = ref("");
	const currentProblemCategory = ref("");
	const detectedProblemCategory = ref("");
	const shouldShowAssessmentSuggestion = ref(false);
	const assessmentProgress = ref({
		isActive: false,
		currentQuestion: null,
		completedQuestions: [],
		totalQuestions: 0,
		currentStep: 1,
		sessionId: "",
		responses: {},
	});

	// Configure marked options
	marked.setOptions({
		breaks: true,
		gfm: true,
	});

	const convertMarkdownToHtml = (text: string) => {
		return marked(text);
	};

	// Generate session ID
	const generateSessionId = () => {
		return (
			"session_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9)
		);
	};

	// Initialize session
	const initializeSession = () => {
		if (!sessionId.value) {
			sessionId.value = generateSessionId();
		}
		if (!conversationId.value) {
			conversationId.value = generateSessionId();
		}
	};

	// Semantic search for mental health context
	const searchMentalHealthContext = async (query: string) => {
		try {
			const response = await fetch(`${config.public.vectorApiUrl}/search`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify({
					query: query,
					collection: "mental-health-problems",
					limit: 3,
					score_threshold: 0.3
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data.results || [];
		} catch (err) {
			console.error('❌ Semantic search error:', err);
			return [];
		}
	};

	// Send message with streaming response via HTTP SSE
	const sendMessageStream = async (
		message: string,
		sessionData?: any,
		onChunk?: (chunk: string) => void,
		onComplete?: (fullResponse: any) => void,
		onNewMessage?: (messageData: any) => void
	) => {
		if (!process.client) {
			console.warn('sendMessageStream called during SSR, skipping');
			return;
		}

		console.log('🔄 sendMessageStream called with:', {
			message,
			sessionData,
			isStreaming: isStreaming.value,
			hasOnChunk: typeof onChunk === 'function',
			hasOnComplete: typeof onComplete === 'function'
		});

		if (!message.trim() || isStreaming.value) {
			console.log('⚠️ sendMessageStream blocked:', {
				emptyMessage: !message.trim(),
				isStreaming: isStreaming.value
			});
			return;
		}

		initializeSession();
		isStreaming.value = true;
		error.value = null;

		try {
			// First, perform semantic search to understand the context
			const searchResults = await searchMentalHealthContext(message);

			// Prepare enhanced message with context
			const enhancedMessage = {
				message: message.trim(),
				session_data: sessionData || {},
				semantic_context: searchResults,
				problem_category: currentProblemCategory.value,
				assessment_progress: assessmentProgress.value,
			};

			let fullResponse = "";
			let responseData: any = {};

			// Use HTTP streaming endpoint instead of WebSocket
			const response = await fetch(`${config.public.customChatApiUrl}/chat/stream`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify(enhancedMessage),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const reader = response.body?.getReader();
			if (!reader) {
				throw new Error('No response body reader available');
			}

			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.trim() === '') continue;

					if (line.startsWith('data: ')) {
						const dataStr = line.slice(6);
						if (dataStr.trim() === '') continue;

						try {
							const data = JSON.parse(dataStr);
							console.log('📋 Parsed SSE data:', data);

							if (data.type === "chunk") {
								console.log('📦 Processing chunk:', { content: data.content, length: data.content?.length });
								fullResponse += data.content;

								// Store assessment suggestion flag for later use
								if (data.is_assessment_suggestion) {
									responseData.is_assessment_suggestion = true;
									responseData.suggested_category = data.suggested_category;
									responseData.sub_category_id = data.sub_category_id;
								}

								if (typeof onChunk === 'function') {
									console.log('📤 Calling onChunk callback with:', data.content);
									onChunk(data.content);
								} else {
									console.warn('⚠️ onChunk callback not provided or not a function');
								}
							} else if (data.type === "complete") {
								console.log('✅ Processing complete message:', { fullResponseLength: fullResponse.length, dataContentLength: data.content?.length });
								// Use data.content if fullResponse is empty (direct complete message)
								const messageContent = fullResponse || data.content || "";
								const htmlContent = convertMarkdownToHtml(messageContent);

								const result = {
									message: htmlContent,
									sentiment: data.sentiment || responseData.sentiment,
									isCrisis: data.is_crisis || responseData.is_crisis,
									timestamp: new Date(),
									conversationId: conversationId.value,
									problemCategory: data.problem_category || responseData.problem_category,
									suggestions: data.suggestions || responseData.suggestions,
									assessmentQuestions: data.assessment_questions || responseData.assessment_questions,
									showAssessmentTransition: data.show_assessment_transition || responseData.show_assessment_transition,
									contextAnalysis: data.context_analysis || responseData.context_analysis,
									semanticContext: searchResults,
									isAssessmentSuggestion: data.is_assessment_suggestion || responseData.is_assessment_suggestion,
									suggestedCategory: data.suggested_category || responseData.suggested_category,
									subCategoryId: data.sub_category_id || responseData.sub_category_id,
								};

								if (typeof onComplete === 'function') {
									console.log('📤 Calling onComplete callback with result');
									onComplete(result);
								} else {
									console.warn('⚠️ onComplete callback not provided or not a function');
								}

								// Reset streaming state
								isStreaming.value = false;
							}
						} catch (parseError) {
							console.error('❌ Error parsing SSE data:', parseError);
							console.error('Raw SSE data:', dataStr);
						}
					}
				}
			}

		} catch (err) {
			console.error('❌ sendMessageStream error:', err);
			error.value = err instanceof Error ? err.message : "An error occurred";
		} finally {
			console.log('🏁 sendMessageStream completed, setting isStreaming to false');
			isStreaming.value = false;
		}
	};

	// Add message to the messages array
	const addMessage = (message: any) => {
		messages.value.push(message);
	};

	// Clear all messages
	const clearMessages = () => {
		messages.value = [];
	};

	// Check if there are messages
	const hasMessages = computed(() => messages.value.length > 0);

	// Dummy functions to satisfy the interface
	const sendMessage = async (message: string, sessionData?: any) => {
		// This is a placeholder - the actual implementation would be more complex
		console.log('sendMessage called (placeholder)');
		return null;
	};

	const getTherapeuticSuggestions = async (problemCategory: string) => {
		// This is a placeholder - the actual implementation would be more complex
		console.log('getTherapeuticSuggestions called (placeholder)');
		return [];
	};

	// Assessment workflow methods
	const startAssessment = async (problemCategory: string, subCategoryId?: string) => {
		if (!process.client) {
			console.warn('startAssessment called during SSR, skipping');
			return { type: 'error', message: 'Assessment not available during SSR' };
		}

		try {
			const requestPayload = {
				problem_category: problemCategory,
				session_data: {
					sub_category_id: subCategoryId,
					session_id: sessionId.value,
				}
			};

			console.log('📤 Starting assessment:', {
				url: `${config.public.customChatApiUrl}/assessment/start`,
				payload: requestPayload
			});

			const response = await fetch(`${config.public.customChatApiUrl}/assessment/start`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify(requestPayload),
			});

			console.log('📥 Assessment start response status:', response.status);

			if (!response.ok) {
				const errorText = await response.text();
				console.error('❌ Assessment start error:', {
					status: response.status,
					statusText: response.statusText,
					error: errorText
				});
				throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
			}

			const result = await response.json();
			console.log('✅ Assessment start result:', result);

			// Update assessment progress
			if (result.type === 'assessment_question') {
				const assessmentSessionId = result.session_id || sessionId.value;
				console.log('🔍 Assessment start - result.session_id:', result.session_id);
				console.log('🔍 Assessment start - sessionId.value:', sessionId.value);
				console.log('🔍 Assessment start - using assessmentSessionId:', assessmentSessionId);

				assessmentProgress.value = {
					isActive: true,
					currentQuestion: result.question,
					completedQuestions: [],
					totalQuestions: result.total_questions || 10,
					currentStep: 1,
					sessionId: assessmentSessionId,
					responses: {},
				};
			}

			return result;
		} catch (err) {
			console.error('❌ Error starting assessment:', err);
			error.value = err instanceof Error ? err.message : "Failed to start assessment";
			return { type: 'error', message: error.value };
		}
	};

	const submitAssessmentAnswer = async (questionId: string, answer: any) => {
		if (!process.client) {
			console.warn('submitAssessmentAnswer called during SSR, skipping');
			return { type: 'error', message: 'Assessment not available during SSR' };
		}

		try {
			// Validate inputs
			if (!questionId || questionId.trim() === '') {
				throw new Error('Question ID is required');
			}
			if (answer === null || answer === undefined || answer === '') {
				throw new Error('Answer is required');
			}

			const requestPayload = {
				question_id: questionId,
				response: answer,
				session_id: assessmentProgress.value.sessionId,
			};

			console.log('🔍 Submit answer - assessmentProgress.value.sessionId:', assessmentProgress.value.sessionId);
			console.log('🔍 Submit answer - sessionId.value:', sessionId.value);

			console.log('📤 Submitting assessment answer:', {
				url: `${config.public.customChatApiUrl}/assessment/respond`,
				payload: requestPayload,
				questionId: questionId,
				answer: answer,
				answerType: typeof answer,
				sessionId: assessmentProgress.value.sessionId
			});

			const response = await fetch(`${config.public.customChatApiUrl}/assessment/respond`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify(requestPayload),
			});

			console.log('📥 Assessment answer response status:', response.status);

			if (!response.ok) {
				const errorText = await response.text();
				console.error('❌ Assessment answer error:', {
					status: response.status,
					statusText: response.statusText,
					error: errorText
				});
				throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
			}

			const result = await response.json();
			console.log('✅ Assessment answer result:', result);

			// Update assessment progress
			if (result.type === 'assessment_question') {
				assessmentProgress.value.currentStep += 1;
				assessmentProgress.value.currentQuestion = result.question;
				(assessmentProgress.value.completedQuestions as any[]).push({
					questionId,
					answer,
					timestamp: new Date(),
				});
				(assessmentProgress.value.responses as any)[questionId] = answer;
			} else if (result.type === 'assessment_complete') {
				assessmentProgress.value.isActive = false;
				assessmentProgress.value.currentQuestion = null;
			}

			return result;
		} catch (err) {
			console.error('❌ Error submitting assessment answer:', err);
			error.value = err instanceof Error ? err.message : "Failed to submit answer";
			return { type: 'error', message: error.value };
		}
	};

	const getAssessmentStatus = async () => {
		if (!process.client) {
			console.warn('getAssessmentStatus called during SSR, skipping');
			return { type: 'error', message: 'Assessment not available during SSR' };
		}

		try {
			const response = await fetch(`${config.public.customChatApiUrl}/assessment/status/${sessionId.value}`, {
				method: 'GET',
				headers: {
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			return result;
		} catch (err) {
			console.error('❌ Error getting assessment status:', err);
			return { active: false };
		}
	};

	const cancelAssessment = async () => {
		if (!process.client) {
			console.warn('cancelAssessment called during SSR, skipping');
			return { type: 'error', message: 'Assessment not available during SSR' };
		}

		try {
			const response = await fetch(`${config.public.customChatApiUrl}/assessment/cancel`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify({
					session_id: assessmentProgress.value.sessionId,
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			// Reset assessment progress
			assessmentProgress.value = {
				isActive: false,
				currentQuestion: null,
				completedQuestions: [],
				totalQuestions: 0,
				currentStep: 1,
				sessionId: "",
				responses: {},
			};

			return await response.json();
		} catch (err) {
			console.error('❌ Error canceling assessment:', err);
			error.value = err instanceof Error ? err.message : "Failed to cancel assessment";
			return { type: 'error', message: error.value };
		}
	};

	// Enhanced message streaming with assessment integration
	const sendMessageWithAssessment = async (
		message: string,
		sessionData?: any,
		onChunk?: (chunk: string) => void,
		onComplete?: (fullResponse: any) => void,
		onAssessmentQuestion?: (question: any) => void
	) => {
		console.log('🔄 sendMessageWithAssessment called with:', {
			message,
			sessionData,
			assessmentActive: assessmentProgress.value.isActive
		});

		if (!message.trim() || isStreaming.value) {
			return;
		}

		initializeSession();
		isStreaming.value = true;
		error.value = null;

		try {
			// First, perform semantic search to understand the context
			const searchResults = await searchMentalHealthContext(message);

			// Prepare enhanced message with context and assessment data
			const enhancedMessage = {
				message: message.trim(),
				session_data: {
					...sessionData,
					assessment_progress: assessmentProgress.value,
					use_flow: true, // Enable conversation flow
				},
				semantic_context: searchResults,
				problem_category: currentProblemCategory.value,
			};

			let fullResponse = "";
			let responseData: any = {};

			// Use HTTP streaming endpoint
			const response = await fetch(`${config.public.customChatApiUrl}/chat/stream`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${config.public.customChatApiKey}`,
				},
				body: JSON.stringify(enhancedMessage),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const reader = response.body?.getReader();
			if (!reader) {
				throw new Error('No response body reader available');
			}

			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.trim() === '') continue;

					if (line.startsWith('data: ')) {
						const dataStr = line.slice(6);
						if (dataStr.trim() === '') continue;

						try {
							const data = JSON.parse(dataStr);
							console.log('📋 Parsed SSE data:', data);

							if (data.type === "chunk") {
								fullResponse += data.content;

								// Store assessment suggestion flag for later use
								if (data.is_assessment_suggestion) {
									responseData.is_assessment_suggestion = true;
									responseData.suggested_category = data.suggested_category;
									responseData.sub_category_id = data.sub_category_id;
								}

								if (typeof onChunk === 'function') {
									onChunk(data.content);
								}
							} else if (data.type === "assessment_question") {
								// Handle assessment question
								console.log('📝 Assessment question received:', data);
								if (typeof onAssessmentQuestion === 'function') {
									onAssessmentQuestion(data);
								}
							} else if (data.type === "complete") {
								const messageContent = fullResponse || data.content || "";
								const htmlContent = convertMarkdownToHtml(messageContent);

								const result = {
									message: htmlContent,
									sentiment: data.sentiment || responseData.sentiment,
									isCrisis: data.is_crisis || responseData.is_crisis,
									timestamp: new Date(),
									conversationId: conversationId.value,
									problemCategory: data.problem_category || responseData.problem_category,
									suggestions: data.suggestions || responseData.suggestions,
									assessmentQuestions: data.assessment_questions || responseData.assessment_questions,
									showAssessmentTransition: data.show_assessment_transition || responseData.show_assessment_transition,
									contextAnalysis: data.context_analysis || responseData.context_analysis,
									semanticContext: searchResults,
									assessmentProgress: data.assessment_progress || responseData.assessment_progress,
									// Assessment suggestion data
									isAssessmentSuggestion: data.is_assessment_suggestion || responseData.is_assessment_suggestion,
									suggestedCategory: data.suggested_category || responseData.suggested_category,
									subCategoryId: data.sub_category_id || responseData.sub_category_id,
								};

								if (typeof onComplete === 'function') {
									onComplete(result);
								}

								// Update assessment progress if provided
								if (data.assessment_progress) {
									assessmentProgress.value = {
										...assessmentProgress.value,
										...data.assessment_progress,
									};
								}

								isStreaming.value = false;
							}
						} catch (parseError) {
							console.error('❌ Error parsing SSE data:', parseError);
						}
					}
				}
			}

		} catch (err) {
			console.error('❌ sendMessageWithAssessment error:', err);
			error.value = err instanceof Error ? err.message : "An error occurred";
		} finally {
			isStreaming.value = false;
		}
	};

	// Return the composable interface
	return {
		// State
		messages,
		isProcessing,
		isStreaming,
		error,
		isConnected,
		sessionId,
		conversationId,
		currentProblemCategory,
		detectedProblemCategory,
		shouldShowAssessmentSuggestion,
		assessmentProgress,
		hasMessages,

		// Methods
		sendMessage,
		sendMessageStream,
		sendMessageWithAssessment,
		addMessage,
		clearMessages,
		searchMentalHealthContext,
		getTherapeuticSuggestions,

		// Assessment workflow methods
		startAssessment,
		submitAssessmentAnswer,
		getAssessmentStatus,
		cancelAssessment,
	};
};
