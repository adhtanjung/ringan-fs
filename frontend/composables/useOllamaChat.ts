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
		onComplete?: (fullResponse: any) => void,
		onNewMessage?: (messageData: any) => void
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
						console.log('📦 Processing chunk:', { content: data.content, length: data.content?.length, isAssessmentSuggestion: data.is_assessment_suggestion });
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
							contextAnalysis: data.context_analysis || responseData.context_analysis,
							assessmentRecommendations: data.assessment_recommendations || responseData.assessment_recommendations,
							assessmentData: data.assessment_data,
							stage: data.stage,
							progress: data.progress,
							responseType: data.type,
							showAssessmentTransition: responseData.is_assessment_suggestion || false,
							suggestedCategory: responseData.suggested_category,
							subCategoryId: responseData.sub_category_id
						};

						// Update detected problem category and assessment suggestion state
						if (data.context_analysis || responseData.context_analysis) {
							const contextAnalysis = data.context_analysis || responseData.context_analysis;
							detectedProblemCategory.value = contextAnalysis.primary_category || "";
							shouldShowAssessmentSuggestion.value = contextAnalysis.should_suggest_assessment || false;
						}

						// Update assessment progress if assessment data is present
					if (data.assessment_data && data.assessment_data.type === "assessment_question") {
						const progressData = data.assessment_data.progress || {};
						const completedCount = progressData.completed_questions || 0;
						const currentStep = progressData.current_step || 1;
						const totalQuestions = progressData.total_estimated || 10;
						
						// Create array of completed question IDs based on completed count
						const completedQuestions = [];
						for (let i = 0; i < completedCount; i++) {
							completedQuestions.push(`completed_${i}`);
						}
						
						assessmentProgress.value = {
							isActive: true,
							currentQuestion: data.assessment_data.question,
							completedQuestions: completedQuestions,
							totalQuestions: totalQuestions,
							currentStep: currentStep,
							sessionId: data.assessment_data.session_id || sessionId.value,
							responses: assessmentProgress.value.responses || {},
						};
						
						console.log('📊 Updated assessment progress:', {
							completedCount,
							currentStep,
							totalQuestions,
							progressPercentage: Math.round((completedCount / totalQuestions) * 100)
						});
						
						// For assessment questions, create a new result with the complete message content
						// Use data.content directly for assessment questions to ensure full content
						const assessmentMessageContent = data.content || messageContent;
						const assessmentHtmlContent = convertMarkdownToHtml(assessmentMessageContent);
						
						const assessmentResult = {
							...result,
							message: assessmentHtmlContent,
							assessmentData: data.assessment_data,
							stage: data.stage,
							progress: data.progress
						};
						
						if (typeof onNewMessage === 'function') {
							console.log('📤 Creating new message for assessment question:', {
								messageLength: assessmentMessageContent.length,
								htmlLength: assessmentHtmlContent.length,
								assessmentData: data.assessment_data,
								result: assessmentResult
							});
							onNewMessage(assessmentResult);
							return; // Don't call onComplete for assessment questions
						}
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
				} else if (data.type === "problem_identified" || data.type === "assessment_question" || data.type === "suggestion_provided" || data.type === "clarification_needed") {
					console.log('📋 Processing structured response:', data.type);
					// For structured responses, treat the message as complete
					const htmlContent = convertMarkdownToHtml(data.message || "");

					const result = {
						message: htmlContent,
						sentiment: data.sentiment,
						isCrisis: data.is_crisis,
						timestamp: new Date(),
						conversationId: conversationId.value,
						problemCategory: data.problem_category,
						suggestions: data.suggestions,
						assessmentQuestions: data.assessment_questions,
						contextAnalysis: data.context_analysis,
						assessmentRecommendations: data.assessment_recommendations,
						responseType: data.type,
						stage: data.stage,
						identifiedProblems: data.identified_problems,
						nextStageAvailable: data.next_stage_available,
						transitionPrompt: data.transition_prompt
					};

					// Update detected problem category and assessment suggestion state
					if (data.context_analysis) {
						detectedProblemCategory.value = data.context_analysis.primary_category || "";
						shouldShowAssessmentSuggestion.value = data.context_analysis.should_suggest_assessment || false;
					}

					if (typeof onComplete === 'function') {
						console.log('📤 Calling onComplete callback with structured result:', result);
						onComplete(result);
					} else {
						console.warn('⚠️ onComplete callback not provided or not a function');
					}
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

			// Handle empty or invalid problem categories
			let validProblemCategory = problemCategory;
			if (!problemCategory || problemCategory.trim() === "" || problemCategory.toLowerCase() === "nan") {
				console.warn(`Invalid problem category: '${problemCategory}'. Using default 'general mental health'.`);
				validProblemCategory = "general mental health";
			}

			const response = await fetch(
				`${config.public.customChatApiUrl}/assessment/start`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify({
						problem_category: validProblemCategory,
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
				const progressData = result.progress || {};
				const completedCount = progressData.completed_questions || 0;
				const currentStep = progressData.current_step || 1;
				const totalQuestions = progressData.total_estimated || 10;
				
				// Create array of completed question IDs based on completed count
				const completedQuestions = [];
				for (let i = 0; i < completedCount; i++) {
					completedQuestions.push(`completed_${i}`);
				}
				
				assessmentProgress.value = {
					isActive: true,
					currentQuestion: result.question,
					completedQuestions: completedQuestions,
					totalQuestions: totalQuestions,
					currentStep: currentStep,
					sessionId: result.session_id || sessionId.value,
					responses: {},
				};
				
				console.log('📊 Started assessment with progress:', {
					completedCount,
					currentStep,
					totalQuestions,
					progressPercentage: Math.round((completedCount / totalQuestions) * 100)
				});
				currentProblemCategory.value = validProblemCategory;
				
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

			// Store the user's response
			assessmentProgress.value.responses[currentQuestion.question_id] = {
				question: currentQuestion,
				answer: answer,
				timestamp: new Date().toISOString(),
			};

			// Send assessment response through WebSocket
			const assessmentResponseMessage = {
				type: "assessment_response",
				response: answer,
				question_id: questionId || currentQuestion.question_id,
				session_id: assessmentProgress.value.sessionId,
				timestamp: new Date().toISOString()
			};

			console.log('📤 Sending assessment response via WebSocket:', assessmentResponseMessage);
			
			// Send through WebSocket if connected
			if (ws && ws.readyState === WebSocket.OPEN) {
				ws.send(JSON.stringify(assessmentResponseMessage));
			} else {
				console.warn('⚠️ WebSocket not connected, attempting to reconnect...');
				ws = connectWebSocket();
				// Wait a moment for connection then send
				setTimeout(() => {
					if (ws && ws.readyState === WebSocket.OPEN) {
						ws.send(JSON.stringify(assessmentResponseMessage));
					}
				}, 1000);
			}

			return { success: true };
		} catch (err) {
			console.error("Continue Assessment Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		}
	};

	// WebSocket connection for real-time chat
	const connectWebSocket = () => {
		// Ensure we have a session ID
		initializeSession();
		
		// Append session ID to WebSocket URL
		const baseWsUrl = config.public.customChatWsUrl;
		const wsUrl = `${baseWsUrl}/${sessionId.value}`;
		console.log('🔌 Connecting to WebSocket:', {
			baseUrl: baseWsUrl,
			fullUrl: wsUrl,
			sessionId: sessionId.value,
			configExists: !!config.public,
			customChatWsUrl: config.public.customChatWsUrl,
			envVar: process.env.NUXT_PUBLIC_CUSTOM_CHAT_WS_URL
		});
		
		// Additional debug logging
		console.log('🔍 Debug WebSocket URL construction:', {
			'config.public': config.public,
			'typeof baseWsUrl': typeof baseWsUrl,
			'baseWsUrl length': baseWsUrl?.length,
			'sessionId': sessionId.value,
			'final wsUrl': wsUrl
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
				const progressData = result.progress || {};
				const completedCount = progressData.completed_questions || 0;
				const currentStep = progressData.current_step || 1;
				const totalQuestions = progressData.total_estimated || 10;
				
				// Create array of completed question IDs based on completed count
				const completedQuestions = [];
				for (let i = 0; i < completedCount; i++) {
					completedQuestions.push(`completed_${i}`);
				}
				
				assessmentProgress.value = {
					isActive: true,
					currentQuestion: result.current_question,
					completedQuestions: completedQuestions,
					totalQuestions: totalQuestions,
					currentStep: currentStep,
					sessionId: sessionId.value,
					responses: {},
				};
				
				console.log('📊 Synced assessment status with progress:', {
					completedCount,
					currentStep,
					totalQuestions,
					progressPercentage: Math.round((completedCount / totalQuestions) * 100)
				});
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
