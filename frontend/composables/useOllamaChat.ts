import { ref, computed } from "vue";
import { marked } from "marked";

export const useOllamaChat = () => {
	const config = useRuntimeConfig();
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
			const response = await fetch(
				`${config.public.customChatApiUrl.replace("/chat", "/vector/search")}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						query: query,
						limit: 5,
						collection: "mental-health-problems",
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data.results || [];
		} catch (err) {
			console.error("Semantic Search Error:", err);
			return [];
		}
	};

	// Get problem categories
	const getProblemCategories = async () => {
		try {
			const response = await fetch(
				`${config.public.customChatApiUrl.replace("/chat", "/vector/search")}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						query: "mental health problems categories",
						limit: 10,
						collection: "mental-health-problems",
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data.results || [];
		} catch (err) {
			console.error("Problem Categories Error:", err);
			return [];
		}
	};

	// Get assessment questions for a problem category
	const getAssessmentQuestions = async (problemCategory: string) => {
		try {
			const response = await fetch(
				`${config.public.customChatApiUrl.replace("/chat", "/vector/search")}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						query: problemCategory,
						limit: 5,
						collection: "mental-health-assessments",
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data.results || [];
		} catch (err) {
			console.error("Assessment Questions Error:", err);
			return [];
		}
	};

	// Get therapeutic suggestions
	const getTherapeuticSuggestions = async (problemCategory: string) => {
		try {
			const response = await fetch(
				`${config.public.customChatApiUrl.replace("/chat", "/vector/search")}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						query: problemCategory,
						limit: 3,
						collection: "mental-health-suggestions",
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data.results || [];
		} catch (err) {
			console.error("Therapeutic Suggestions Error:", err);
			return [];
		}
	};

	// WebSocket instance
	let ws: WebSocket | null = null;

	// Send message via WebSocket with streaming support
	const sendMessage = async (message: string, sessionData?: any) => {
		if (!message.trim() || isProcessing.value) return null;

		initializeSession();
		isProcessing.value = true;
		error.value = null;

		try {
			console.log('🔍 Starting semantic search for message:', message);
			// First, perform semantic search to understand the context
			const searchResults = await searchMentalHealthContext(message);
			console.log('🔍 Semantic search results:', searchResults);

			// Connect to WebSocket if not already connected
			console.log('🔌 Checking WebSocket connection:', {
				exists: !!ws,
				readyState: ws?.readyState,
				isOpen: ws?.readyState === WebSocket.OPEN
			});
			
			if (!ws || ws.readyState !== WebSocket.OPEN) {
				console.log('🔌 Creating new WebSocket connection...');
				ws = connectWebSocket();
				// Wait for connection
				await new Promise((resolve, reject) => {
					const timeout = setTimeout(() => {
						console.error('⏰ WebSocket connection timeout');
						reject(new Error("WebSocket connection timeout"));
					}, 5000);
					ws!.onopen = () => {
						console.log('✅ WebSocket connected successfully');
						clearTimeout(timeout);
						resolve(true);
					};
					ws!.onerror = (error) => {
						console.error('❌ WebSocket connection failed:', error);
						clearTimeout(timeout);
						reject(new Error("WebSocket connection failed"));
					};
				});
			} else {
				console.log('✅ Using existing WebSocket connection');
			}

			// Prepare enhanced message with context
			const enhancedMessage = {
				message: message.trim(),
				session_data: sessionData || {},
				semantic_context: searchResults,
				problem_category: currentProblemCategory.value,
				assessment_progress: assessmentProgress.value,
			};
			console.log('📤 Prepared enhanced message:', enhancedMessage);

			// Send message and wait for complete response
			return new Promise((resolve, reject) => {
				let fullResponse = "";
				let responseData: any = {};

				// Set up message handler
				ws!.onmessage = (event) => {
					try {
						const data = JSON.parse(event.data);

						if (data.type === "chunk") {
							fullResponse += data.content;
						} else if (data.type === "complete") {
							// Convert markdown to HTML
							const htmlContent = convertMarkdownToHtml(fullResponse);

							const result = {
								message: htmlContent,
								sentiment: responseData.sentiment,
								isCrisis: responseData.is_crisis,
								timestamp: new Date(),
								conversationId: conversationId.value,
								problemCategory: responseData.problem_category,
								suggestions: responseData.suggestions,
								assessmentQuestions: responseData.assessment_questions,
								contextAnalysis: responseData.context_analysis,
								assessmentRecommendations: responseData.assessment_recommendations,
								showAssessmentTransition: responseData.context_analysis?.should_suggest_assessment || false,
							};

							// Update detected problem category and assessment suggestion state
							if (responseData.context_analysis) {
								detectedProblemCategory.value = responseData.context_analysis.primary_category || "";
								shouldShowAssessmentSuggestion.value = responseData.context_analysis.should_suggest_assessment || false;
							}

							resolve(result);
						} else if (data.type === "error") {
							reject(new Error(data.message || "WebSocket error occurred"));
						} else {
							// Store additional response data
							responseData = { ...responseData, ...data };
						}
					} catch (err) {
						reject(new Error("Error parsing WebSocket message"));
					}
				};

				ws!.onerror = () => {
					reject(new Error("WebSocket error occurred"));
				};

				// Send the message
				ws!.send(JSON.stringify(enhancedMessage));
			});
		} catch (err) {
			console.error("WebSocket Chat Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		} finally {
			isProcessing.value = false;
		}
	};

	// Send message with streaming response via WebSocket
	const sendMessageStream = async (
		message: string,
		sessionData?: any,
		onChunk?: (chunk: string) => void,
		onComplete?: (fullResponse: any) => void
	) => {
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

			// Connect to WebSocket if not already connected
			if (!ws || ws.readyState !== WebSocket.OPEN) {
				ws = connectWebSocket();
				// Wait for connection
				await new Promise((resolve, reject) => {
					const timeout = setTimeout(() => reject(new Error("WebSocket connection timeout")), 5000);
					ws!.onopen = () => {
						clearTimeout(timeout);
						resolve(true);
					};
					ws!.onerror = () => {
						clearTimeout(timeout);
						reject(new Error("WebSocket connection failed"));
					};
				});
			}

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

			// Set up message handler for streaming
			ws!.onmessage = (event) => {
				console.log('📨 Received WebSocket message:', event.data);
				try {
					const data = JSON.parse(event.data);
					console.log('📋 Parsed message data:', data);

					if (data.type === "chunk") {
						console.log('📦 Processing chunk:', { content: data.content, length: data.content?.length });
						fullResponse += data.content;
						if (typeof onChunk === 'function') {
							console.log('📤 Calling onChunk callback with:', data.content);
							onChunk(data.content);
						} else {
							console.warn('⚠️ onChunk callback not provided or not a function');
						}
					} else if (data.type === "complete") {
						console.log('✅ Processing complete message:', { fullResponseLength: fullResponse.length });
						const htmlContent = convertMarkdownToHtml(fullResponse);

						const result = {
							message: htmlContent,
							sentiment: responseData.sentiment,
							isCrisis: responseData.is_crisis,
							timestamp: new Date(),
							conversationId: conversationId.value,
							problemCategory: responseData.problem_category,
							suggestions: responseData.suggestions,
							assessmentQuestions: responseData.assessment_questions,
							contextAnalysis: responseData.context_analysis,
							assessmentRecommendations: responseData.assessment_recommendations,
						};

						// Update detected problem category and assessment suggestion state
						if (responseData.context_analysis) {
							detectedProblemCategory.value = responseData.context_analysis.primary_category || "";
							shouldShowAssessmentSuggestion.value = responseData.context_analysis.should_suggest_assessment || false;
						}

						if (typeof onComplete === 'function') {
							console.log('📤 Calling onComplete callback with result:', result);
							onComplete(result);
						} else {
							console.warn('⚠️ onComplete callback not provided or not a function');
						}
					} else if (data.type === "error") {
						console.error('❌ Received error message:', data.message);
						error.value = data.message || "WebSocket error occurred";
					} else {
						console.log('📋 Storing additional response data:', data);
						// Store additional response data
						responseData = { ...responseData, ...data };
					}
				} catch (err) {
					console.error("❌ Error parsing WebSocket message:", err, 'Raw data:', event.data);
				}
			};

			ws!.onerror = (error) => {
				console.error('❌ WebSocket error occurred:', error);
				error.value = "WebSocket error occurred";
			};

			// Send the message
			console.log('📤 Sending message to WebSocket:', JSON.stringify(enhancedMessage));
			ws!.send(JSON.stringify(enhancedMessage));
			console.log('📤 Message sent successfully');
		} catch (err) {
			console.error("❌ WebSocket Streaming Error:", err);
			console.error("❌ Error details:", {
				message: err instanceof Error ? err.message : 'Unknown error',
				stack: err instanceof Error ? err.stack : undefined,
				name: err instanceof Error ? err.name : undefined
			});
			error.value = err instanceof Error ? err.message : "An error occurred";
		} finally {
			console.log('🏁 sendMessageStream completed, setting isStreaming to false');
			isStreaming.value = false;
		}
	};

	// Start assessment for a specific problem category
	const startAssessment = async (
		problemCategory: string,
		subCategoryId?: string,
		sessionData?: any
	) => {
		try {
			initializeSession();
			const token =
				localStorage.getItem("auth_token") || config.public.customChatApiKey;

			const response = await fetch(
				`${config.public.customChatApiUrl}/assessment/start`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify({
						problem_category: problemCategory,
						sub_category_id: subCategoryId,
						session_data: sessionData || {},
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			
			if (result.type === "assessment_question") {
				// Update assessment progress with backend data
				assessmentProgress.value = {
					isActive: true,
					currentQuestion: result.question,
					completedQuestions: [],
					totalQuestions: result.progress?.total_estimated || 10,
					currentStep: result.progress?.current_step || 1,
					sessionId: result.session_id || sessionId.value,
					responses: {},
				};
				currentProblemCategory.value = problemCategory;
				
				// Add AI message with the question
				const aiMessage = {
				id: generateSessionId(),
				text: result.message,
				sender: "ai" as const,
				timestamp: new Date(),
				assessmentQuestion: result.question,
				assessmentProgress: result.progress,
			};
				messages.value.push(aiMessage);
			}

			return result;
		} catch (err) {
			console.error("Assessment API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// Continue assessment with next question
	const continueAssessment = async (answer: string, questionId?: string) => {
		try {
			if (!assessmentProgress.value.isActive) {
				throw new Error("No active assessment");
			}

			const currentQuestion = assessmentProgress.value.currentQuestion;
			if (!currentQuestion) {
				throw new Error("No current question found");
			}

			const token =
				localStorage.getItem("auth_token") || config.public.customChatApiKey;

			const response = await fetch(
				`${config.public.customChatApiUrl}/assessment/respond`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify({
						response: answer,
						question_id: questionId || currentQuestion.question_id,
					}),
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			
			// Store the user's response
			assessmentProgress.value.responses[currentQuestion.question_id] = {
				question: currentQuestion,
				answer: answer,
				timestamp: new Date().toISOString(),
			};
			
			// Add user message
			const userMessage = {
				id: generateSessionId(),
				text: answer,
				sender: "user" as const,
				timestamp: new Date(),
			};
			messages.value.push(userMessage);

			if (result.type === "assessment_question") {
				// Continue with next question
				assessmentProgress.value.currentQuestion = result.question;
				assessmentProgress.value.currentStep = result.progress?.current_step || assessmentProgress.value.currentStep + 1;
				assessmentProgress.value.completedQuestions.push(currentQuestion);
				
				// Add AI message with next question
				const aiMessage = {
				id: generateSessionId(),
				text: result.message,
				sender: "ai" as const,
				timestamp: new Date(),
				assessmentQuestion: result.question,
				assessmentProgress: result.progress,
			};
				messages.value.push(aiMessage);
				
			} else if (result.type === "assessment_complete") {
				// Assessment completed
				assessmentProgress.value.isActive = false;
				assessmentProgress.value.currentQuestion = null;
				assessmentProgress.value.completedQuestions.push(currentQuestion);
				
				// Add completion message
				const completionMessage = {
				id: generateSessionId(),
				text: result.message,
				sender: "ai" as const,
				timestamp: new Date(),
				assessmentComplete: true,
				assessmentSummary: result.summary,
				recommendations: result.recommendations,
			};
				messages.value.push(completionMessage);
			}

			return result;
		} catch (err) {
			console.error("Continue Assessment Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// WebSocket connection for real-time chat
	const connectWebSocket = () => {
		const wsUrl = config.public.customChatWsUrl;
		console.log('🔌 Connecting to WebSocket:', {
			url: wsUrl,
			configExists: !!config.public,
			customChatWsUrl: config.public.customChatWsUrl
		});
		
		const newWs = new WebSocket(wsUrl);
		console.log('🔌 WebSocket instance created:', {
			readyState: newWs.readyState,
			url: newWs.url
		});

		newWs.onopen = () => {
			isConnected.value = true;
			console.log("✅ WebSocket connected to streaming endpoint:", wsUrl);
			console.log('✅ Connection details:', {
				readyState: newWs.readyState,
				protocol: newWs.protocol,
				extensions: newWs.extensions
			});
		};

		newWs.onclose = (event) => {
			isConnected.value = false;
			console.log("🔌 WebSocket disconnected:", {
				code: event.code,
				reason: event.reason,
				wasClean: event.wasClean
			});
		};

		newWs.onerror = (error) => {
			console.error("❌ WebSocket error:", error);
			console.error("❌ WebSocket error details:", {
				readyState: newWs.readyState,
				url: newWs.url,
				error: error
			});
			isConnected.value = false;
		};

		return newWs;
	};

	// Disconnect WebSocket
	const disconnectWebSocket = () => {
		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.close();
		}
		ws = null;
		isConnected.value = false;
	};

	// Legacy WebSocket send function (kept for backward compatibility)
	const sendMessageWebSocket = (
		wsInstance: WebSocket,
		message: string,
		sessionData?: any,
		onChunk?: (chunk: string) => void,
		onComplete?: (fullResponse: any) => void
	) => {
		if (wsInstance.readyState === WebSocket.OPEN) {
			// Send the message
			wsInstance.send(
				JSON.stringify({
					message,
					session_data: sessionData || {},
					semantic_context: [],
					problem_category: currentProblemCategory.value,
					assessment_progress: assessmentProgress.value,
				})
			);

			// Set up message handler for streaming responses
			wsInstance.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);

					if (data.type === "chunk") {
						onChunk?.(data.content);
					} else if (data.type === "complete") {
						onComplete?.({ message: "Stream completed" });
					} else if (data.type === "error") {
						error.value = data.message || "WebSocket error occurred";
					}
				} catch (err) {
					console.error("Error parsing WebSocket message:", err);
				}
			};
		}
	};

	// Get conversation history
	const getConversationHistory = async () => {
		try {
			const token = localStorage.getItem("auth_token");

			if (!token) {
				throw new Error("Authentication required");
			}

			const response = await fetch(
				`${config.public.customChatApiUrl}/conversation/history`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${token}`,
					},
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		} catch (err) {
			console.error("History API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// Clear conversation history
	const clearConversationHistory = async () => {
		try {
			const token = localStorage.getItem("auth_token");

			if (!token) {
				throw new Error("Authentication required");
			}

			const response = await fetch(
				`${config.public.customChatApiUrl}/conversation/clear`,
				{
					method: "DELETE",
					headers: {
						Authorization: `Bearer ${token}`,
					},
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		} catch (err) {
			console.error("Clear History API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// Check model status
	const checkModelStatus = async () => {
		try {
			const response = await fetch(
				`${config.public.customChatApiUrl}/model/status`
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		} catch (err) {
			console.error("Model Status API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// Pull model
	const pullModel = async () => {
		try {
			const response = await fetch(
				`${config.public.customChatApiUrl}/model/pull`,
				{
					method: "POST",
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		} catch (err) {
			console.error("Pull Model API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// Add message to local state
	const addMessage = (message: {
		id?: string;
		text: string;
		sender: "user" | "ai";
		sentiment?: any;
		isCrisis?: boolean;
		problemCategory?: string;
		suggestions?: any[];
		assessmentQuestions?: any[];
		timestamp?: Date;
		isStreaming?: boolean;
		detectedEmotion?: any;
		emotionTone?: any;
	}) => {
		messages.value.push({
			id: message.id || Date.now().toString(),
			text: message.text,
			sender: message.sender,
			timestamp: message.timestamp || new Date(),
			sentiment: message.sentiment,
			isCrisis: message.isCrisis,
			problemCategory: message.problemCategory,
			suggestions: message.suggestions,
			assessmentQuestions: message.assessmentQuestions,
			isStreaming: message.isStreaming,
			detectedEmotion: message.detectedEmotion,
			emotionTone: message.emotionTone,
		});
	};

	// Clear messages
	const clearMessages = () => {
		messages.value = [];
		assessmentProgress.value = {
			isActive: false,
			currentQuestion: null,
			completedQuestions: [],
			totalQuestions: 0,
		};
		currentProblemCategory.value = "";
	};

	// Computed properties
	const hasMessages = computed(() => messages.value.length > 0);
	const lastMessage = computed(() => messages.value[messages.value.length - 1]);
	const isAssessmentActive = computed(() => assessmentProgress.value.isActive);
	const assessmentProgressPercentage = computed(() => {
		if (!assessmentProgress.value.isActive) return 0;
		return (
			(assessmentProgress.value.completedQuestions.length /
				assessmentProgress.value.totalQuestions) *
			100
		);
	});

	// Get assessment status
	const getAssessmentStatus = async () => {
		try {
			const token =
				localStorage.getItem("auth_token") || config.public.customChatApiKey;

			const response = await fetch(
				`${config.public.customChatApiUrl}/assessment/status`,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			
			if (result.active) {
				// Sync local state with backend
				assessmentProgress.value = {
					isActive: true,
					currentQuestion: result.current_question,
					completedQuestions: [],
					totalQuestions: result.progress?.total_estimated || 10,
					currentStep: result.progress?.current_step || 1,
					sessionId: sessionId.value,
					responses: {},
				};
				currentProblemCategory.value = result.problem_category || "";
			} else {
				assessmentProgress.value.isActive = false;
			}

			return result;
		} catch (err) {
			console.error("Get Assessment Status Error:", err);
			return { active: false };
		}
	};

	// Cancel assessment
	const cancelAssessment = async () => {
		try {
			const token =
				localStorage.getItem("auth_token") || config.public.customChatApiKey;

			const response = await fetch(
				`${config.public.customChatApiUrl}/assessment/cancel`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			
			// Reset local assessment state
			assessmentProgress.value = {
				isActive: false,
				currentQuestion: null,
				completedQuestions: [],
				totalQuestions: 0,
				currentStep: 1,
				sessionId: "",
				responses: {},
			};
			currentProblemCategory.value = "";

			return result;
		} catch (err) {
			console.error("Cancel Assessment Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return { success: false, message: "Failed to cancel assessment" };
		}
	};

// Accept assessment suggestion and start assessment
	const acceptAssessmentSuggestion = async () => {
		if (detectedProblemCategory.value) {
			const result = await startAssessment(detectedProblemCategory.value);
			shouldShowAssessmentSuggestion.value = false;
			return result;
		}
		return null;
	};

	// Decline assessment suggestion
	const declineAssessmentSuggestion = () => {
		shouldShowAssessmentSuggestion.value = false;
		detectedProblemCategory.value = "";
	};

	return {
		// State
		isProcessing,
		isStreaming,
		error,
		isConnected,
		messages,
		sessionId,
		conversationId,
		currentProblemCategory,
		detectedProblemCategory,
		shouldShowAssessmentSuggestion,
		assessmentProgress,

		// Computed
		hasMessages,
		lastMessage,
		isAssessmentActive,
		assessmentProgressPercentage,

		// Methods
		sendMessage,
		sendMessageStream,
		connectWebSocket,
		disconnectWebSocket,
		sendMessageWebSocket,
		startAssessment,
		continueAssessment,
		getAssessmentStatus,
		cancelAssessment,
		getConversationHistory,
		clearConversationHistory,
		checkModelStatus,
		pullModel,
		addMessage,
		acceptAssessmentSuggestion,
		declineAssessmentSuggestion,
		clearMessages,
		convertMarkdownToHtml,
		initializeSession,
		searchMentalHealthContext,
		getProblemCategories,
		getAssessmentQuestions,
		getTherapeuticSuggestions,
	};
};
